import json
import os
import base64
import types
import time
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.asr.v20190614 import asr_client, models
from pydub import AudioSegment
import shutil
import requests
import re
tencentid = os.getenv("tencent_id")
tencentkey = os.getenv("tencent_key")
os.makedirs("temp", exist_ok=True)
cookie = os.getenv("b_cookie")
bvname="BV1tcJzz9Etx"
refer=f"https://www.bilibili.com/{bvname}"
url = f"https://www.bilibili.com/video/{bvname}"
headers = {
    "Cookie": cookie,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}
response = requests.get(url=url, headers=headers)
html = response.text
title = re.findall('title="(.*?)"', html)[0]
print(f"处理视频: {title}")
title1 =title+"\\"+title

def split_audio(input_file, output_dir, max_size=5*1024*1024):
    """
    用pydub将音频文件分割成每段小于max_size（默认10MB）的mp3文件
    """
    audio = AudioSegment.from_file(input_file)
    file_size = os.path.getsize(input_file)
    duration = len(audio)  # 毫秒
    bytes_per_ms = file_size / duration
    chunk_duration_ms = int(max_size / bytes_per_ms)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for i, start in enumerate(range(0, duration, chunk_duration_ms)):
        end = min(start + chunk_duration_ms, duration)
        chunk = audio[start:end]
        chunk_path = os.path.join(output_dir, f"chunk_{i}.mp3")
        chunk.export(chunk_path, format="mp3")
def mp3_to_text_tencent(mp3_file, tencentid, tencentkey):
    with open(mp3_file, 'rb') as f:
        audio_data = base64.b64encode(f.read()).decode('utf-8')
    # 初始化腾讯云 ASR 客户端
    cred = credential.Credential(tencentid, tencentkey)
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
def create_rec_task_with_data(dir, tencentid, tencentkey):
    """
    从目录中读取切割好的音频文件，逐个上传进行语音识别
    :param dir: 存放音频切片的目录
    :param tencentid: 腾讯云API ID
    :param tencentkey: 腾讯云API Key
    :return: 识别任务ID列表
    """
    # 初始化腾讯云客户端
    cred = credential.Credential(tencentid, tencentkey)
    httpProfile = HttpProfile()
    httpProfile.endpoint = "asr.tencentcloudapi.com"
    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    client = asr_client.AsrClient(cred, "ap-shanghai")
    
    # 获取目录中所有MP3文件并排序
    audio_files = [f for f in os.listdir(dir) if f.startswith("chunk_") and f.endswith(".mp3")]
    audio_files.sort(key=lambda x: int(x.split("_")[1].split(".")[0]))  # 按照序号排序
    
    task_ids = []
    for idx, audio_file in enumerate(audio_files):
        file_path = os.path.join(dir, audio_file)
        print(f"处理文件: {file_path}")
        
        # 读取音频文件并Base64编码
        with open(file_path, 'rb') as f:
            audio_data = base64.b64encode(f.read()).decode('utf-8')
        
        # 创建识别请求
        req = models.CreateRecTaskRequest()
        params = {
            "EngineModelType": "16k_zh",
            "ChannelNum": 1,
            "ResTextFormat": 0,
            "SourceType": 1,
            "Data": audio_data
        }
        req.from_json_string(json.dumps(params))
        
        # 发送请求并获取任务ID
        resp = client.CreateRecTask(req)
        print(f"Chunk {idx}:", resp.to_json_string())
        task_id = json.loads(resp.to_json_string())["Data"]["TaskId"]
        task_ids.append(task_id)
    
    return task_ids
def get_rec_result(task_ids, tencentid, tencentkey):
    cred = credential.Credential(tencentid, tencentkey)
    client = asr_client.AsrClient(cred, "ap-shanghai")
    results = []
    file=title1+".txt"
    with open(file, "w", encoding="utf-8") as f:
        f.write("")
    for task_id in task_ids:
        req = models.DescribeTaskStatusRequest()
        params = {"TaskId": int(task_id)}
        req.from_json_string(json.dumps(params))
        resp = client.DescribeTaskStatus(req)
        print(f"Task {task_id} result:", resp.to_json_string())

        with open(file, "a", encoding="utf-8") as f:
            f.write(json.loads(resp.to_json_string())["Data"]["Result"])
        results.append(resp.to_json_string())
        with open(title1+".txt", "a", encoding="utf-8") as f:
            f.write(json.loads(resp.to_json_string())["Data"]["Result"])
    return results
def convert_mp3_to_wav(input_mp3, output_wav):
    audio = AudioSegment.from_file(input_mp3)
    # 转为单声道、16k采样率
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(output_wav, format="wav")
if __name__ == "__main__":
    convert_mp3_to_wav(title1+".mp3", "temp/output.wav")
    file = "temp/output.wav"  # 建议用16k采样率单声道wav
    split_audio(file, "temp\\"+title)
    task_ids=  create_rec_task_with_data("temp\\"+title, tencentid, tencentkey)
    # task_ids= [12206247150, 12206247222, 12206247332, 12206247401, 12206247477, 12206247585, 12206247637, 12206247766, 12206247839]
    print("Task IDs:",task_ids)
    time.sleep(5)
    get_rec_result(task_ids, tencentid, tencentkey)
    shutil.rmtree("temp")
    