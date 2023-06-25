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
        self.setWindowTitle('坐标转换器软件')
        self.fangfa_label = QLabel('使用方法：在C盘根目录下放入coord.csv文件，格式为“编号,原坐标经度,原坐标纬度”三列，输入原坐标系名和转后坐标系名，点击软件界面的开始转换后将会将结果输出在C盘目录下的coord1.csv文件中。', self)
        self.fangfa_label.setAlignment(Qt.AlignCenter)
        self.fangfa_label.setStyleSheet("QLabel{color:rgb(70,70,70,255);font-size:15px;font-weight:normal;font-family:Arial;}")
        self.yuan_label = QLabel('原坐标系名:', self)
        self.yuan_line = QLineEdit(self)
        self.zhuan_label = QLabel('转后坐标系名:', self)
        self.zhuan_line = QLineEdit(self)
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
        self.start_btn.setText('开始转换')
        self.stop_btn.setText('停止转换')
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.start_btn.clicked.connect(lambda: self.btn_slot(self.start_btn))
        self.stop_btn.clicked.connect(lambda: self.btn_slot(self.stop_btn))
    def table_init(self):
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['id', 'ori_lng', 'ori_lat', 'tra_lng', 'tra_lat'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    def layout_init(self):
        self.v_layout.addWidget(self.fangfa_label)
        self.koujian_h_layout.addWidget(self.yuan_label)
        self.koujian_h_layout.addWidget(self.yuan_line)
        self.koujian_h_layout.addWidget(self.zhuan_label)
        self.koujian_h_layout.addWidget(self.zhuan_line)
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
            self.log_browser.append('<font color="red">开始转换</font>')
            self.table.clearContents()
            self.table.setRowCount(0)
            self.yuan_line.setEnabled(False)
            self.zhuan_line.setEnabled(False)
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.crawl_thread.start()
        else:
            self.log_browser.append('<font color="red">停止转换</font>')
            self.yuan_line.setEnabled(True)
            self.zhuan_line.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.start_btn.setEnabled(True)
            self.crawl_thread.terminate()
    def finish_slot(self):
        self.yuan_line.setEnabled(True)
        self.zhuan_line.setEnabled(True)
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    def set_log_slot(self, new_log):
        self.log_browser.append(new_log)
    def set_table_slot(self,id,ori_lng,ori_lat,tri_lng,tri_lat):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(id))
        self.table.setItem(row, 1, QTableWidgetItem(ori_lng))
        self.table.setItem(row, 2, QTableWidgetItem(ori_lat))
        self.table.setItem(row, 3, QTableWidgetItem(tri_lng))
        self.table.setItem(row, 4, QTableWidgetItem(tri_lat))
    def lineedit1_init(self):
        self.yuan_line.setPlaceholderText('请输入原坐标系名')
        self.zhuan_line.setPlaceholderText('请输入转后坐标系名')
        self.yuan_line.textChanged.connect(self.check_input1_func)
        self.zhuan_line.textChanged.connect(self.check_input1_func)
    def check_input1_func(self):
        if self.yuan_line.text() and self.zhuan_line.text():
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
    # 运行函数2
    def run1(self, yuan, zhuan):
        p = open("C:\\coord.csv")
        date_1 = p.read().splitlines()
        a_1 = list(filter(None, date_1))
        global jss4
        jss4 = []
        for x in range(len(a_1)):
            jss4.append((a_1[x].split(",")))
        global jss3
        jss3 = []
        y = 0
        if yuan == '地球坐标' and zhuan == '百度坐标':
            for x in range(len(a_1)):
                Ori_1 = a_1[x].split(',')[1]
                Ori_2 = a_1[x].split(',')[2]
                jss2 = self.wgs84_to_bd09(float(Ori_1), float(Ori_2))
                jss3.append(jss2)
                y = y + 1
                self.log_signal.emit('正在转换第{:.0f}个坐标'.format(y))
        elif yuan == '地球坐标' and zhuan == '火星坐标':
            for x in range(len(a_1)):
                Ori_1 = a_1[x].split(',')[1]
                Ori_2 = a_1[x].split(',')[2]
                jss2 = self.wgs84_to_gcj02(float(Ori_1), float(Ori_2))
                jss3.append(jss2)
                y = y + 1
                self.log_signal.emit('正在转换第{:.0f}个坐标'.format(y))
        elif yuan == '百度坐标' and zhuan == '地球坐标':
            for x in range(len(a_1)):
                Ori_1 = a_1[x].split(',')[1]
                Ori_2 = a_1[x].split(',')[2]
                jss2 = self.bd09_to_wgs84(float(Ori_1), float(Ori_2))
                jss3.append(jss2)
                y = y + 1
                self.log_signal.emit('正在转换第{:.0f}个坐标'.format(y))
        elif yuan == '百度坐标' and zhuan == '火星坐标':
            for x in range(len(a_1)):
                Ori_1 = a_1[x].split(',')[1]
                Ori_2 = a_1[x].split(',')[2]
                jss2 = self.bd09_to_gcj02(float(Ori_1), float(Ori_2))
                jss3.append(jss2)
                y = y + 1
                self.log_signal.emit('正在转换第{:.0f}个坐标'.format(y))
        elif yuan == '火星坐标' and zhuan == '地球坐标':
            for x in range(len(a_1)):
                Ori_1 = a_1[x].split(',')[1]
                Ori_2 = a_1[x].split(',')[2]
                jss2 = self.gcj02_to_wgs84(float(Ori_1), float(Ori_2))
                jss3.append(jss2)
                y = y + 1
                self.log_signal.emit('正在转换第{:.0f}个坐标'.format(y))
        elif yuan == '火星坐标' and zhuan == '百度坐标':
            for x in range(len(a_1)):
                Ori_1 = a_1[x].split(',')[1]
                Ori_2 = a_1[x].split(',')[2]
                jss2 = self.gcj02_to_bd09(float(Ori_1), float(Ori_2))
                jss3.append(jss2)
                y = y + 1
                self.log_signal.emit('正在转换第{:.0f}个坐标'.format(y))
        return jss3,jss4
    # 运行函数1
    def run(self):
        yuan = self.Crawl_Window.yuan_line.text()
        zhuan = self.Crawl_Window.zhuan_line.text()
        try:
            self.run1(str(yuan),str(zhuan))
            df1 = pd.DataFrame(jss3)
            df1.rename(
                columns={0: 'tra_lng', 1: 'tra_lat'}, inplace=True)
            df2 = pd.DataFrame(jss4)
            df2.rename(
                columns={0: 'id', 1: 'ori_lng', 2: 'ori_lat'}, inplace=True)
            df3 = df2.join(df1)
            self.log_signal.emit('总共转换{:.0f}个坐标'.format(len(df1)))
            dv = df3.reset_index()
            for b in range(len(dv)):
                self.result_signal.emit(str(dv['id'][b]),str(dv['ori_lng'][b]),str(dv['ori_lat'][b]),str(dv['tra_lng'][b]),
                                        str(dv['tra_lat'][b]))
            outputpath = 'C:\\coord1.csv'
            df1.to_csv(outputpath, sep=',', index=False, header=False)
            self.log_signal.emit('<font color="red">转换结束！</font>')
        except:
            self.log_signal.emit('<font color="red">出现错误！</font>')
            self.log_signal.emit('<font color="red">请输入正确的坐标系名或查看是否把coord.csv文件放入C盘中,文件格式是否正确！</font>')
        self.finished_signal.emit()
# 主函数
if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())

































