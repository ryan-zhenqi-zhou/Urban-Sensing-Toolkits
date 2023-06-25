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
        self.setWindowTitle('街景地图提取器')

        self.fangfa_label = QLabel('使用方法：在C盘根目录下放入picture.csv文件，格式为“编号,坐标百度经度,坐标百度纬度”三列，在与软件相同目录下建立picture文件夹，输入AK，点击软件界面的开始爬取后将会将结果输出在与软件相同目录下picture文件夹和message.txt文件中。', self)
        self.fangfa_label.setAlignment(Qt.AlignCenter)
        self.fangfa_label.setStyleSheet("QLabel{color:rgb(70,70,70,255);font-size:15px;font-weight:normal;font-family:Arial;}")

        self.ak_label = QLabel('AK:', self)
        self.ak_line = QLineEdit(self)

        self.jieshao_label = QLabel('南京林业大学 周珍琦 徐振', self)
        self.jieshao_label.setAlignment(Qt.AlignCenter)
        self.jieshao_label.setStyleSheet("QLabel{color:rgb(70,70,70,255);font-size:10px;font-weight:normal;font-family:Arial;}")

        self.start_btn = QPushButton(self)
        self.stop_btn = QPushButton(self)
        self.log_browser = QTextBrowser(self)

        self.koujian_h_layout = QHBoxLayout()
        self.h_layout = QHBoxLayout()
        self.v_layout = QVBoxLayout()

        self.crawl_thread = CrawlThread(self)

        self.db = None

        self.lineedit1_init()
        self.btn_init()
        self.layout_init()
        self.crawl_init()

    def btn_init(self):
        self.start_btn.setText('开始爬取')
        self.stop_btn.setText('停止爬取')
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.start_btn.clicked.connect(lambda: self.btn_slot(self.start_btn))
        self.stop_btn.clicked.connect(lambda: self.btn_slot(self.stop_btn))

    def layout_init(self):
        self.v_layout.addWidget(self.fangfa_label)
        self.koujian_h_layout.addWidget(self.ak_label)
        self.koujian_h_layout.addWidget(self.ak_line)
        self.v_layout.addLayout(self.koujian_h_layout)
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
            self.log_browser.append('<font color="red">开始爬取</font>')
            self.ak_line.setEnabled(False)
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.crawl_thread.start()
        else:
            self.log_browser.append('<font color="red">停止爬取</font>')
            self.ak_line.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.start_btn.setEnabled(True)
            self.crawl_thread.terminate()

    def finish_slot(self):
        self.ak_line.setEnabled(True)
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def set_log_slot(self, new_log):
        self.log_browser.append(new_log)

    def lineedit1_init(self):
        self.ak_line.setPlaceholderText('请输入AK')

        self.ak_line.textChanged.connect(self.check_input1_func)

    def check_input1_func(self):
        if self.ak_line.text():
            self.start_btn.setEnabled(True)
        else:
            self.start_btn.setEnabled(False)

# 爬虫代码
class CrawlThread(QThread):
    finished_signal = pyqtSignal()
    log_signal = pyqtSignal(str)
    def __init__(self, cw):
        super(CrawlThread, self).__init__(cw)
        self.Crawl_Window = cw

    def pic_download(self,pic_path, f_pic):
        web = urllib.request.urlopen(pic_path)
        itdata = web.read()
        f_tup = open(f_pic, "wb")
        f_tup.write(itdata)
        f_tup.close()

    def write_txt(self,path, content):
        f = open(path, 'a', encoding='utf-8')
        f.write(content)
        f.close()

    def get_data(self,key_o, lng, lat, i, j,f_pic,f_path):
        url = "http://api.map.baidu.com/panorama/v2?ak=" + key_o + "&width=1024&height=512&location=" + lng + "," + lat + "&fov=90&heading=" + str(
            i * 90)
        try:
            js = requests.get(url).text
            if js.find('status') == -1:
                time.sleep(3)
                self.pic_download(url, f_pic + "\\" + j + "_" + str(i) + '.jpg')
                content = j + ',' + lng + ',' + lat + ',' + j + '_' + str(
                    i) + '.jpg' + "\n"
                self.write_txt(f_path, content)
            else:
                self.log_signal.emit('AK错误或需要更换AK,已把遗留信息存储在log.txt中')
                with open('./log.txt', 'a') as fl:
                    fl.write(url + '\n')
                return 'NO'
        except:
            self.log_signal.emit('error,已把遗留信息存储在log.txt中')
            with open('./log.txt', 'a') as fl:
                fl.write(url + '\n')

    # 运行函数2
    def run1(self,ak):

        f_pic = "./picture/"
        f_path = "./message.txt"

        p = open("C:\\picture.csv")
        date_1 = p.read().splitlines()
        a_1 = list(filter(None, date_1))

        time.sleep(5)
        y = 0
        for x in range(len(a_1)):
            id = a_1[x].split(',')[0]
            Lng = a_1[x].split(',')[1]
            Lat = a_1[x].split(',')[2]

            for i in range(0, 4):
                y = y + 1
                self.log_signal.emit('正在爬取第{:.0f}张街景地图'.format(y))
                self.get_data(ak, Lng, Lat, i, id,f_pic,f_path)


    # 运行函数1
    def run(self):
        ak_o = self.Crawl_Window.ak_line.text()
        try:
            self.run1(str(ak_o))
            self.log_signal.emit('<font color="red">爬取结束！</font>')
        except:
            self.log_signal.emit('<font color="red">出现错误！</font>')
            self.log_signal.emit('<font color="red">请输入正确的AK！</font>')

        self.finished_signal.emit()

# 主函数
if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())

































