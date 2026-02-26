import requests
import json

def find_bank():
    key = "3cc2c28498d55a83f16667a4681b8340"
    location = "113.350116,22.948431"
    url = "https://restapi.amap.com/v3/place/around"
    
    params = {
        "key": key,
        "location": location,
        "keywords": "中国银行",
        "types": "银行",
        "radius": 10000,
        "sortrule": "distance",
        "output": "json"
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["status"] == "1" and int(data["count"]) > 0:
            pois = data["pois"]
            print(f"找到 {data['count']} 个结果。最近的如下：\n")
            for i, poi in enumerate(pois[:3]):
                print(f"{i+1}. {poi['name']}")
                print(f"   距离: {poi['distance']} 米")
                print(f"   地址: {poi['address']}")
                print("-" * 20)
        else:
            print(f"未找到结果或错误: {data.get('info', '未知错误')}")
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    find_bank()
