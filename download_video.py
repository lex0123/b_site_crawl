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
from concurrent.futures import ThreadPoolExecutor, as_completed
title=""
cookie = os.getenv("b_cookie")
url =[
    "https://www.bilibili.com/video/BV1yQJ8zZEiY/?spm_id_from=333.337.search-card.all.click",
    ]
headers = {
    "Cookie": cookie,
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
def download_single_audio(url,headers):
    headers["Referer"] = url
    try:
        response = requests.get(url=url, headers=headers)
        html = response.text
        title = re.findall('title="(.*?)"', html)[0]
        print(f"处理视频: {title}")
        
        # 提取视频信息
        info = re.findall('window.__playinfo__=(.*?)</script>', html)[0]
        # 提取视频链接
        json_data = json.loads(info)
        video_url = json_data['data']['dash']['video'][0]['baseUrl']
        audio_url = json_data['data']['dash']['audio'][0]['baseUrl']
        chunk_download(audio_url, f"wav/{title}.wav")
        return title
    except Exception as e:
        print(f"处理视频失败：{url}，原因：{e}")
        return None
def download_single_video(url,headers):
    headers["Referer"] = url
    try:
        response = requests.get(url=url, headers=headers)
        html = response.text
        title = re.findall('title="(.*?)"', html)[0]
        print(f"处理视频: {title}")
        
        # 提取视频信息
        info = re.findall('window.__playinfo__=(.*?)</script>', html)[0]
        # 提取视频链接
        json_data = json.loads(info)
        video_url = json_data['data']['dash']['video'][0]['baseUrl']
        audio_url = json_data['data']['dash']['audio'][0]['baseUrl']

        os.makedirs(title, exist_ok=True)
        chunk_download(video_url, f"{title}/{title}.mp4")
        chunk_download(audio_url, f"{title}/{title}.mp3")
        chunk_download(audio_url, f"{title}/{title}.wav")
        chunk_download(audio_url, f"wav/{title}.wav")
        video_path = f"{title}/{title}.mp4"
        audio_path = f"{title}/{title}.mp3"
        output_path = f"{title}/{title}_merged.mp4"
        if os.path.exists(output_path):
            os.remove(output_path)
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
            os.remove(video_path)
            if result.returncode == 0:
                print(f"合成完成：{output_path}")
            else:
                print(f"合成失败，FFmpeg返回码: {result.returncode}")
                print(f"错误信息: {result.stderr.decode('utf-8', errors='ignore')}")
        except Exception as e:
            print(f"合成失败：{e}")
        return title
    except Exception as e:
        print(f"处理视频失败：{url}，原因：{e}")
        return None
def download_video(urls, cookie):
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_url = {executor.submit(download_single_video, url, headers): url for url in urls}
        completed_titles = []
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                title = future.result()
                if title:
                    completed_titles.append(title)
            except Exception as e:
                print(f"处理URL时出错 {url}: {e}")
                executor.shutdown(wait=False)
    return completed_titles
def download_video(urls, cookie):
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_url = {executor.submit(download_single_audio, url, headers): url for url in urls}
        completed_titles = []
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                title = future.result()
                if title:
                    completed_titles.append(title)
            except Exception as e:
                print(f"处理URL时出错 {url}: {e}")
                executor.shutdown(wait=False)
    
print("完成：",download_video(url, cookie))
# ...existing code...