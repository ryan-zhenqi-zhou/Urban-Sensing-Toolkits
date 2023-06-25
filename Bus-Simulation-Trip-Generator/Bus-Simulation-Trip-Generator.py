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
        self.setWindowTitle('公交模拟出行生成器')

        self.fangfa_label = QLabel('使用方法：在C盘根目录下放入bus.csv文件，格式为“起点百度经度,起点百度纬度,终点百度经度,终点百度纬度”四列，输入市内公交换乘策略（0：推荐，1：少换乘，2：少步行，3：不坐地铁，4：时间短，5：地铁优先），', self)
        self.fangfa_label.setAlignment(Qt.AlignCenter)
        self.fangfa_label.setStyleSheet("QLabel{color:rgb(70,70,70,255);font-size:12px;font-weight:normal;font-family:Arial;}")
        self.fangfa1_label = QLabel('输入跨城公交换乘策略（0：时间短，1：出发早，2：价格低），输入跨城交通方式策略（0：火车优先，1：飞机优先，2：大巴优先），输入AK，点击软件界面的开始爬取后将会将结果输出在与软件相同目录下的shp文件夹中。', self)
        self.fangfa1_label.setAlignment(Qt.AlignCenter)
        self.fangfa1_label.setStyleSheet("QLabel{color:rgb(70,70,70,255);font-size:12px;font-weight:normal;font-family:Arial;}")

        self.incity_label = QLabel('市内公交换乘策略:', self)
        self.incity_line = QLineEdit(self)
        self.intercity_label = QLabel('跨城公交换乘策略:', self)
        self.intercity_line = QLineEdit(self)
        self.intercity1_label = QLabel('跨城交通方式策略:', self)
        self.intercity1_line = QLineEdit(self)
        self.ak_label = QLabel('AK:', self)
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
        self.start_btn.setText('开始爬取')
        self.stop_btn.setText('停止爬取')
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)

        self.start_btn.clicked.connect(lambda: self.btn_slot(self.start_btn))
        self.stop_btn.clicked.connect(lambda: self.btn_slot(self.stop_btn))

    def table_init(self):
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(['ori_lng_bd', 'ori_lat_bd', 'des_lng_bd', 'des_lat_bd', 'distance','duration','price'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def layout_init(self):
        self.v_layout.addWidget(self.fangfa_label)
        self.v_layout.addWidget(self.fangfa1_label)
        self.koujian_h_layout.addWidget(self.incity_label)
        self.koujian_h_layout.addWidget(self.incity_line)
        self.koujian_h_layout.addWidget(self.intercity_label)
        self.koujian_h_layout.addWidget(self.intercity_line)
        self.koujian_h_layout.addWidget(self.intercity1_label)
        self.koujian_h_layout.addWidget(self.intercity1_line)
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
            self.log_browser.append('<font color="red">开始爬取</font>')
            self.table.clearContents()
            self.table.setRowCount(0)
            self.ak_line.setEnabled(False)
            self.incity_line.setEnabled(False)
            self.intercity_line.setEnabled(False)
            self.intercity1_line.setEnabled(False)
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.crawl_thread.start()
        else:
            self.log_browser.append('<font color="red">停止爬取</font>')
            self.ak_line.setEnabled(True)
            self.incity_line.setEnabled(True)
            self.intercity_line.setEnabled(True)
            self.intercity1_line.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.start_btn.setEnabled(True)
            self.crawl_thread.terminate()

    def finish_slot(self):
        self.ak_line.setEnabled(True)
        self.incity_line.setEnabled(True)
        self.intercity_line.setEnabled(True)
        self.intercity1_line.setEnabled(True)
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def set_log_slot(self, new_log):
        self.log_browser.append(new_log)
    def set_table_slot(self,ori_lng_bd,ori_lat_bd,des_lng_bd,des_lat_bd,distance,duration,price):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(ori_lng_bd))
        self.table.setItem(row, 1, QTableWidgetItem(ori_lat_bd))
        self.table.setItem(row, 2, QTableWidgetItem(des_lng_bd))
        self.table.setItem(row, 3, QTableWidgetItem(des_lat_bd))
        self.table.setItem(row, 4, QTableWidgetItem(distance))
        self.table.setItem(row, 5, QTableWidgetItem(duration))
        self.table.setItem(row, 6, QTableWidgetItem(price))

    def lineedit1_init(self):
        self.ak_line.setPlaceholderText('请输入AK')
        self.incity_line.setPlaceholderText('请输入市内公交换乘策略')
        self.intercity_line.setPlaceholderText('请输入跨城公交换乘策略')
        self.intercity1_line.setPlaceholderText('请输入跨城交通方式策略')

        self.ak_line.textChanged.connect(self.check_input1_func)
        self.incity_line.textChanged.connect(self.check_input1_func)
        self.intercity_line.textChanged.connect(self.check_input1_func)
        self.intercity1_line.textChanged.connect(self.check_input1_func)

    def check_input1_func(self):
        if self.ak_line.text() and self.incity_line.text() and self.intercity_line.text() and self.intercity1_line.text():
            self.start_btn.setEnabled(True)
        else:
            self.start_btn.setEnabled(False)

# 爬虫代码
class CrawlThread(QThread):
    finished_signal = pyqtSignal()
    log_signal = pyqtSignal(str)
    result_signal = pyqtSignal(str,str,str,str,str,str,str)
    def __init__(self, cw):
        super(CrawlThread, self).__init__(cw)
        self.Crawl_Window = cw

    # 坐标转换
    def bd09_to_wgs84(self, bd_lon, bd_lat):
        global x_pi, pi, a, ee
        x_pi = 3.14159265358979324 * 3000.0 / 180.0
        pi = 3.1415926535897932384626
        a = 6378245.0
        ee = 0.00669342162296594323

        lon, lat = self.bd09_to_gcj02(bd_lon, bd_lat)
        return self.gcj02_to_wgs84(lon, lat)

    def bd09_to_gcj02(self, bd_lon, bd_lat):
        x = bd_lon - 0.0065
        y = bd_lat - 0.006
        z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
        theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
        gg_lng = z * math.cos(theta)
        gg_lat = z * math.sin(theta)
        return [gg_lng, gg_lat]

    def gcj02_to_wgs84(self,lng, lat):
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

    def out_of_china(self,lng, lat):
        return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)

    # 公交路径规划
    def get_data2(self, Ori, Des, ak, tactics_incity, tactics_intercity, trans_type_intercity):
        global jss2
        jss2 = []
        try:
            Ori_84_lng = self.bd09_to_wgs84(float(Ori.split(',')[0]), float(Ori.split(',')[1]))[0]
            Ori_84_lat = self.bd09_to_wgs84(float(Ori.split(',')[0]), float(Ori.split(',')[1]))[1]
            Des_84_lng = self.bd09_to_wgs84(float(Des.split(',')[0]), float(Des.split(',')[1]))[0]
            Des_84_lat = self.bd09_to_wgs84(float(Des.split(',')[0]), float(Des.split(',')[1]))[1]

            Ori1 = Ori.split(',')[1] + ',' + Ori.split(',')[0]
            Des1 = Des.split(',')[1] + ',' + Des.split(',')[0]

            url = 'http://api.map.baidu.com/direction/v2/transit?origin={}&destination={}&ak={}&tactics_incity={}&tactics_intercity={}&trans_type_intercity={}'. \
                format(Ori1, Des1, ak, tactics_incity, tactics_intercity, trans_type_intercity)

            r = requests.get(url).text

            dt = json.loads(r)
            if dt['status'] == 0:
                distance = dt['result']['routes'][0]['distance']  # 各出行的距离
                duration = dt['result']['routes'][0]['duration']  # 各出行的耗时
                price = abs(float(dt['result']['routes'][0]['price']))


                steps_lst = []
                for m in dt['result']['routes'][0]['steps']:
                    steps_lst.append(m[0]['path'])

                coords = ';'.join(steps_lst).split(';')
                path_wgs84 = [self.bd09_to_wgs84(float(i.split(',')[0]), float(i.split(',')[1])) for i in
                              coords]
                jss2 = [float(Ori.split(',')[0]), float(Ori.split(',')[1]),
                        float(Des.split(',')[0]), float(Des.split(',')[1]),
                        float(Ori_84_lng), float(Ori_84_lat),
                        float(Des_84_lng), float(Des_84_lat),
                        float(distance), float(duration), float(price), path_wgs84]
                return jss2
            else:
                pass
        except:
            pass

    # 运行函数2
    def run1(self,ak, tactics_incity, tactics_intercity, trans_type_intercity):
        p = open("C:\\bus.csv")
        date_1 = p.read().splitlines()
        a_1 = list(filter(None, date_1))
        global jss3
        jss3 = []
        y = 0
        for x in range(len(a_1)):
            Ori_1 = a_1[x].split(',')[0]
            Ori_2 = a_1[x].split(',')[1]
            Ori = Ori_1 + ',' + Ori_2
            Des_1 = a_1[x].split(',')[2]
            Des_2 = a_1[x].split(',')[3]
            Des = Des_1 + ',' + Des_2
            self.get_data2(str(Ori), str(Des), str(ak),str(tactics_incity), str(tactics_intercity),str(trans_type_intercity))
            if jss2 != []:
                jss3.append(jss2)
                y = y + 1
                self.log_signal.emit('正在爬取第{:.0f}条公交路径'.format(y))
        return jss3

    # 运行函数1
    def run(self):
        ak_o = self.Crawl_Window.ak_line.text()
        incity_o = self.Crawl_Window.incity_line.text()
        intercity_o = self.Crawl_Window.intercity_line.text()
        intercity1_o = self.Crawl_Window.intercity1_line.text()
        try:
            self.run1(str(ak_o),str(incity_o),str(intercity_o),str(intercity1_o))
            df1 = pd.DataFrame(jss3)
            df1.rename(
                columns={0: 'ori_lng_bd', 1: 'ori_lat_bd', 2: 'des_lng_bd', 3: 'des_lat_bd', 4: 'ori_lng_wgs84',
                         5: 'ori_lat_wgs84',6: 'des_lng_wgs84',7: 'des_lat_wgs84',8: 'distance',9: 'duration',10:'price',
                         11: 'path_wgs84'}, inplace=True)

            if len(df1) == 0:
                self.log_signal.emit('<font color="red">出现错误！</font>')
                self.log_signal.emit('<font color="red">请输入正确的市内公交换乘策略编码、跨城公交换乘策略编码、跨城交通方式策略编码和AK！</font>')
            else:
                self.log_signal.emit('总共生成{:.0f}条公交路径'.format(len(df1)))
            dv = df1.reset_index()
            for b in range(len(dv)):
                self.result_signal.emit(str(dv['ori_lng_bd'][b]),str(dv['ori_lat_bd'][b]),str(dv['des_lng_bd'][b]),str(dv['des_lat_bd'][b]),
                                        str(dv['distance'][b]),str(dv['duration'][b]),str(dv['price'][b]))

            # 生成shp线文件
            w = shapefile.Writer(r'.\shp\bus lines')
            w.field('ori_lng_bd', 'F', decimal=10)
            w.field('ori_lat_bd', 'F', decimal=10)
            w.field('des_lng_bd', 'F', decimal=10)
            w.field('des_lat_bd', 'F', decimal=10)
            w.field('distance', 'F')
            w.field('duration', 'F')
            w.field('price', 'F')

            for num in range(len(dv)):
                w.line([dv['path_wgs84'][num]])
                w.record(
                    dv['ori_lng_bd'][num],
                    dv['ori_lat_bd'][num],
                    dv['des_lng_bd'][num],
                    dv['des_lat_bd'][num],
                    dv['distance'][num],
                    dv['duration'][num],
                    dv['price'][num])
            w.close()
            self.log_signal.emit('<font color="red">爬取结束！</font>')
        except:
            self.log_signal.emit('<font color="red">出现错误！</font>')
            self.log_signal.emit('<font color="red">请输入正确的市内公交换乘策略编码、跨城公交换乘策略编码、跨城交通方式策略编码和AK！</font>')

        self.finished_signal.emit()

# 主函数
if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())

































