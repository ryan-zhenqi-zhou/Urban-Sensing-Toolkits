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
import time
import schedule
import random
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
        self.setWindowTitle('交通路况提取器软件')
        self.fangfa_label = QLabel('使用方法：输入抓取范围和AK值，点击软件界面的开始抓取后将会将结果输出在软件相同目录下的shp文件夹中。', self)
        self.fangfa_label.setAlignment(Qt.AlignCenter)
        self.fangfa_label.setStyleSheet("QLabel{color:rgb(70,70,70,255);font-size:15px;font-weight:normal;font-family:Arial;}")
        self.fanwei_label = QLabel('抓取范围:', self)
        self.fanwei_line = QLineEdit(self)
        self.ak_label = QLabel('ak:', self)
        self.ak_line = QLineEdit(self)
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
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['name', 'status', 'direction', 'angle', 'speed'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    def layout_init(self):
        self.v_layout.addWidget(self.fangfa_label)
        self.koujian_h_layout.addWidget(self.fanwei_label)
        self.koujian_h_layout.addWidget(self.fanwei_line)
        self.koujian_h_layout.addWidget(self.ak_label)
        self.koujian_h_layout.addWidget(self.ak_line)
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
            self.fanwei_line.setEnabled(False)
            self.ak_line.setEnabled(False)
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.crawl_thread.start()
        else:
            self.log_browser.append('<font color="red">停止抓取</font>')
            self.fanwei_line.setEnabled(True)
            self.ak_line.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.start_btn.setEnabled(True)
            self.crawl_thread.terminate()
    def finish_slot(self):
        self.fanwei_line.setEnabled(True)
        self.ak_line.setEnabled(True)
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    def set_log_slot(self, new_log):
        self.log_browser.append(new_log)
    def set_table_slot(self,name,status,direction,angle,speed):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(name))
        self.table.setItem(row, 1, QTableWidgetItem(status))
        self.table.setItem(row, 2, QTableWidgetItem(direction))
        self.table.setItem(row, 3, QTableWidgetItem(angle))
        self.table.setItem(row, 4, QTableWidgetItem(speed))
    def lineedit1_init(self):
        self.fanwei_line.setPlaceholderText('请输入左下坐标，右上坐标，两者皆为火星坐标系')
        self.ak_line.setPlaceholderText('请输入ak值')
        self.fanwei_line.textChanged.connect(self.check_input1_func)
        self.ak_line.textChanged.connect(self.check_input1_func)
    def check_input1_func(self):
        if self.fanwei_line.text() and self.ak_line.text():
            self.start_btn.setEnabled(True)
        else:
            self.start_btn.setEnabled(False)
# 转换函数
class CrawlThread(QThread):
    finished_signal = pyqtSignal()
    log_signal = pyqtSignal(str)
    result_signal = pyqtSignal(str,str,str,str,str)
    def __init__(self, cw):
        super(CrawlThread, self).__init__(cw)
        self.Crawl_Window = cw
    # 坐标转换
    def gcj02_to_bd09(self,lng, lat):
        global x_pi, pi, a, ee
        x_pi = 3.14159265358979324 * 3000.0 / 180.0
        pi = 3.1415926535897932384626
        a = 6378245.0
        ee = 0.00669342162296594323
        z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
        theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
        bd_lng = z * math.cos(theta) + 0.0065
        bd_lat = z * math.sin(theta) + 0.006
        return [bd_lng, bd_lat]
    def bd09_to_gcj02(self,bd_lon, bd_lat):
        global x_pi, pi, a, ee
        x_pi = 3.14159265358979324 * 3000.0 / 180.0
        pi = 3.1415926535897932384626
        a = 6378245.0
        ee = 0.00669342162296594323
        x = bd_lon - 0.0065
        y = bd_lat - 0.006
        z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
        theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
        gg_lng = z * math.cos(theta)
        gg_lat = z * math.sin(theta)
        return [gg_lng, gg_lat]
    def wgs84_to_gcj02(self,lng, lat):
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
        return [mglng, mglat]
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
    def bd09_to_wgs84(self, bd_lon, bd_lat):
        global x_pi, pi, a, ee
        x_pi = 3.14159265358979324 * 3000.0 / 180.0
        pi = 3.1415926535897932384626
        a = 6378245.0
        ee = 0.00669342162296594323
        lon, lat = self.bd09_to_gcj02(bd_lon, bd_lat)
        return self.gcj02_to_wgs84(lon, lat)
    def wgs84_to_bd09(self, lon, lat):
        global x_pi, pi, a, ee
        x_pi = 3.14159265358979324 * 3000.0 / 180.0
        pi = 3.1415926535897932384626
        a = 6378245.0
        ee = 0.00669342162296594323
        lon, lat = self.wgs84_to_gcj02(lon, lat)
        return self.gcj02_to_bd09(lon, lat)
    def _transformlat(self, lng, lat):
        global x_pi, pi, a, ee
        x_pi = 3.14159265358979324 * 3000.0 / 180.0
        pi = 3.1415926535897932384626
        a = 6378245.0
        ee = 0.00669342162296594323
        ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
              0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
        ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
                math.sin(2.0 * lng * pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lat * pi) + 40.0 *
                math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
        ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
                math.sin(lat * pi / 30.0)) * 2.0 / 3.0
        return ret
    def _transformlng(self, lng, lat):
        global x_pi, pi, a, ee
        x_pi = 3.14159265358979324 * 3000.0 / 180.0
        pi = 3.1415926535897932384626
        a = 6378245.0
        ee = 0.00669342162296594323
        ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
              0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
        ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
                math.sin(2.0 * lng * pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lng * pi) + 40.0 *
                math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
        ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
                math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
        return ret
    def out_of_china(self, lng, lat):
        global x_pi, pi, a, ee
        x_pi = 3.14159265358979324 * 3000.0 / 180.0
        pi = 3.1415926535897932384626
        a = 6378245.0
        ee = 0.00669342162296594323
        return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)
    # 抓取网格1
    def get_lst(self, coords):
        global jss1
        jss1 = []
        try:
            url = 'http://restapi.amap.com/v3/traffic/status/rectangle?rectangle={}&key={}&extensions=all'. \
                format(coords, api_key)
            r = requests.get(url).text
            sjson = json.loads(r)
            if sjson['info'] == 'OK':
                if len(sjson['trafficinfo']['roads']) != 0:
                    dic = {}
                    dic['coords'] = coords
                    jss1 = [dic]
                    return jss1
            else:
                pass
        except:
            self.get_lst(coords)
    def lng_lat(self, loc_all, div):
        lng_sw = float(loc_all.split(',')[0])
        lng_ne = float(loc_all.split(',')[2])
        lat_sw = float(loc_all.split(',')[1])
        lat_ne = float(loc_all.split(',')[3])
        lng_list = [str(lng_ne)]
        while lng_ne - lng_sw >= 0:
            m = lng_ne - div
            lng_ne = lng_ne - div
            lng_list.append('%.2f' % m)
        lat_list = [str(lat_ne)]
        while lat_ne - lat_sw >= 0:
            m = lat_ne - div
            lat_ne = lat_ne - div
            lat_list.append('%.2f' % m)
        return [sorted(lng_list), lat_list]
    def get_coords(self, divs):
        lng = divs[0]
        lat = divs[1]
        dt = ['{},{}'.format(lng[i2], lat[i]) for i in range(0, len(lat)) for i2 in range(0, len(lng))]
        lst = []
        for i in range(len(lat)):
            lst.append(dt[i * len(lng):(i + 1) * len(lng)])
        ls = []
        for n in range(0, len(lat) - 1):
            for i in range(0, len(lng) - 1):
                ls.append([lst[n + 1][i], lst[n][i + 1]])
        return ls
    # 抓取网格2
    def run1(self):
        global jss2
        jss2 = []
        div = 0.02
        divds = self.lng_lat(loc_all, div)
        coord_divs = self.get_coords(divds)
        for i, coords in enumerate(coord_divs[:]):
            cds = '{};{}'.format(coords[0], coords[1])
            self.get_lst(cds)
            jss2.append(jss1)
    # 抓取路况1
    def get_dt(self, coords, api_key):
        global jss3
        jss3 = []
        try:
            url = 'http://restapi.amap.com/v3/traffic/status/rectangle?rectangle={}&key={}&extensions=all'. \
                format(coords, api_key)
            r = requests.get(url).text
            sjson = json.loads(r)
            if sjson['info'] == "OK":
                if 'trafficinfo' in sjson:
                    if len(sjson['trafficinfo']['roads']) != 0:
                        rds = sjson['trafficinfo']['roads']
                        for rd in rds:
                            dt = {}
                            keys = ['name', 'status', 'direction', 'angle', 'speed', 'lcodes', 'polyline']
                            for key in keys:
                                if key in rd:
                                    dt[key] = rd[key]
                                else:
                                    dt[key] = None
                            if 'polyline' in rd:
                                dt['line_wgs84'] = [self.gcj02_to_wgs84(float(x.split(',')[0]), float(x.split(',')[1])) for x
                                                    in dt['polyline'].split(';')]
                            else:
                                dt['line_wgs84'] = None
                            dt['record_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                            jss3 = [dt['name'], dt['status'], dt['direction'], dt['angle'], dt['speed'],
                                    dt['line_wgs84']]
                            return jss3
                    else:
                        print('{}--->no data 1'.format(coords))
                else:
                    print('{}--->no data 2'.format(coords))

            elif sjson['info'] == 'DAILY_QUERY_OVER_LIMIT':
                with open('./log.txt', 'a') as fl:
                    fl.write(url + '\n')
                return 'NO'
            else:
                pass
        except:
            with open('./log.txt', 'a') as fl:
                fl.write(url + '\n')
    # 抓取路况2
    def run2(self):
        global jss4
        w = 0
        jss4 = []
        tb_name = time.strftime("%Y-%m-%d-%H-%M", time.localtime())
        api_key = random.choice(key_lst)
        data = jss2
        for e in range(len(data)):
            dm = self.get_dt(data[e][0]['coords'], api_key)
            jss4.append(jss3)
            w = w + 1
            self.log_signal.emit('正在抓取第{:.0f}条交通路况'.format(w))
            if dm == 'NO':
                api_key = random.choice(key_lst)
            else:
                pass
        df = pd.DataFrame(jss4)
        df.rename(
            columns={0: 'name', 1: 'status', 2: 'direction', 3: 'angle', 4: 'speed',
                     5: 'line_wgs84'}, inplace=True)
        for b in range(len(df)):
            self.result_signal.emit(str(df['name'][b]), str(df['status'][b]), str(df['direction'][b]),
                                    str(df['angle'][b]),
                                    str(df['speed'][b]))
        w = shapefile.Writer(r'.\shp\traffic{}lines'.format(tb_name))
        w.field('name', 'C')
        w.field('status', 'F')
        w.field('direction', 'C')
        w.field('angle', 'F')
        w.field('speed', 'F')
        df = df.drop_duplicates(subset='direction')
        dv = df.reset_index()
        for i in range(len(dv)):
            w.line([dv['line_wgs84'][i]])
            w.record(
                dv['name'][i],
                dv['status'][i],
                dv['direction'][i],
                dv['angle'][i],
                dv['speed'][i],
            )
        w.close()
    # 主运行函数
    def run(self):
        fanwei = self.Crawl_Window.fanwei_line.text()
        ak = self.Crawl_Window.ak_line.text()
        try:
            global key_lst
            global api_key
            global loc_all
            api_key = str(ak)
            key_lst = [str(ak)]
            loc_all = str(fanwei)
            self.run1()
            self.run2()
            self.log_signal.emit('<font color="red">结束抓取</font>')
        except:
            self.log_signal.emit('<font color="red">出现错误！</font>')
            self.log_signal.emit('<font color="red">请输入正确的坐标范围和AK值！</font>')

        self.finished_signal.emit()
# 主函数
if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())

































