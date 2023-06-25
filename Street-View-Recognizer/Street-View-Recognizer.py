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
import math
import shapefile
import csv
# 导入识别库
from urllib import request
import ssl
import json
import base64
import requests
import os
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
        self.setWindowTitle('街景图像识别软件')
        self.fangfa_label = QLabel('使用方法：在C盘根目录下放入带有街景图片的test文件夹,点击软件界面的开始识别后将会将识别结果输出在C盘cg21.txt文件中', self)
        self.fangfa_label.setAlignment(Qt.AlignCenter)
        self.fangfa_label.setStyleSheet("QLabel{color:rgb(70,70,70,255);font-size:15px;font-weight:normal;font-family:Arial;}")
        self.ak_label = QLabel('AK:', self)
        self.ak_line = QLineEdit(self)
        self.sk_label = QLabel('SK:', self)
        self.sk_line = QLineEdit(self)
        self.jieshao_label = QLabel('南京林业大学 周珍琦 徐振', self)
        self.jieshao_label.setAlignment(Qt.AlignCenter)
        self.jieshao_label.setStyleSheet("QLabel{color:rgb(70,70,70,255);font-size:10px;font-weight:normal;font-family:Arial;}")
        self.start_btn = QPushButton(self)
        self.stop_btn = QPushButton(self)
        self.table = QTableWidget(self)
        self.log_browser = QTextBrowser(self)
        self.koujian_h_layout = QHBoxLayout()
        self.h_layout = QHBoxLayout()
        self.v_layout = QVBoxLayout()
        self.crawl_thread = CrawlThread(self)
        self.db = None
        self.lineedit1_init()
        self.btn_init()
        self.table_init()
        self.layout_init()
        self.crawl_init()
    def btn_init(self):
        self.start_btn.setText('开始识别')
        self.stop_btn.setText('停止识别')
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.start_btn.clicked.connect(lambda: self.btn_slot(self.start_btn))
        self.stop_btn.clicked.connect(lambda: self.btn_slot(self.stop_btn))
    def table_init(self):
        self.table.setColumnCount(19)
        self.table.setHorizontalHeaderLabels(['照片名称', '山', '水', '田', '湖泊','草','竹','植物', '花', '道路', '建筑', '人','动物','车','指示牌', '栏杆', '座椅', '石头','雕像'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    def layout_init(self):
        self.v_layout.addWidget(self.fangfa_label)
        self.koujian_h_layout.addWidget(self.ak_label)
        self.koujian_h_layout.addWidget(self.ak_line)
        self.koujian_h_layout.addWidget(self.sk_label)
        self.koujian_h_layout.addWidget(self.sk_line)
        self.v_layout.addLayout(self.koujian_h_layout)
        self.h_layout.addWidget(self.start_btn)
        self.h_layout.addWidget(self.stop_btn)
        self.v_layout.addWidget(self.table)
        self.v_layout.addWidget(self.log_browser)
        self.v_layout.addLayout(self.h_layout)
        self.v_layout.addWidget(self.jieshao_label)
        self.setLayout(self.v_layout)
    def crawl_init(self):
        self.crawl_thread.finished_signal.connect(self.finish_slot)
        self.crawl_thread.log_signal.connect(self.set_log_slot)
        self.crawl_thread.result_signal.connect(self.set_table_slot)
    def btn_slot(self, btn):
        if btn == self.start_btn:
            self.log_browser.clear()
            self.log_browser.append('<font color="red">开始识别</font>')
            self.table.clearContents()
            self.table.setRowCount(0)
            self.ak_line.setEnabled(False)
            self.sk_line.setEnabled(False)
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.crawl_thread.start()
        else:
            self.log_browser.append('<font color="red">停止识别</font>')
            self.ak_line.setEnabled(True)
            self.sk_line.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.start_btn.setEnabled(True)
            self.crawl_thread.terminate()
    def finish_slot(self):
        self.ak_line.setEnabled(True)
        self.sk_line.setEnabled(True)
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    def set_log_slot(self, new_log):
        self.log_browser.append(new_log)
    def set_table_slot(self,zhaopian,shan,shui,tian,hupo,cao,zhu,zhiwu,hua,daolu,jianzhu,ren,dongwu,che,zhishipai,langan,zuoyi,shitou,diaoxiang):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(zhaopian))
        self.table.setItem(row, 1, QTableWidgetItem(shan))
        self.table.setItem(row, 2, QTableWidgetItem(shui))
        self.table.setItem(row, 3, QTableWidgetItem(tian))
        self.table.setItem(row, 4, QTableWidgetItem(hupo))
        self.table.setItem(row, 5, QTableWidgetItem(cao))
        self.table.setItem(row, 6, QTableWidgetItem(zhu))
        self.table.setItem(row, 7, QTableWidgetItem(zhiwu))
        self.table.setItem(row, 8, QTableWidgetItem(hua))
        self.table.setItem(row, 9, QTableWidgetItem(daolu))
        self.table.setItem(row, 10, QTableWidgetItem(jianzhu))
        self.table.setItem(row, 11, QTableWidgetItem(ren))
        self.table.setItem(row, 12, QTableWidgetItem(dongwu))
        self.table.setItem(row, 13, QTableWidgetItem(che))
        self.table.setItem(row, 14, QTableWidgetItem(zhishipai))
        self.table.setItem(row, 15, QTableWidgetItem(langan))
        self.table.setItem(row, 16, QTableWidgetItem(zuoyi))
        self.table.setItem(row, 17, QTableWidgetItem(shitou))
        self.table.setItem(row, 18, QTableWidgetItem(diaoxiang))
    def lineedit1_init(self):
        self.ak_line.setPlaceholderText('请输入AK')
        self.sk_line.setPlaceholderText('请输入SK')
        self.ak_line.textChanged.connect(self.check_input1_func)
        self.sk_line.textChanged.connect(self.check_input1_func)
    def check_input1_func(self):
        if self.ak_line.text() and self.sk_line.text():
            self.start_btn.setEnabled(True)
        else:
            self.start_btn.setEnabled(False)
# 爬虫代码
class CrawlThread(QThread):
    finished_signal = pyqtSignal()
    log_signal = pyqtSignal(str)
    result_signal = pyqtSignal(str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str)
    def __init__(self, cw):
        super(CrawlThread, self).__init__(cw)
        self.Crawl_Window = cw
    # 写入txt
    def write_txt(self,path, content):
        f = open(path, 'a', encoding='utf-8')
        f.write(content)
        f.close()
    # 判断函数
    def judgement(self,a, b, c):
        if a in b:
            return c
        else:
            return 0
    # 运行函数
    def run(self):
        i = 1
        ak_o = self.Crawl_Window.ak_line.text()
        sk_o = self.Crawl_Window.sk_line.text()
        image_path = "C:\\test\\"
        txt_path = "C:\\cg21.txt"
        try:
            self.write_txt(txt_path, "照片名称,山,水,田,湖泊,草,竹,植物,花,道路,建筑,人,动物,车,指示牌,栏杆,座椅,石头,雕像" + "\n")
            gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            host = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=" + str(ak_o) + "&client_secret=" + str(sk_o)
            req = request.Request(host)
            response = request.urlopen(req, context=gcontext).read().decode('UTF-8')
            result = json.loads(response)
            #if (result):
            file_names = os.listdir(image_path)
            for file_name in file_names:
                f = open(image_path + file_name, 'rb')
                img = base64.b64encode(f.read())
                host = 'https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general'
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
                access_token = result['access_token']
                host = host + '?access_token=' + access_token
                data = {}
                data['access_token'] = access_token
                data['image'] = img
                res = requests.post(url=host, headers=headers, data=data)
                req = res.json()
                if (req['result']):
                    lists = req['result']
                    total_score_shan = total_score_shui = total_score_tian = total_score_hu = total_score_cao = total_score_zhu = total_score_zhiwu = total_score_hua = total_score_daolu = 0
                    total_score_jianzhu = total_score_ren = total_score_dongwu = total_score_che = total_score_zhishipai = total_score_langang = total_score_zuoyi = total_score_shitou = total_score_diaoxiang = 0
                    for list in lists:
                        # 1、山
                        score_shan = self.judgement("山", list['keyword'], list['score'])
                        total_score_shan = total_score_shan + score_shan
                        # 2、水
                        score_shui = self.judgement("水", list['keyword'], list['score'])
                        score_xi = self.judgement("溪", list['keyword'], list['score'])
                        total_score_shui = total_score_shui + score_shui + score_xi
                        # 3、田
                        score_tian = self.judgement("田", list['keyword'], list['score'])
                        total_score_tian = total_score_tian + score_tian
                        # 4、湖泊
                        score_hu = self.judgement("湖", list['keyword'], list['score'])
                        score_shuiku = self.judgement("水库", list['keyword'], list['score'])
                        total_score_hu = total_score_hu + score_hu + score_shuiku
                        # 5、草
                        score_cao = self.judgement("草", list['keyword'], list['score'])
                        total_score_cao = total_score_cao + score_cao
                        # 6、竹
                        score_zhu = self.judgement("竹", list['keyword'], list['score'])
                        total_score_zhu = total_score_zhu + score_zhu
                        # 7、植物
                        score_lin = self.judgement("林", list['keyword'], list['score'])
                        score_zhiwu = self.judgement("植物", list['keyword'], list['score'])
                        score_shu = self.judgement("树", list['keyword'], list['score'])
                        total_score_zhiwu = total_score_zhiwu + score_lin + score_zhiwu + score_shu
                        # 8、花
                        score_hua = self.judgement("花", list['keyword'], list['score'])
                        total_score_hua = total_score_hua + score_hua
                        # 9、道路
                        score_lu = self.judgement("路", list['keyword'], list['score'])
                        score_dao = self.judgement("道", list['keyword'], list['score'])
                        total_score_daolu = total_score_daolu + score_lu + score_dao
                        # 10、建筑
                        score_jianzhu = self.judgement("建筑", list['keyword'], list['score'])
                        score_juminglou = self.judgement("居民楼", list['keyword'], list['score'])
                        total_score_jianzhu = total_score_jianzhu + score_jianzhu + score_juminglou
                        # 11、人
                        score_ren = self.judgement("人", list['keyword'], list['score'])
                        score_hezhao = self.judgement("合照", list['keyword'], list['score'])
                        total_score_ren = total_score_ren + score_ren + score_hezhao
                        # 12、动物
                        score_niao = self.judgement("鸟", list['keyword'], list['score'])
                        score_dongwu = self.judgement("动物", list['keyword'], list['score'])
                        total_score_dongwu = total_score_dongwu + score_niao + score_dongwu
                        # 13、车
                        score_che = self.judgement("车", list['keyword'], list['score'])
                        total_score_che = total_score_che + score_che
                        # 14、指示牌
                        score_zhishipai = self.judgement("指示牌", list['keyword'], list['score'])
                        score_lubiao = self.judgement("路标", list['keyword'], list['score'])
                        total_score_zhishipai = total_score_zhishipai + score_zhishipai + score_lubiao
                        # 15、栏杆
                        score_langang = self.judgement("栏杆", list['keyword'], list['score'])
                        total_score_langang = total_score_langang + score_langang
                        # 16、座椅
                        score_yizi = self.judgement("椅", list['keyword'], list['score'])
                        score_deng = self.judgement("凳", list['keyword'], list['score'])
                        total_score_zuoyi = total_score_zuoyi + score_yizi + score_deng
                        # 17、石头
                        score_shi = self.judgement("石", list['keyword'], list['score'])
                        score_yan = self.judgement("岩", list['keyword'], list['score'])
                        total_score_shitou = total_score_shitou + score_shi + score_yan
                        # 18、雕像
                        score_diaoxiang = self.judgement("雕像", list['keyword'], list['score'])
                        total_score_diaoxiang = total_score_diaoxiang + score_diaoxiang
                    content_cg = file_name.split(".")[0] + "," + str(total_score_shan) + "," + str(total_score_shui) + "," + str(
                        total_score_tian) + "," + str(total_score_hu) + "," + str(total_score_cao) + "," + str(
                        total_score_zhu) + "," + str(total_score_zhiwu) + "," + str(total_score_hua) + "," + str(
                        total_score_daolu) + "," + str(total_score_jianzhu) + "," + str(total_score_ren) + "," + str(
                        total_score_dongwu) + "," + str(total_score_che) + "," + str(total_score_zhishipai) + "," + str(
                        total_score_langang) + "," + str(total_score_zuoyi) + "," + str(total_score_shitou) + "," + str(
                        total_score_diaoxiang) + "\n"
                    self.result_signal.emit(str(file_name.split(".")[0]), str(total_score_shan), str(total_score_shui),str(
                        total_score_tian), str(total_score_hu), str(total_score_cao), str(
                        total_score_zhu), str(total_score_zhiwu), str(total_score_hua), str(
                        total_score_daolu), str(total_score_jianzhu), str(total_score_ren), str(
                        total_score_dongwu), str(total_score_che), str(total_score_zhishipai), str(
                        total_score_langang), str(total_score_zuoyi), str(total_score_shitou), str(
                        total_score_diaoxiang))
                    self.write_txt(txt_path, content_cg)
                    self.log_signal.emit('第{:.0f}张识别完成'.format(i))
                    i = i+1
                else:
                    self.log_signal.emit('<font color="red">超出识别标签范围，无法识别！</font>')
            self.log_signal.emit('<font color="red">识别结束</font>')
        except:
            self.log_signal.emit('<font color="red">出现错误！</font>')
            self.log_signal.emit('<font color="red">请输入正确的AK或者SK，检查图片设置是否正确，并再次点击开始识别！</font>')

        self.finished_signal.emit()
# 主函数
if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())

































