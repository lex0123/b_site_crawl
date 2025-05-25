import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTextEdit, QGroupBox, QFormLayout, QMessageBox,
                             QFileDialog, QCheckBox, QProgressBar, QStatusBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import json
import requests
import re
from bilibili_get_all.subtitle  import get_video_subtitle
from bilibili_get_all.downloader import download_video,download_audio     
from bilibili_get_all.tencent_asr import create_rec_task_with_data, get_rec_result
# 捕获打印输出以更新UI
import io
import sys
class Worker(QThread):
    """工作线程类，用于在后台执行耗时操作"""
    update_progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, bv_number, cookie, api_key):
        super().__init__()
        self.bv_number = bv_number
        self.cookie = cookie
        self.api_key = api_key
        # print(f"Worker initialized with BV: {self.bv_number}, Cookie: {self.cookie}, API Key: {self.api_key}")
        
    def run(self):
            
        try:
            original_stdout = sys.stdout
            sys.stdout = io.StringIO()
            print(f"开始处理视频：{self.bv_number}")
            # 调用视频字幕提取和总结函数
            get_video_subtitle(self.api_key, self.bv_number,self.cookie)
            
            # 获取捕获的输出
            output = sys.stdout.getvalue()
            sys.stdout = original_stdout
            
            # 发送进度更新和完成信号
            self.update_progress.emit(output)
            self.finished.emit(True, "处理完成！")
            
        except Exception as e:
            self.finished.emit(False, f"错误：{str(e)}")


class BilibiliApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("B站视频字幕提取与AI总结工具")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()
        
    def initUI(self):
        # 创建中央部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 创建输入表单
        input_group = QGroupBox("输入参数")
        form_layout = QFormLayout()
        
        # BV号输入
        self.bv_input = QLineEdit()
        self.bv_input.setPlaceholderText("例如：BV1M64y1E7o1,不同bv号之间用逗号隔开")
        form_layout.addRow("B站视频BV号:", self.bv_input)
        
        # Cookie输入
        self.cookie_input = QLineEdit()
        self.cookie_input.setPlaceholderText("输入B站cookie...")
        self.cookie_input.setEchoMode(QLineEdit.Password)  # 隐藏敏感信息
        form_layout.addRow("B站Cookie:", self.cookie_input)
        
                
        # 显示Cookie选项
        show_cookie_layout = QHBoxLayout()
        self.show_cookie_checkbox = QCheckBox("显示Cookie")
        self.show_cookie_checkbox.stateChanged.connect(self.toggle_cookie_visibility)
        show_cookie_layout.addWidget(self.show_cookie_checkbox)
        show_cookie_layout.addStretch()
        form_layout.addRow("", show_cookie_layout)
        # 显示Cookie选项


        # show_cookie_layout = QHBoxLayout()
        # self.show_cookie_checkbox = QCheckBox("显示Cookie")
        # self.show_cookie_checkbox.stateChanged.connect(self.toggle_cookie_visibility)
        # show_cookie_layout.addWidget(self.show_cookie_checkbox)
        # show_cookie_layout.addStretch()
        # form_layout.addRow("", show_cookie_layout)
        
        # DeepSeek API密钥输入
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("输入DeepSeek API密钥...")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("DeepSeek API密钥:", self.api_key_input)
        
        # 显示API密钥选项
        show_api_layout = QHBoxLayout()
        self.show_api_checkbox = QCheckBox("显示API密钥")
        self.show_api_checkbox.stateChanged.connect(self.toggle_api_visibility)
        show_api_layout.addWidget(self.show_api_checkbox)
        show_api_layout.addStretch()
        form_layout.addRow("", show_api_layout)
        
        # 腾讯云id和密钥输入
        self.tencent_api_id_input = QLineEdit()
        self.tencent_api_id_input.setPlaceholderText("输入腾讯id...")
        self.tencent_api_id_input.setEchoMode(QLineEdit.Normal)
        form_layout.addRow("腾讯id:", self.tencent_api_id_input)
        
        self.tencent_api_secret_input = QLineEdit()
        self.tencent_api_secret_input.setPlaceholderText("腾讯云API密钥...")
        self.tencent_api_secret_input.setEchoMode(QLineEdit.Password)  # 隐藏敏感信息
        form_layout.addRow("腾讯云API密钥:", self.tencent_api_secret_input)

     
        
        # # 显示API密钥选项
        tencent_api_secret_layout = QHBoxLayout()
        self.tencent_api_secret_checkbox = QCheckBox("显示API密钥")
        self.tencent_api_secret_checkbox.stateChanged.connect(self.toggle_api_visibility)
        tencent_api_secret_layout.addWidget(self.tencent_api_secret_checkbox)
        tencent_api_secret_layout.addStretch()
        form_layout.addRow("", tencent_api_secret_layout)
        input_group.setLayout(form_layout)
        main_layout.addWidget(input_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 保存配置按钮
        self.save_config_btn = QPushButton("保存配置")
        self.save_config_btn.clicked.connect(self.save_config)
        button_layout.addWidget(self.save_config_btn)
        
        # 加载配置按钮
        self.load_config_btn = QPushButton("加载配置")
        self.load_config_btn.clicked.connect(self.load_config)
        button_layout.addWidget(self.load_config_btn)
        
        # 执行按钮
        self.execute_btn = QPushButton("下载字幕")
        self.execute_btn.clicked.connect(self.downloadsubtitle)
        button_layout.addWidget(self.execute_btn)
        self.download_video_btn = QPushButton("下载视频")
        self.download_video_btn.clicked.connect(self.downloadvideo)
        button_layout.addWidget(self.download_video_btn)
        self.download_audio_btn = QPushButton("下载音频")
        self.download_audio_btn.clicked.connect(self.downloadaudio)
        button_layout.addWidget(self.download_audio_btn)
        self.asr_btn = QPushButton("下载音频并识别语音")
        self.asr_btn.clicked.connect(self.asr)
        button_layout.addWidget(self.asr_btn)
        main_layout.addLayout(button_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 设置为不确定模式
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # 输出日志区域
        log_group = QGroupBox("处理日志")
        log_layout = QVBoxLayout()
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        log_layout.addWidget(self.log_output)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        # 状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("就绪")
        
        # 尝试加载之前保存的配置
        self.try_load_config()
        
    def toggle_cookie_visibility(self, state):
        if state == Qt.Checked:
            self.cookie_input.setEchoMode(QLineEdit.Normal)
        else:
            self.cookie_input.setEchoMode(QLineEdit.Password)
            
    def toggle_api_visibility(self, state):
        if state == Qt.Checked:
            self.api_key_input.setEchoMode(QLineEdit.Normal)
        else:
            self.api_key_input.setEchoMode(QLineEdit.Password)
    
    def save_config(self):
        try:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(
                self, "保存配置", "config.json", "JSON Files (*.json)", options=options
            )
            if file_name:
                config = {
                    "tencentid": self.tencent_api_id_input.text(),
                    "tencentsecret": self.tencent_api_secret_input.text(),
                    "cookie": self.cookie_input.text(),
                    "api_key": self.api_key_input.text()
                }
                
                with open(file_name, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                
                self.statusBar.showMessage(f"配置已保存到 {file_name}")
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"保存配置时出错: {str(e)}")
    
    def load_config(self):
        try:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getOpenFileName(
                self, "加载配置", "", "JSON Files (*.json)", options=options
            )
            
            if file_name:
                with open(file_name, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                if "cookie" in config:
                    self.cookie_input.setText(config["cookie"])
                if "api_key" in config:
                    self.api_key_input.setText(config["api_key"])
                    
                if "tencentid" in config:
                    self.tencent_api_id_input.setText(config["tencentid"])

                if "tencentsecret" in config:
                    self.tencent_api_secret_input.setText(config["tencentsecret"])
                
                self.statusBar.showMessage(f"配置已从 {file_name} 加载")
        except Exception as e:
            QMessageBox.critical(self, "加载失败", f"加载配置时出错: {str(e)}")
    
    def try_load_config(self):
        """尝试加载默认配置文件"""
        if os.path.exists("config.json"):
            try:
                with open("config.json", 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                if "cookie" in config:
                    self.cookie_input.setText(config["cookie"])
                
                if "api_key" in config:
                    self.api_key_input.setText(config["api_key"])

                if "tencentid" in config:
                    self.api_key_input.setText(config["tencentid"])

                if "tencentsecret" in config:
                    self.api_key_input.setText(config["tencentsecret"])

                
                self.statusBar.showMessage("已加载默认配置")
            except:
                pass
    
    def downloadsubtitle(self):
        """执行视频处理任务"""
        bv_number = self.bv_input.text().strip()
        cookie = self.cookie_input.text().strip()
        api_key = self.api_key_input.text().strip()
        
        if not bv_number:
            QMessageBox.warning(self, "输入错误", "请输入BV号")
            return
        
        if not cookie:
            QMessageBox.warning(self, "输入错误", "请输入B站Cookie")
            return
        
        # API密钥可选，不强制要求
        
        # 清空日志区域
        self.log_output.clear()
        
        # 显示进度条，禁用按钮
        self.progress_bar.setVisible(True)
        self.execute_btn.setEnabled(False)
        self.statusBar.showMessage("正在处理...")
        
        # 创建并启动工作线程
        self.worker = Worker(bv_number, cookie, api_key)
        print("123123123123")
        self.worker.update_progress.connect(self.update_log)
        self.worker.finished.connect(self.task_completed)
        self.worker.start()
    def downloadvideo(self):
        return
    def downloadaudio(self):
        return
    def asr(self):
        return
    def update_log(self, text):
        """更新日志区域"""
        self.log_output.append(text)
        # 滚动到底部
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )
    
    def task_completed(self, success, message):
        """任务完成回调"""
        # 隐藏进度条，启用按钮
        self.progress_bar.setVisible(False)
        self.execute_btn.setEnabled(True)
        
        # 更新状态栏
        self.statusBar.showMessage(message)
        
        if success:
            QMessageBox.information(self, "处理完成", message)
        else:
            QMessageBox.critical(self, "处理失败", message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BilibiliApp()
    window.show()
    sys.exit(app.exec_())