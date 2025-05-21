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
import time
import random
title=""
cookie = "buvid3=430277AB-F19D-E42F-B985-4E96B159881A84478infoc; b_nut=1746872884; _uuid=7A7D6A4B-1153-B29C-B944-F5B10F9421B9186258infoc; buvid4=B472E5D9-E55D-DE4D-8AFB-200A83FCA05486323-025051018-BE5tNRPq5Hm1axKT15iGDQ%3D%3D; rpdid=|(JJmY)YRu~~0J'u~RY)~k))m; DedeUserID=3546715265173614; DedeUserID__ckMd5=7b4e3ead3db48297; header_theme_version=CLOSE; enable_web_push=DISABLE; enable_feed_channel=ENABLE; fingerprint=ab96a73572632a9e1ebdd467149da5e1; buvid_fp_plain=undefined; buvid_fp=ab96a73572632a9e1ebdd467149da5e1; SESSDATA=cac768bb%2C1763282713%2C5e39d%2A51CjAZ7LI-EqGaLiW_TA1-VzQCfbh_KI35h0sCA2Uutj0OqrgFRPUgAhAt83HNs2auA0QSVk1Ub3lBdEh3bGttdkc1alBxNmJ1RFJBell6bkNxdkNPNkVEb3I5c0NkVVFhdHgtay0ybmtKMFhhYTF6Y2ZiV3E1OWpZLWVxNTY5ZjdxVFREVFlvNDZRIIEC; bili_jct=e832e3adb91f3531b0224708681bdc39; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDc5OTMzMTYsImlhdCI6MTc0NzczNDA1NiwicGx0IjotMX0.I35lF4Hth0G9xTEZtDdF9KfRcfihw6_lenhcGCLh5Q8; bili_ticket_expires=1747993256; CURRENT_QUALITY=120; bmg_af_switch=1; bmg_src_def_domain=i0.hdslb.com; sid=84ex66a0; b_lsid=8AE5C101C_196F24065CF; bp_t_offset_3546715265173614=1069373739180752896; home_feed_column=5; browser_resolution=1432-774; CURRENT_FNVAL=4048"
url =[
  "https://www.bilibili.com/video/BV16eJBzGEAY/?spm_id_from=333.337.search-card.all.click&vd_source=e4be74da35c9c95e7756dfd980a19587"
    ]
headers = {
    "Cookie": cookie,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}

def chunk_download(file_url, filename, task_headers):
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            with requests.get(file_url, headers=task_headers, stream=True, timeout=30) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                downloaded = 0
                
                # 减小chunk大小到1MB
                chunk_size = 1024 * 1024  # 1MB
                
                print(f"开始下载: {filename} (总大小: {total_size/1024/1024:.2f} MB)")
                start_time = time.time()
                with open(filename, "wb") as f:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # 计算下载进度
                            percent = (downloaded / total_size) * 100
                            
                            # 计算下载速度
                            elapsed_time = time.time() - start_time
                            if elapsed_time > 0:
                                speed = downloaded / elapsed_time / 1024 / 1024  # MB/s
                                
                                # 估计剩余时间
                                if percent > 0:
                                    remaining_size = total_size - downloaded
                                    eta_seconds = remaining_size / (downloaded / elapsed_time)
                                    eta_min = int(eta_seconds / 60)
                                    eta_sec = int(eta_seconds % 60)
                                    
                                    # 使用\r更新同一行内容，显示进度条
                                    print(f"\r下载进度: [{('█' * int(percent // 5)).ljust(20, '░')}] {percent:.1f}% | {speed:.2f} MB/s | 剩余: {eta_min}:{eta_sec:02d}", end="")
                
                print(f"\n下载完成：{filename} - 总用时: {time.time() - start_time:.1f}秒")
                return True
                
        except (requests.exceptions.ChunkedEncodingError, 
                requests.exceptions.ConnectionError, 
                requests.exceptions.ReadTimeout) as e:
            print(f"\n下载中断 (尝试 {attempt+1}/{max_retries}): {filename}, 错误: {e}")
            if attempt < max_retries - 1:
                sleep_time = retry_delay * (attempt + 1) + random.uniform(0, 1)
                print(f"等待 {sleep_time:.1f} 秒后重试...")
                time.sleep(sleep_time)
            
        except Exception as e:
            print(f"\n下载失败：{filename}，原因：{e}")
            break
    return False
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
        chunk_download(audio_url, f"wav/{title}.wav",headers)
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
        chunk_download(video_url, f"{title}/{title}.mp4",headers)
        chunk_download(audio_url, f"{title}/{title}.mp3",headers)
        chunk_download(audio_url, f"{title}/{title}.wav",headers)
        chunk_download(audio_url, f"wav/{title}.wav",headers)
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
    # with ThreadPoolExecutor(max_workers=1) as executor:
    #     future_to_url = {executor.submit(download_single_video, url, headers): url for url in urls}
    #     completed_titles = []
    #     for future in as_completed(future_to_url):
    #         url = future_to_url[future]
    #         try:
    #             title = future.result()
    #             if title:
    #                 completed_titles.append(title)
    #         except Exception as e:
    #             print(f"处理URL时出错 {url}: {e}")
    #             executor.shutdown(wait=False)
    # return completed_titles
    # completed_titles = []
    for url in urls:
        download_single_video(url, headers)
def download_audio(urls, cookie):
    # 这里不使用线程池，因为我实测中发现如果使用线程池会导致连接中断？不知道有没有人有好的办法解决
    ## 或许只爬取网页数据使用线程池会好一点，但是持续连接下载使用线程池会导致连接中断
    # with ThreadPoolExecutor(max_workers=1) as executor:
    #     future_to_url = {executor.submit(download_single_audio, url, headers): url for url in urls}
    #     completed_titles = []
    #     for future in as_completed(future_to_url):
    #         url = future_to_url[future]
    #         try:
    #             title = future.result()
    #             if title:
    #                 completed_titles.append(title)
    #         except Exception as e:
    #             print(f"处理URL时出错 {url}: {e}")
    #             executor.shutdown(wait=False)
    completed_titles = []
    for url in urls:
        download_single_audio(url, headers)
    return completed_titles
print("完成：",download_video(url, cookie))
# ...existing code...