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
# 登陆界面
USER_PWD = {
        'Ryan Zhou': '1RIBcMUslFkWfVVn'
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
        self.setWindowTitle('城市空气质量提取器软件')
        self.city_label = QLabel('城市:', self)
        self.city_line = QLineEdit(self)
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
        self.start_btn.setText('开始抓取')
        self.stop_btn.setText('停止抓取')
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.start_btn.clicked.connect(lambda: self.btn_slot(self.start_btn))
        self.stop_btn.clicked.connect(lambda: self.btn_slot(self.stop_btn))
    def table_init(self):
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(['time', 'cityname', 'stationname', 'devid', 'PM25','AQI','lng','lat'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    def layout_init(self):
        self.koujian_h_layout.addWidget(self.city_label)
        self.koujian_h_layout.addWidget(self.city_line)
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
            self.log_browser.append('<font color="red">开始抓取</font>')
            self.table.clearContents()
            self.table.setRowCount(0)
            self.city_line.setEnabled(False)
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.crawl_thread.start()
        else:
            self.log_browser.append('<font color="red">停止抓取</font>')
            self.city_line.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.start_btn.setEnabled(True)
            self.crawl_thread.terminate()
    def finish_slot(self):
        self.city_line.setEnabled(True)
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    def set_log_slot(self, new_log):
        self.log_browser.append(new_log)
    def set_table_slot(self,time,cityname,stationname,devid,PM25,AQI,lng,lat):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(time))
        self.table.setItem(row, 1, QTableWidgetItem(cityname))
        self.table.setItem(row, 2, QTableWidgetItem(stationname))
        self.table.setItem(row, 3, QTableWidgetItem(devid))
        self.table.setItem(row, 4, QTableWidgetItem(PM25))
        self.table.setItem(row, 5, QTableWidgetItem(AQI))
        self.table.setItem(row, 6, QTableWidgetItem(lng))
        self.table.setItem(row, 7, QTableWidgetItem(lat))
    def lineedit1_init(self):
        self.city_line.setPlaceholderText('请输入城市名')
        self.city_line.textChanged.connect(self.check_input1_func)
    def check_input1_func(self):
        if self.city_line.text():
            self.start_btn.setEnabled(True)
        else:
            self.start_btn.setEnabled(False)
# 转换函数
class CrawlThread(QThread):
    finished_signal = pyqtSignal()
    log_signal = pyqtSignal(str)
    result_signal = pyqtSignal(str,str,str,str,str,str,str,str)
    def __init__(self, cw):
        super(CrawlThread, self).__init__(cw)
        self.Crawl_Window = cw
    # 函数1
    def get_city(self,cityname1):
        url = 'http://service.envicloud.cn:8082/v2/air/cities/CNLHBNPOB3UXNTG3NJA4OTQYMJY5'
        r = requests.get(url)
        lst = []
        if r.json()['rdesc'] == 'Success':
            for i in r.json()['cities']:
                dt = {}
                dt['citycode'] = i['citycode']
                dt['belong'] = i['belong']
                dt['cityname'] = i['cityname']
                lst.append(dt)
            df = pd.DataFrame(lst)
            for x in range(len(df)):
                if df['cityname'][x] == cityname1:
                    return df['citycode'][x]
    # 函数2
    def get_dt(self,citycode):
        url = f'http://service.envicloud.cn:8082/v2/air/live/city/CNLHBNPOB3UXNTG3NJA4OTQYMJY5/{citycode}'
        r = requests.get(url)
        lst = []
        if r.json()['rcode'] == 200:
            citycode = r.json()['citycode']
            time = r.json()['time']
            cityname = r.json()['cityname']
            for i in r.json()['info']:
                dt = {}
                dt['citycode'] = citycode
                dt['time'] = time
                dt['cityname'] = cityname
                for item in ['PM25', 'AQI', 'stationname', 'devid']:
                    if item in i.keys():
                        dt[item] = i[item]
                    else:
                        dt[item] = '-'
                lst.append(dt)
            return pd.DataFrame(lst)
    # 函数3
    def get_st(self,citycode):
        url = f'http://service.envicloud.cn:8082/v2/air/devices/CNLHBNPOB3UXNTG3NJA4OTQYMJY5/{citycode}'
        r = requests.get(url)
        lst = []
        if r.json()['rcode'] == 200:
            citycode = r.json()['citycode']
            #         time = r.json()['time']
            cityname = r.json()['cityname']
            for i in r.json()['devices']:
                dt = {}
                dt['citycode'] = citycode
                #             dt['time'] = time
                dt['cityname'] = cityname
                for item in ['lng', 'lat', 'stationname', 'devid']:
                    if item in i.keys():
                        dt[item] = i[item]
                    else:
                        dt[item] = '-'
                lst.append(dt)
            return pd.DataFrame(lst)
    # 运行函数
    def run(self):
        cityname1 = self.Crawl_Window.city_line.text()
        try:
            citycode1 = self.get_city(str(cityname1))
            df1 = self.get_dt(citycode1)
            df2 = self.get_st(citycode1)
            dx = pd.merge(df1, df2, on='devid')
            df4 = dx[['time', 'cityname_x', 'stationname_x', 'devid', 'PM25',
                     'AQI', 'lng', 'lat']]
            self.log_signal.emit('此城市公共有{:.0f}个空气质量监测点'.format(len(df4)))
            for b in range(len(df4)):
                self.result_signal.emit(str(df4['time'][b]),str(df4['cityname_x'][b]),str(df4['stationname_x'][b]),str(df4['devid'][b]),
                                        str(df4['PM25'][b]),str(df4['AQI'][b]),str(df4['lng'][b]),str(df4['lat'][b]))
            # 生成shp文件
            w = shapefile.Writer(r'pm25.shp')
            w.field('time', 'F')
            w.field('cityname_x', 'C')
            w.field('stationname_x', 'C')
            w.field('devid', 'C')
            w.field('PM25', 'F')
            w.field('AQI', 'F')
            w.field('lng', 'F', decimal=10)
            w.field('lat', 'F', decimal=10)
            df4 = df4.reset_index()
            for i in range(len(df4)):
                w.point(float(df4['lng'][i]), float(df4['lat'][i]))
                w.record(df4['time'][i],
                         df4['cityname_x'][i],
                         df4['stationname_x'][i],
                         df4['devid'][i],
                         df4['PM25'][i],
                         df4['AQI'][i],
                         df4['lng'][i],
                         df4['lat'][i])
            w.close()
            self.log_signal.emit('<font color="red">抓取结束！</font>')
        except:
            self.log_signal.emit('<font color="red">出现错误！</font>')
            self.log_signal.emit('<font color="red">请输入正确的城市名！</font>')
        self.finished_signal.emit()
# 主函数
if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
