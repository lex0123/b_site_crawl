import json
import requests
from bs4 import BeautifulSoup
import re
import os
# bvname="BV1M64y1E7o1"
# cookie=os.getenv("b_cookie")
# deepseek_api_key = os.getenv("deepseek-api-key")
def get_video_subtitle(deepseek_api_key,bvname,cookie):
    refer=f"https://www.bilibili.com/{bvname}"
    url = f"https://www.bilibili.com/video/{bvname}"
    headers = {
    "Cookie": cookie,
    "Origin": "https://www.bilibili.com",
    "Referer": refer,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
}
    # 发送HTTP请求
    response = requests.get(url, headers=headers)
    html = response.text
    title = re.findall('title="(.*?)"', html)[0]
    print(f"处理视频: {title}")
    os.makedirs(title, exist_ok=True)
    subtitle_path=title+"\\"+"subtitle.txt"
    aid_match = re.findall(r'.*,"aid":(\d+),', response.text)[0]
    cids_match = re.findall(f'.*"{url.split("/")[4]}","cid":(\\d+),', response.text)[0]
    # print(aid_match)
    # print(cids_match)

    htur=f"https://api.bilibili.com/x/player/wbi/v2?aid={aid_match}&cid={cids_match}"

    response2 = requests.get(htur, headers=headers)
    pattern = r'"subtitle_url":"(.*?)","subtitle_url_v2"'
    
    # 使用re.search()查找匹配的内容
    match = re.search(pattern, response2.text)
    
    # 如果找到匹配项，则提取第一个括号内的内容
    if match:
        subtitle_url = match.group(1)
    else:
        print("No match found")
    uul=f"https:{subtitle_url}"
    responses1=requests.get(uul,headers=headers)
    data = json.loads(responses1.text)
    contents = [item['content'] for item in data['body']]
    with open(subtitle_path, "w", encoding="utf-8") as f:
        for content in contents:
            f.write(content + "\n")
    print(contents)
    print(f"字幕已保存至: {subtitle_path}")
        
        # 组合成完整文本，用于发送给DeepSeek
    full_text = "\n".join(contents)
    
    if not deepseek_api_key:
        print("警告: 未找到DeepSeek API密钥，跳过总结步骤")
    else:
        print("正在使用DeepSeek AI总结内容...")
        
        headers = {
            "Authorization": f"Bearer {deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        # DeepSeek API请求
        deepseek_url = "https://api.deepseek.com/v1/chat/completions"
        response = requests.post(
            deepseek_url,
            headers=headers,
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一个专业的内容分析师，并且有着充分的金融市场的专业背景知识，请对以下视频字幕内容进行分析和总结。"},
                    {"role": "user", "content": f"请对以下B站视频的字幕内容进行概括总结，提炼关键观点和见解，以及整体结构：\n\n{full_text}"}
                ],
                "max_tokens": 1000
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            summary = result["choices"][0]["message"]["content"]
            
            # 保存总结到文件
            summary_path = os.path.join(title, "summary.txt")
            with open(summary_path, "w", encoding="utf-8") as f:
                f.write(summary)
            print(f"内容总结已保存至: {summary_path}")
            print("\n摘要预览:")
            print(summary[:500] + "..." if len(summary) > 500 else summary)
        else:
            print(f"DeepSeek API请求失败: {response.status_code}")
            print(response.text)
