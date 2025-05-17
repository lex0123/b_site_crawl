# 导入数据请求模块
import os
import requests
# 导入正则表达式模块
import re
# 导入json模块
import json
import base64
import json
from tencentcloud.asr.v20190614 import asr_client, models
from tencentcloud.common import credential
from pydub import AudioSegment

def compress_audio(input_file, output_file):
    audio = AudioSegment.from_file(input_file)
    # 设置采样率为 16kHz，单声道
    audio = audio.set_frame_rate(16000).set_channels(1)
    # 导出压缩后的音频
    audio.export(output_file, format="mp3")

def split_audio(input_file, output_dir, chunk_duration_ms=60000):
    """
    将音频文件分割为指定时长的片段。
    :param input_file: 输入音频文件路径
    :param output_dir: 输出片段存储目录
    :param chunk_duration_ms: 每段音频的时长（以毫秒为单位），默认 60 秒
    """
    # 加载音频文件
    audio = AudioSegment.from_file(input_file)
    # 分割音频
    for i in range(0, len(audio), chunk_duration_ms):
        chunk = audio[i:i + chunk_duration_ms]
        chunk.export(f"{output_dir}/chunk_{i // chunk_duration_ms}.mp3", format="mp3")

def mp3_to_text_tencent(mp3_file, tecentid, tecentkey):
    # 读取 MP3 文件并进行 Base64 编码
    with open(mp3_file, 'rb') as f:
        audio_data = base64.b64encode(f.read()).decode('utf-8')

    # 初始化腾讯云 ASR 客户端
    cred = credential.Credential(tecentid, tecentkey)
    client = asr_client.AsrClient(cred, "ap-guangzhou")  # 根据需要选择区域

    # 创建请求对象
    req = models.SentenceRecognitionRequest()
    params = {
        "ProjectId": 0,  # 项目 ID，默认为 0
        "SubServiceType": 2,  # 子服务类型，2 表示实时流式识别
        "EngSerViceType": "16k_zh",  # 引擎类型，16k_zh 表示中文普通话
        "SourceType": 1,  # 音频来源，1 表示音频数据直接上传
        "VoiceFormat": "mp3",  # 音频格式
        "UsrAudioKey": "test",  # 用户自定义的音频标识
        "Data": audio_data,  # 音频数据（Base64 编码）
    }
    req.from_json_string(json.dumps(params))

    # 发送请求并获取响应
    resp = client.SentenceRecognition(req)
    result = resp.to_json_string()
    result_json = json.loads(result)

    # 提取识别结果
    if "Result" in result_json:
        return result_json["Result"]
    else:
        return "识别失败，请检查音频文件或参数配置！"

# url = 'https://www.bilibili.com/video/BV1tuR2YRE13'
# cookie = "buvid3=7893001B-A462-AAA0-AB35-1978835AA7A995939infoc;"
# headers = {
#         "Referer": url,
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
# }
# # 发送请求
# response = requests.get(url=url, headers=headers)
# html = response.text
# # print(html)
# # 解析数据: 提取视频标题
# title = re.findall('title="(.*?)"', html)[0]
# print(title)
# # # 提取视频信息
# info = re.findall('window.__playinfo__=(.*?)</script>', html)[0]
# # print(info)
# # info -> json字符串转成json字典
# json_data = json.loads(info)
# # # 提取视频链接
# video_url = json_data['data']['dash']['video'][0]['baseUrl']
# audio_url = json_data['data']['dash']['audio'][0]['baseUrl']
# video_content = requests.get(url=video_url, headers=headers).content
# audio_content = requests.get(url=audio_url, headers=headers).content
# # 保存数据
# with open(title + '.mp4', mode='wb') as v:
#     v.write(video_content)
# input=title + '.wav'
# with open( title + '.wav', mode='wb') as a:
#     a.write(audio_content)
input = "output.wav"  # 替换为您的 MP3 文件路径
tecentid = ""  # 替换为您的腾讯云 SecretId
tecentkey = ""  # 替换为您的腾讯云 SecretKey

results = []
output_dir = "chunks"
with open("input.txt", 'w') as f:
    for chunk_file in sorted(os.listdir(output_dir),key=lambda x: int(re.search(r'\d+', x).group())):
        chunk_path = os.path.join(output_dir, chunk_file)
        print(f"Processing chunk: {chunk_path}")
        text = mp3_to_text_tencent(chunk_path, tecentid, tecentkey)
        results.append(text)
        f.write(text + "\n")
    full_text = " ".join(results)
f.close
print(f"识别的文字内容: {full_text}")