# 导入数据请求模块
import os
import requests
# 导入正则表达式模块
import re
# 导入json模块
import json
import base64
import subprocess
from  tencentcloud.asr.v20190614 import asr_client, models
from tencentcloud.common import credential
from moviepy import AudioFileClip
url ="buvid3=FB472403-4318-2DB6-3EA2-795CD15D327C68444infoc; b_nut=1739875368; _uuid=BEC3EDE5-5157-9B7F-E5AA-BA4C8741041B1069686infoc; enable_web_push=DISABLE; buvid4=4AF1702D-54E3-BF5D-57FE-E6206805318C69553-025021810-pZEji5QGhfyiXMpuB5gnPQ%3D%3D; DedeUserID=3546715265173614; DedeUserID__ckMd5=7b4e3ead3db48297; rpdid=|(JJmY)YR|Yk0J'u~R|uRu~kR; LIVE_BUVID=AUTO4917403122766556; header_theme_version=CLOSE; enable_feed_channel=ENABLE; hit-dyn-v2=1; fingerprint=7bd4acc6278e975b775d8d3f4fb5768b; buvid_fp_plain=undefined; buvid_fp=7bd4acc6278e975b775d8d3f4fb5768b; home_feed_column=4; browser_resolution=1133-627; PVID=1; CURRENT_QUALITY=80; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDc5MTMwMDUsImlhdCI6MTc0NzY1Mzc0NSwicGx0IjotMX0.EHVcfS44cgatQgdpHkyftuFEKa1uu1R-jzk3DPKIcIs; bili_ticket_expires=1747912945; SESSDATA=80af750f%2C1763223409%2C26bb6%2A51CjB1Elfkn-JGZ8AfIu9zcdKOW3IIaq-HpZK3sfWt6eD7ys3kolOBt7LovrKACB3V5qcSVnBCMHUzaXM3N1BDdl9JVTJReXdTekRhYXB0cTJDci1Ya3N5TFNjblkzdkNMNl9zNGNqV0NHd2gxaG9nb0V0ZDgtNWlxQVFjY0FXQTA5emxUaXpRbWZnIIEC; bili_jct=03bd19462d59e91fa31ea84fb0d76524; sid=6dvq210x; bp_t_offset_3546715265173614=1068729747489423360; b_lsid=B10CE688E_196F05B4A28; CURRENT_FNVAL=2000"
cookie = ""
headers = {
    "Cookie": cookie,
    "Referer": url,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}
def chunk_download(file_url, filename):
    try:
        with requests.get(file_url, headers=headers, stream=True, timeout=10) as r:
            r.raise_for_status()
            with open(filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
        print(f"下载完成：{filename}")
    except Exception as e:
        print(f"下载失败：{filename}，原因：{e}")
def download_video(url, cookie):
   
    response = requests.get(url=url, headers=headers)
    html = response.text
    title = re.findall('title="(.*?)"', html)[0]
    print(title)
    # 提取视频信息
    info = re.findall('window.__playinfo__=(.*?)</script>', html)[0]
    json_data = json.loads(info)
    # 提取视频链接
    video_url = json_data['data']['dash']['video'][0]['baseUrl']
    audio_url = json_data['data']['dash']['audio'][0]['baseUrl']

    os.makedirs(title, exist_ok=True)



    chunk_download(video_url, f"{title}/{title}.mp4")
    chunk_download(audio_url, f"{title}/{title}.mp3")
    chunk_download(audio_url, f"{title}/{title}.wav")
    video_path = f"{title}/{title}.mp4"
    audio_path = f"{title}/{title}.mp3"
    output_path = f"{title}/{title}_merged.mp4"
    try:
        cmd = [
            "ffmpeg", 
            "-i", video_path, 
            "-i", audio_path, 
            "-c:v", "copy", 
            "-c:a", "aac", 
            "-strict", "experimental",
            output_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode == 0:
            print(f"合成完成：{output_path}")
            os.remove(video_path)
        else:
            print(f"合成失败，FFmpeg返回码: {result.returncode}")
            print(f"错误信息: {result.stderr.decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"合成失败：{e}")
        
    return title

download_video(url, cookie)