# 导入数据请求模块
import os
import requests
# 导入正则表达式模块
import re
# 导入json模块
import json
import base64
from tencentcloud.asr.v20190614 import asr_client, models
from tencentcloud.common import credential
from moviepy import AudioFileClip
title=""
url ="https://www.bilibili.com/video/BV1qt411j7fV/"
cookie = ""
def download_video(url, cookie):
    headers = {
            "Referer": url,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }
    response = requests.get(url=url, headers=headers)
    html = response.text
    title = re.findall('title="(.*?)"', html)[0]
    print(title)
    # # 提取视频信息
    info = re.findall('window.__playinfo__=(.*?)</script>', html)[0]
    # print(info)
    # info -> json字符串转成json字典
    json_data = json.loads(info)
    # # 提取视频链接
    video_url = json_data['data']['dash']['video'][0]['baseUrl']
    audio_url = json_data['data']['dash']['audio'][0]['baseUrl']
    video_content = requests.get(url=video_url, headers=headers).content
    audio_content = requests.get(url=audio_url, headers=headers).content
    # 保存数据
    os.makedirs(title,exist_ok=True)
    with open(title+'/'+title + '.mp4', mode='wb') as v:
        v.write(video_content)
    with open( title+'/'+title + '.mp3', mode='wb') as a:
        a.write(audio_content)
    with open( title+'/'+title +'.wav', mode='wb') as a:
        a.write(audio_content)
    return title
download_video(url, cookie)