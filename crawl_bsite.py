# 导入数据请求模块
import os
import requests
# 导入正则表达式模块
import re
# 导入json模块
import json
from pydub import AudioSegment
from vosk import Model, KaldiRecognizer
import wave
def mp3_to_text_offline(mp3_file, model_path):
    wav_file = mp3_file.replace('.mp3', '.wav')
    audio = AudioSegment.from_mp3(mp3_file)
    audio.export(wav_file, format="wav")
    if not os.path.exists(model_path):
        return "模型路径不存在，请检查！"
    model = Model(model_path)
    
    # 打开 .wav 文件进行识别
    wf = wave.open(wav_file, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in [8000, 16000]:
        return "音频格式不支持，请确保为单声道 16-bit 16kHz。"
    
    recognizer = KaldiRecognizer(model, wf.getframerate())
    recognizer.SetWords(True)
    
    result_text = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            result_json = json.loads(result)
            if "text" in result_json:
                # 去掉空格并添加到结果列表
                result_text+=(result_json["text"].replace(" ", ""))
    wf.close()
    final_text = result_text
    with open('result.txt', 'w', encoding='utf-8') as f:
         f.write(final_text)
    wf.close()
    return result_text
url = 'https://www.bilibili.com/video/BV1tuR2YRE13'
cookie = "buvid3=7893001B-A462-AAA0-AB35-1978835AA7A995939infoc;"
headers = {
        "Referer": url,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}
# 发送请求
response = requests.get(url=url, headers=headers)
html = response.text
# print(html)
# 解析数据: 提取视频标题
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
with open(title + '.mp4', mode='wb') as v:
    v.write(video_content)
with open( title + '.wav', mode='wb') as a:
    a.write(audio_content)
command = f"ffmpeg -i {title}.wav -ar 16000 -ac 1 output.wav"
os.system(command)
input_file='output.wav'
model_path = "/home/lizheng/下载/vosk-model-cn-kaldi-multicn-0.15" # 替换为你的模型路径
if os.path.exists(input_file):
    text = mp3_to_text_offline(input_file, model_path)  # 使用 .wav 文件
    print(f"识别的文字内容: {text}")
else:
    print(f"文件 {input_file} 不存在。")