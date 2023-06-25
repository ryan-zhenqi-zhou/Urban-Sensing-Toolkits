# 导入界面库
import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtCore import QThread, pyqtSignal, QFile, QTextStream,Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QComboBox, QTextBrowser, QTableWidget, \
                            QTableWidgetItem, QHeaderView, QProgressBar, QHBoxLayout, QVBoxLayout, QMessageBox,QDialog,QLabel,QLineEdit,\
                            QGridLayout,QMessageBox
# 导入爬虫库
import requests
import json
import pandas as pd
import urllib.request
import requests
import json
import pandas as pd
import time
import random
import cv2
import os
import time

# 登陆界面
USER_PWD = {
        'Ryan Zhou': '12345678'
    }

# 做第一层登陆界面
class Demo(QWidget):
    def __init__(self):
        super(Demo, self).__init__()
        self.resize(300, 100)
        self.setWindowTitle('登陆界面')
        self.user_label = QLabel('许可账号:', self)
        self.pwd_label = QLabel('许可密码:', self)
        self.user_line = QLineEdit(self)
        self.pwd_line = QLineEdit(self)
        self.login_button = QPushButton('登陆', self)

        self.grid_layout = QGridLayout()
        self.h_layout = QHBoxLayout()
        self.v_layout = QVBoxLayout()

        self.lineedit_init()
        self.pushbutton_init()
        self.Crawl_Window = CrawlWindow()
        self.layout_init()

    def layout_init(self):
        self.grid_layout.addWidget(self.user_label, 0, 0, 1, 1)
        self.grid_layout.addWidget(self.user_line, 0, 1, 1, 1)
        self.grid_layout.addWidget(self.pwd_label, 1, 0, 1, 1)
        self.grid_layout.addWidget(self.pwd_line, 1, 1, 1, 1)
        self.h_layout.addWidget(self.login_button)
        self.v_layout.addLayout(self.grid_layout)
        self.v_layout.addLayout(self.h_layout)

        self.setLayout(self.v_layout)

    def lineedit_init(self):
        self.user_line.setPlaceholderText('请输入许可账号')
        self.pwd_line.setPlaceholderText('请输入许可密码')
        self.pwd_line.setEchoMode(QLineEdit.Password)

        self.user_line.textChanged.connect(self.check_input_func)
        self.pwd_line.textChanged.connect(self.check_input_func)

    def check_input_func(self):
        if self.user_line.text() and self.pwd_line.text():
            self.login_button.setEnabled(True)
        else:
            self.login_button.setEnabled(False)

    def pushbutton_init(self):
        self.login_button.setEnabled(False)
        self.login_button.clicked.connect(self.check_login_func)

    def check_login_func(self):
        if USER_PWD.get(self.user_line.text()) == self.pwd_line.text():
            self.Crawl_Window.exec_()
        else:
            QMessageBox.critical(self, 'Wrong', '登陆失败！请联系453497361@qq.com')

        self.user_line.clear()
        self.pwd_line.clear()

# 主界面 把需要的控件进行实例化
class CrawlWindow(QDialog):
    def __init__(self):
        super(CrawlWindow, self).__init__()
        self.resize(1200, 800)
        self.setWindowTitle('图像绿视率提取器')

        self.fangfa_label = QLabel('使用方法：在C盘根目录下放入picture文件夹，里面的图像格式为jpg格式（图像命名最好以数字命名），在与软件相同目录下建立hsv文件夹，点击软件界面的开始后将会将结果输出在与软件相同目录下hsv文件夹和result.txt文件中。', self)
        self.fangfa_label.setAlignment(Qt.AlignCenter)
        self.fangfa_label.setStyleSheet("QLabel{color:rgb(70,70,70,255);font-size:15px;font-weight:normal;font-family:Arial;}")

        self.jieshao_label = QLabel('南京林业大学 周珍琦 徐振', self)
        self.jieshao_label.setAlignment(Qt.AlignCenter)
        self.jieshao_label.setStyleSheet("QLabel{color:rgb(70,70,70,255);font-size:10px;font-weight:normal;font-family:Arial;}")

        self.start_btn = QPushButton(self)
        self.stop_btn = QPushButton(self)
        self.log_browser = QTextBrowser(self)

        self.h_layout = QHBoxLayout()
        self.v_layout = QVBoxLayout()

        self.crawl_thread = CrawlThread(self)

        self.db = None

        self.btn_init()
        self.layout_init()
        self.crawl_init()

    def btn_init(self):
        self.start_btn.setText('开始')
        self.stop_btn.setText('停止')
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.start_btn.clicked.connect(lambda: self.btn_slot(self.start_btn))
        self.stop_btn.clicked.connect(lambda: self.btn_slot(self.stop_btn))

    def layout_init(self):
        self.v_layout.addWidget(self.fangfa_label)
        self.h_layout.addWidget(self.start_btn)
        self.h_layout.addWidget(self.stop_btn)
        self.v_layout.addWidget(self.log_browser)
        self.v_layout.addLayout(self.h_layout)
        self.v_layout.addWidget(self.jieshao_label)
        self.setLayout(self.v_layout)

    def crawl_init(self):
        self.crawl_thread.finished_signal.connect(self.finish_slot)
        self.crawl_thread.log_signal.connect(self.set_log_slot)

    def btn_slot(self, btn):
        if btn == self.start_btn:
            self.log_browser.clear()
            self.log_browser.append('<font color="red">开始</font>')
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.crawl_thread.start()
        else:
            self.log_browser.append('<font color="red">停止</font>')
            self.stop_btn.setEnabled(False)
            self.start_btn.setEnabled(True)
            self.crawl_thread.terminate()

    def finish_slot(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def set_log_slot(self, new_log):
        self.log_browser.append(new_log)


# 爬虫代码
class CrawlThread(QThread):
    finished_signal = pyqtSignal()
    log_signal = pyqtSignal(str)
    def __init__(self, cw):
        super(CrawlThread, self).__init__(cw)
        self.Crawl_Window = cw

    # 绿视率
    def brg2hsv(self,image_path, save_path_hsv,Txt_path):
        f = open(Txt_path, 'a')
        f.write("Name,Percentage" + "\n")
        f.close()
        filenames = os.listdir(image_path)
        for filename in filenames:
            t = int(time.time())
            examname = filename[:-4]
            type = filename.split('.')[-1]
            img = cv2.imread(image_path + filename)
            img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            save_hsv = save_path_hsv + "\\" + examname + '_HSV' + '.' + type
            cv2.imwrite(save_hsv, img_hsv)
            row_num = img_hsv.shape[0]
            column_num = img_hsv.shape[1]
            k = 0
            for i in range(0, row_num):
                for j in range(0, column_num):
                    if 77 > img_hsv[i, j, 0] > 35:
                        k = k + 1
            Percentage = k / (row_num * column_num)
            result = filename.split(".")[0] + ".jpg" + "," + str(Percentage) + "\n"
            f = open(Txt_path, 'a')
            f.write(result)
            f.close()
            self.log_signal.emit(filename + " " + "识别完成！" + "用时：" + str(int(time.time() - t)) + "s")

    # 运行函数1
    def run(self):
        image_path = "C:\\picture\\"
        Txt_path = ".\\result.txt"
        save_path_hsv = ".\\hsv"
        try:
            self.brg2hsv(image_path, save_path_hsv,Txt_path)
            self.log_signal.emit('<font color="red">结束！</font>')
        except:
            self.log_signal.emit('<font color="red">出现错误！</font>')
            self.log_signal.emit('<font color="red">请检查picture文件夹！</font>')

        self.finished_signal.emit()

# 主函数
if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())

































