import json
import requests
from bs4 import BeautifulSoup
import re
from tencentcloud_get_voice import title
# 目标网址
import os
os.makedirs(title+"\\"+"subtitle", exist_ok=True)
bvname="BV16eJBzGEAY"
refer=f"https://www.bilibili.com/{bvname}"
subtitle_path=title+"\\"+"subtitle.txt"
cookie="buvid3=430277AB-F19D-E42F-B985-4E96B159881A84478infoc; b_nut=1746872884; _uuid=7A7D6A4B-1153-B29C-B944-F5B10F9421B9186258infoc; buvid4=B472E5D9-E55D-DE4D-8AFB-200A83FCA05486323-025051018-BE5tNRPq5Hm1axKT15iGDQ%3D%3D; rpdid=|(JJmY)YRu~~0J'u~RY)~k))m; DedeUserID=3546715265173614; DedeUserID__ckMd5=7b4e3ead3db48297; header_theme_version=CLOSE; enable_web_push=DISABLE; enable_feed_channel=ENABLE; fingerprint=ab96a73572632a9e1ebdd467149da5e1; buvid_fp_plain=undefined; buvid_fp=ab96a73572632a9e1ebdd467149da5e1; SESSDATA=cac768bb%2C1763282713%2C5e39d%2A51CjAZ7LI-EqGaLiW_TA1-VzQCfbh_KI35h0sCA2Uutj0OqrgFRPUgAhAt83HNs2auA0QSVk1Ub3lBdEh3bGttdkc1alBxNmJ1RFJBell6bkNxdkNPNkVEb3I5c0NkVVFhdHgtay0ybmtKMFhhYTF6Y2ZiV3E1OWpZLWVxNTY5ZjdxVFREVFlvNDZRIIEC; bili_jct=e832e3adb91f3531b0224708681bdc39; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDc5OTMzMTYsImlhdCI6MTc0NzczNDA1NiwicGx0IjotMX0.I35lF4Hth0G9xTEZtDdF9KfRcfihw6_lenhcGCLh5Q8; bili_ticket_expires=1747993256; CURRENT_QUALITY=120; bmg_af_switch=1; bmg_src_def_domain=i0.hdslb.com; sid=84ex66a0; b_lsid=8AE5C101C_196F24065CF; bp_t_offset_3546715265173614=1069373739180752896; home_feed_column=5; browser_resolution=1432-774; CURRENT_FNVAL=4048"
headers = {
    "Cookie": cookie,
    "Origin": "https://www.bilibili.com",
    "Referer": refer,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
}

 
url = f"https://www.bilibili.com/video/{bvname}/?spm_id_from=333.1007.tianma.1-2-2.click&vd_source=efbc10526f5fa5642530923cf09ce506&p=0"

# 发送HTTP请求
response = requests.get(url, headers=headers)
 
aid_match = re.findall(r'.*,"aid":(\d+),', response.text)[0]
cids_match = re.findall(f'.*"{url.split("/")[4]}","cid":(\\d+),', response.text)[0]
# print(aid_match)
# print(cids_match)

htur=f"https://api.bilibili.com/x/player/wbi/v2?aid={aid_match}&cid={cids_match}"

response2 = requests.get(htur, headers=headers)
print(response2.text)
pattern = r'"subtitle_url":"(.*?)","subtitle_url_v2"'
 
# 使用re.search()查找匹配的内容
match = re.search(pattern, response2.text)
 
# 如果找到匹配项，则提取第一个括号内的内容
if match:
    subtitle_url = match.group(1)
    print(subtitle_url)
else:
    print("No match found")
 
 
uul=f"https:{subtitle_url}"
responses1=requests.get(uul,headers=headers)
data = json.loads(responses1.text)
 
# 提取content内容
print("\n\n\n\n")

contents = [item['content'] for item in data['body']]
with open(subtitle_path, "w", encoding="utf-8") as f:
    for content in contents:
        f.write(content + "\n")
print(contents)
print(f"字幕已保存至: {subtitle_path}")
    
    # 组合成完整文本，用于发送给DeepSeek
full_text = "\n".join(contents)
# 调用DeepSeek API进行总结
deepseek_api_key = os.getenv("xiaomi")
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
