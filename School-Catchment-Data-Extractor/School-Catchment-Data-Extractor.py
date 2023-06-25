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
        self.setWindowTitle('学区数据提取器软件')
        self.city_label = QLabel('城市名:', self)
        self.city_line = QLineEdit(self)
        self.school_label = QLabel('学校类别:', self)
        self.school_line = QLineEdit(self)
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
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['id', 'school'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    def layout_init(self):
        self.koujian_h_layout.addWidget(self.city_label)
        self.koujian_h_layout.addWidget(self.city_line)
        self.koujian_h_layout.addWidget(self.school_label)
        self.koujian_h_layout.addWidget(self.school_line)
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
            self.school_line.setEnabled(False)
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.crawl_thread.start()
        else:
            self.log_browser.append('<font color="red">停止抓取</font>')
            self.city_line.setEnabled(True)
            self.school_line.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.start_btn.setEnabled(True)
            self.crawl_thread.terminate()
    def finish_slot(self):
        self.city_line.setEnabled(True)
        self.school_line.setEnabled(True)
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    def set_log_slot(self, new_log):
        self.log_browser.append(new_log)
    def set_table_slot(self,id,school):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(id))
        self.table.setItem(row, 1, QTableWidgetItem(school))
    def lineedit1_init(self):
        self.city_line.setPlaceholderText('请输入城市名')
        self.school_line.setPlaceholderText('请输入学校类别，小学或中学')
        self.city_line.textChanged.connect(self.check_input1_func)
        self.school_line.textChanged.connect(self.check_input1_func)
    def check_input1_func(self):
        if self.city_line.text() and self.school_line.text():
            self.start_btn.setEnabled(True)
        else:
            self.start_btn.setEnabled(False)
# 抓取函数
class CrawlThread(QThread):
    finished_signal = pyqtSignal()
    log_signal = pyqtSignal(str)
    result_signal = pyqtSignal(str,str)
    def __init__(self, cw):
        super(CrawlThread, self).__init__(cw)
        self.Crawl_Window = cw
    # 运行函数1
    def run1(self, city, school):
        url = 'http://xwf.szhome.com/School/GetFeatures'
        if school == '小学':
            data = {
                'bounds': '{top:22.401973,right:113.653778,bottom:23.236076,left:115.005037}',
                'schoolId': '3',
                'zoom': '17'
            }
        if school == '中学':
            data = {
                'bounds': '{top:22.401973,right:113.653778,bottom:23.236076,left:115.005037}',
                'schoolId': '6',
                'zoom': '17'
            }
        r = requests.post(url, data=data)
        js = r.json()
        lst = []
        for item in js['data']:
            vl = ['id', 'ctg', 'n', 'cd', 'tp']
            dt = {}
            for v in vl:
                if v in item['p'].keys():
                    dt[v] = item['p'][v]
                if v in item['g'].keys():
                    dt[v] = item['g'][v]
            lst.append(dt)
        df = pd.DataFrame(lst)
        return df
        # 运行函数2
    def run(self):
        city = self.Crawl_Window.city_line.text()
        school = self.Crawl_Window.school_line.text()
        try:
            df = self.run1(str(city), str(school))
            df_xx = df[df['tp'] == 'POLYGON']
            self.log_signal.emit('总共抓取了{:.0f}个学区'.format(len(df_xx)))
            df_xx1 = df_xx[['id', 'n']]
            df_xx1 = df_xx1.reset_index()
            for f in range(len(df_xx1)):
                self.result_signal.emit(str(df_xx1['id'][f]), str(df_xx1['n'][f]))
            df_xq = df[df['tp'] == 'POINT']
            if school == '小学':
                school1 = df_xq[df_xq['ctg'].isin([1, 3])]
            if school == '中学':
                school1 = df_xq[df_xq['ctg'].isin([2, 3])]
            # 学区面
            w = shapefile.Writer(r'xq.shp')
            w.field('id', 'F')
            w.field('school', 'C')
            dv = df_xx.reset_index()
            for i in range(len(dv)):
                w.poly(dv['cd'][i])
                w.record(dv['id'][i],
                         dv['n'][i]
                         )
            w.close()
            # 学校点
            ws = shapefile.Writer(r'school.shp')
            ws.field('id', 'F')
            ws.field('school', 'C')
            dvs = school1.reset_index()
            for i in range(len(dvs)):
                ws.point(dvs['cd'][i][0], dvs['cd'][i][1])
                ws.record(dvs['id'][i],
                          dvs['n'][i]
                          )
            ws.close()
            self.log_signal.emit('<font color="red">抓取结束！</font>')
        except:
            self.log_signal.emit('<font color="red">出现错误！</font>')
            self.log_signal.emit('<font color="red">请输入正确的城市名和学校类别！</font>')
        self.finished_signal.emit()
# 主函数
if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
