import cv2
import os
import base64
import requests
import json
from pathlib import Path
from moviepy import VideoFileClip

# 配置信息
API_KEY = "sk-592vE7E0F2h1f0I5D2X1H7e0C0C8I5B1B2A1C0D2F4I5lIJxps"
BASE_URL = "https://api.linkapi.ai/v1"
MODEL_ID = "custom/gemini-3-flash-preview"

def extract_frames(video_path, output_dir, fps=1.0):
    """
    提取帧并记录时间戳
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    vidcap = cv2.VideoCapture(video_path)
    video_fps = vidcap.get(cv2.CAP_PROP_FPS)
    hop = int(video_fps / fps) if video_fps > fps else 1
    
    count = 0
    frame_count = 0
    success, image = vidcap.read()
    frame_data = []
    
    while success:
        if count % hop == 0:
            timestamp = count / video_fps
            frame_path = os.path.join(output_dir, f"frame_{frame_count:04d}.jpg")
            cv2.imwrite(frame_path, image)
            frame_data.append({"path": frame_path, "timestamp": timestamp})
            frame_count += 1
        success, image = vidcap.read()
        count += 1
    
    vidcap.release()
    print(f"提取了 {len(frame_data)} 帧")
    return frame_data

def extract_audio(video_path, audio_output_path):
    print("正在提取音频...")
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_output_path, logger=None)
    video.close()
    return audio_output_path

def transcribe_audio_with_timestamps(audio_path):
    """
    调用 Whisper 并请求时间戳信息 (verbose_json)
    """
    print("正在尝试获取带时间戳的转录内容...")
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    # 注意：某些中转站可能不支持 response_format="verbose_json"
    data = {
        "model": "whisper-1",
        "response_format": "verbose_json"
    }
    
    try:
        with open(audio_path, "rb") as f:
            files = {"file": (os.path.basename(audio_path), f)}
            response = requests.post(f"{BASE_URL}/audio/transcriptions", headers=headers, files=files, data=data, timeout=60)
        
        if response.status_code == 200:
            res_json = response.json()
            segments = res_json.get("segments", [])
            formatted_text = ""
            for s in segments:
                formatted_text += f"[{s['start']:.2f}s - {s['end']:.2f}s] {s['text']}\n"
            return formatted_text if formatted_text else res_json.get("text", "[无时间戳文本]")
        else:
            print(f"Whisper 报错: {response.text}")
            return "[音频转录失败]"
    except Exception as e:
        print(f"网络异常: {e}")
        return "[音频处理异常]"

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_v3(video_path, user_prompt):
    temp_dir = "temp_v3"
    if not os.path.exists(temp_dir): os.makedirs(temp_dir)
        
    # 1. 提取帧（降低到每秒1帧，节省上下文）
    frames_data = extract_frames(video_path, temp_dir, fps=1.0)
    
    # 2. 提取并转录音频
    audio_path = os.path.join(temp_dir, "temp_audio.mp3")
    extract_audio(video_path, audio_path)
    audio_with_ts = transcribe_audio_with_timestamps(audio_path)
    
    # 3. 构建多模态消息
    # 我们告诉模型：图片序列中的每一张图对应的时间点
    prompt = f"""
{user_prompt}

以下是视频的音频转录（带时间戳）:
---
{audio_with_ts}
---

上传的图片序列对应的时间点如下：
"""
    for i, fd in enumerate(frames_data):
        prompt += f"图片 {i}: {fd['timestamp']:.2f}s\n"

    content = [{"type": "text", "text": prompt}]
    
    # 只取前 50 帧，防止上下文爆炸（Gemini 3 Flash 建议限制）
    step = max(1, len(frames_data) // 50)
    selected_frames = frames_data[::step]

    for fd in selected_frames:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{encode_image(fd['path'])}"}
        })

    print(f"正在发送 {len(selected_frames)} 张图片进行最终分析...")
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    payload = {"model": MODEL_ID, "messages": [{"role": "user", "content": content}], "max_tokens": 2048}

    response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
    
    # 清理
    for fd in frames_data: os.remove(fd['path'])
    if os.path.exists(audio_path): os.remove(audio_path)
    if os.path.exists(temp_dir): os.rmdir(temp_dir)
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"分析失败: {response.text}"

if __name__ == "__main__":
    v_file = "current_video.mp4" # 使用你刚发的视频
    if os.path.exists(v_file):
        print(analyze_v3(v_file, "请结合时间戳，详细分析视频中人物的对话内容与画面的对应关系，并评价其表达的情感。"))
