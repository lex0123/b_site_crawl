import json
import requests
from bs4 import BeautifulSoup
import re
 
# 目标网址
bvname="BV16G4y1S7Hp"
refer=f"https://www.bilibili.com/{bvname}"
headers = {
 
    "Cookie": " ",
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
print(responses1.text)
data = json.loads(responses1.text)
 
# 提取content内容
print("\n\n\n\n")
contents = [item['content'] for item in data['body']]
print(contents)