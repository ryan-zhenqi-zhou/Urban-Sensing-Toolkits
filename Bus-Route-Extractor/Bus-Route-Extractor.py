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
from lxml import etree
import time
import numpy as np
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
        self.setWindowTitle('公交路线提取器软件')
        self.city_label = QLabel('城市名:', self)
        self.city_line = QLineEdit(self)
        self.cityE_label = QLabel('城市名英文拼写:', self)
        self.cityE_line = QLineEdit(self)
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
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(['name'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    def layout_init(self):
        self.koujian_h_layout.addWidget(self.city_label)
        self.koujian_h_layout.addWidget(self.city_line)
        self.koujian_h_layout.addWidget(self.cityE_label)
        self.koujian_h_layout.addWidget(self.cityE_line)
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
            self.cityE_line.setEnabled(False)
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.crawl_thread.start()
        else:
            self.log_browser.append('<font color="red">停止抓取</font>')
            self.city_line.setEnabled(True)
            self.cityE_line.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.start_btn.setEnabled(True)
            self.crawl_thread.terminate()
    def finish_slot(self):
        self.city_line.setEnabled(True)
        self.cityE_line.setEnabled(True)
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    def set_log_slot(self, new_log):
        self.log_browser.append(new_log)
    def set_table_slot(self,name):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(name))
    def lineedit1_init(self):
        self.city_line.setPlaceholderText('请输入城市名')
        self.cityE_line.setPlaceholderText('请输入城市名英文拼写')
        self.city_line.textChanged.connect(self.check_input1_func)
        self.cityE_line.textChanged.connect(self.check_input1_func)
    def check_input1_func(self):
        if self.city_line.text() and self.cityE_line.text():
            self.start_btn.setEnabled(True)
        else:
            self.start_btn.setEnabled(False)
# 抓取函数
class CrawlThread(QThread):
    finished_signal = pyqtSignal()
    log_signal = pyqtSignal(str)
    result_signal = pyqtSignal(str)
    def __init__(self, cw):
        super(CrawlThread, self).__init__(cw)
        self.Crawl_Window = cw
    # 函数1
    def get_lines(self,city,cityE):
        lst = []
        url = 'http://{}.gongjiao.com/lines_all.html'.format(cityE)
        r = requests.get(url).text
        et = etree.HTML(r)
        line = et.xpath('//div[@class="list"]//a/text()')
        for l in line:
            lst.append(l.split(city)[1].split('公交')[0])
        return lst
    # 函数2
    def get_dt(self,line, api_key, city):
        try:
            url = 'https://restapi.amap.com/v3/bus/linename?s=rsv3&extensions=all&key={}&output=json&city={}&offset=2&keywords={}&platform=JS'. \
                format(api_key, city, line)
            r = requests.get(url).text
            rt = json.loads(r)
            if rt['buslines']:
                self.log_signal.emit('========================================')
                num = len(rt['buslines'])
                for i in range(num):
                    dt = {}
                    dt['line_name'] = rt['buslines'][i]['name']
                    dt['polyline'] = rt['buslines'][i]['polyline']
                    dt['total_price'] = rt['buslines'][i]['total_price']
                    st_name = []
                    st_coords = []
                    for st in rt['buslines'][i]['busstops']:
                        st_name.append(st['name'])
                        st_coords.append(st['location'])
                    dt['station_names'] = st_name
                    dt['station_coords'] = st_coords
                    yield dt
            else:
                pass
        except:
            time.sleep(2)
            self.get_dt(line, api_key, city)
    # 函数3
    def process_dt(self,city, cityE, api_key):
        lines_list = self.get_lines(city, cityE)
        self.log_signal.emit('{}：有 {} 条公交线路'.format(city, len(lines_list)))
        time.sleep(5)
        lst = []
        for i, line in enumerate(lines_list[:]):
            self.log_signal.emit('{}/{}: {}'.format(i + 1, len(lines_list), line))
            dt = self.get_dt(line, api_key, city)
            df = pd.DataFrame(dt)
            lst.append(df)
        return lst
    # 函数4
    def conv(self,city, cityE, api_key):
        dz = self.process_dt(city, cityE, api_key)
        dv = pd.concat(dz)
        dv = dv.dropna()
        st_all = pd.DataFrame( \
            np.column_stack(( \
                np.hstack(dv['station_coords']),
                np.hstack(dv['station_names']),
            )),
            columns=['station_coords', 'station_names']
        )
        st_all = st_all.drop_duplicates()
        def st_wgs84(x):
            lng = float(x.split(',')[0])
            lat = float(x.split(',')[1])
            return self.gcj02_to_wgs84(lng, lat)
        st_all['st_coords_wgs84'] = st_all['station_coords'].apply(st_wgs84)
        dv['polyline'] = dv['polyline'].apply(lambda x: x.split(';'))
        def lines_wgs84(x):
            lst = []
            for i in x:
                lng = float(i.split(',')[0])
                lat = float(i.split(',')[1])
                lst.append(self.gcj02_to_wgs84(lng, lat))
            return lst
        dv['lines_wgs84'] = dv['polyline'].apply(lines_wgs84)
        return [st_all, dv]
    # 函数5
    def outPointAndPolyline(self,city, cityE, api_key, out_path):
        df = self.conv(city, cityE, api_key)
        # 公交站点
        df_sts = df[0].reset_index()
        w = shapefile.Writer(r'{}\{}_point.shp'.format(out_path, cityE))
        w.field('name', 'C')
        for i in range(len(df_sts)):
            w.point(df_sts['st_coords_wgs84'][i][0], df_sts['st_coords_wgs84'][i][1])
            w.record(df_sts['station_names'][i])
        w.close()
        # 公交线路
        df_ls = df[1].reset_index()
        for f in range(len(df_ls)):
            self.result_signal.emit(str(df_ls['line_name'][f]))
        w = shapefile.Writer(r'{}\{}_polyline.shp'.format(out_path, cityE))
        w.field('name', 'C')
        for i in range(len(df_ls)):
            w.line([df_ls['lines_wgs84'][i]])
            w.record(df_ls['line_name'][i])
        w.close()
    # 坐标转换函数
    def gcj02_to_wgs84(self,lng, lat):
        global x_pi, pi, a, ee
        x_pi = 3.14159265358979324 * 3000.0 / 180.0
        pi = 3.1415926535897932384626
        a = 6378245.0
        ee = 0.00669342162296594323
        if self.out_of_china(lng, lat):
            return [lng, lat]
        dlat = self._transformlat(lng - 105.0, lat - 35.0)
        dlng = self._transformlng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * pi
        magic = math.sin(radlat)
        magic = 1 - ee * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
        dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
        mglat = lat + dlat
        mglng = lng + dlng
        return [lng * 2 - mglng, lat * 2 - mglat]
    def out_of_china(self,lng, lat):
        return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)
    def _transformlat(self,lng, lat):
        ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
              0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
        ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
                math.sin(2.0 * lng * pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lat * pi) + 40.0 *
                math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
        ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
                math.sin(lat * pi / 30.0)) * 2.0 / 3.0
        return ret
    def _transformlng(self,lng, lat):
        ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
              0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
        ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
                math.sin(2.0 * lng * pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lng * pi) + 40.0 *
                math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
        ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
                math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
        return ret
    def run(self):
        city = self.Crawl_Window.city_line.text()
        cityE = self.Crawl_Window.cityE_line.text()
        out_path = './data'
        api_key = '7811cca34eeec38c223ddc7bcda10050'
        try:
            self.outPointAndPolyline(city, cityE, api_key, out_path)
            self.log_signal.emit('<font color="red">抓取结束！</font>')
        except:
            self.log_signal.emit('<font color="red">出现错误！</font>')
            self.log_signal.emit('<font color="red">请输入正确的城市名和城市名英文拼写！</font>')
        self.finished_signal.emit()
# 主函数
if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())

































