# 导入界面库
import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QSound
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

import res

# 登陆界面
USER_PWD = {
        'Ryan Zhou': '1RIBcMUslFkWfVVn'
    }


class Demo(QWidget):
    def __init__(self):
        super(Demo, self).__init__()
        self.resize(300, 100)
        self.setWindowTitle('登陆界面')
        self.setWindowIcon(QIcon(':res/timg.jpg'))
        self.user_label = QLabel('许可账号:', self)
        self.pwd_label = QLabel('许可密码:', self)
        self.user_line = QLineEdit(self)
        self.pwd_line = QLineEdit(self)
        self.login_button = QPushButton('登陆', self)
        self.btn_sound = QSound(':res/btn.wav', self)

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
        self.btn_sound.play()
        if USER_PWD.get(self.user_line.text()) == self.pwd_line.text():
            self.Crawl_Window.exec_()
        else:
            QMessageBox.critical(self, 'Wrong', '登陆失败！请联系453497361@qq.com')

        self.user_line.clear()
        self.pwd_line.clear()


# 主界面
class CrawlWindow(QDialog):

    def __init__(self):
        super(CrawlWindow, self).__init__()
        self.resize(1200, 800)
        self.setWindowTitle('周边步行路径提取器')
        self.setWindowIcon(QIcon(':res/timg.jpg'))

        self.zuobiao_label = QLabel('中心点坐标:', self)
        self.fenlei_label = QLabel('分类:', self)
        self.juli_label = QLabel('距离:', self)
        self.ak_label = QLabel('AK:', self)
        self.zuobiao_line = QLineEdit(self)
        self.fenlei_line = QLineEdit(self)
        self.juli_line = QLineEdit(self)
        self.ak_line = QLineEdit(self)

        self.jieshao_label = QLabel('南京林业大学 周珍琦', self)
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
        self.btn_sound = QSound(':res/btn.wav', self)
        self.finish_sound = QSound(':res/finish.wav', self)

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
        self.table.setColumnCount(14)
        self.table.setHorizontalHeaderLabels(['name', 'des_lng_bd', 'des_lat_bd', 'address', 'uid','province','city','area','des_lng_84','des_lat_84','ori_lng_bd','ori_lat_bd','distance','duration'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def layout_init(self):
        self.koujian_h_layout.addWidget(self.zuobiao_label)
        self.koujian_h_layout.addWidget(self.zuobiao_line)
        self.koujian_h_layout.addWidget(self.fenlei_label)
        self.koujian_h_layout.addWidget(self.fenlei_line)
        self.koujian_h_layout.addWidget(self.juli_label)
        self.koujian_h_layout.addWidget(self.juli_line)
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
        self.btn_sound.play()
        if btn == self.start_btn:
            self.log_browser.clear()
            self.log_browser.append('<font color="red">开始爬取</font>')
            self.table.clearContents()
            self.table.setRowCount(0)
            self.zuobiao_line.setEnabled(False)
            self.juli_line.setEnabled(False)
            self.fenlei_line.setEnabled(False)
            self.ak_line.setEnabled(False)
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.crawl_thread.start()
        else:
            self.log_browser.append('<font color="red">停止爬取</font>')
            self.zuobiao_line.setEnabled(True)
            self.juli_line.setEnabled(True)
            self.fenlei_line.setEnabled(True)
            self.ak_line.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.start_btn.setEnabled(True)
            self.crawl_thread.terminate()

    def finish_slot(self):
        self.zuobiao_line.setEnabled(True)
        self.juli_line.setEnabled(True)
        self.fenlei_line.setEnabled(True)
        self.ak_line.setEnabled(True)
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def set_log_slot(self, new_log):
        self.log_browser.append(new_log)

    def set_table_slot(self,name,des_lng_bd,des_lat_bd,address,uid,province,city,area,des_lng_84,des_lat_84,ori_lng_bd,ori_lat_bd,distance,duration):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(name))
        self.table.setItem(row, 1, QTableWidgetItem(des_lng_bd))
        self.table.setItem(row, 2, QTableWidgetItem(des_lat_bd))
        self.table.setItem(row, 3, QTableWidgetItem(address))
        self.table.setItem(row, 4, QTableWidgetItem(uid))
        self.table.setItem(row, 5, QTableWidgetItem(province))
        self.table.setItem(row, 6, QTableWidgetItem(city))
        self.table.setItem(row, 7, QTableWidgetItem(area))
        self.table.setItem(row, 8, QTableWidgetItem(des_lng_84))
        self.table.setItem(row, 9, QTableWidgetItem(des_lat_84))
        self.table.setItem(row, 10, QTableWidgetItem(ori_lng_bd))
        self.table.setItem(row, 11, QTableWidgetItem(ori_lat_bd))
        self.table.setItem(row, 12, QTableWidgetItem(distance))
        self.table.setItem(row, 13, QTableWidgetItem(duration))
        self.finish_sound.play()

    def lineedit1_init(self):
        self.zuobiao_line.setPlaceholderText('请输入百度坐标')
        self.fenlei_line.setPlaceholderText('请输入类别')
        self.juli_line.setPlaceholderText('请输入最大距离')
        self.ak_line.setPlaceholderText('请输入AK')

        self.zuobiao_line.textChanged.connect(self.check_input1_func)
        self.fenlei_line.textChanged.connect(self.check_input1_func)
        self.juli_line.textChanged.connect(self.check_input1_func)
        self.ak_line.textChanged.connect(self.check_input1_func)

    def check_input1_func(self):
        if self.zuobiao_line.text() and self.fenlei_line.text() and self.juli_line.text() and self.ak_line.text():
            self.start_btn.setEnabled(True)
        else:
            self.start_btn.setEnabled(False)

# 爬虫代码
class CrawlThread(QThread):
    finished_signal = pyqtSignal()
    log_signal = pyqtSignal(str)
    result_signal = pyqtSignal(str,str,str,str,str,str,str,str,str,str,str,str,str,str)
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

    # 圆形poi检索
    def get_data(self,loc, query, radius, ak):
        self.log_signal.emit('正在搜索附近的POI...')
        global jss1
        jss1 = []

        loc = loc.split(',')[1] + ',' + loc.split(',')[0]
        urls = []
        for i in range(0, 20):
            url = 'https://api.map.baidu.com/place/v2/search?query=' + query \
                  + '&location=' + loc + '&radius=' + radius + '&page_size=20&page_num=' + str(
                i) + '&output=json&ak=' + ak
            urls.append(url)

        for url in urls:
            try:
                js = requests.get(url).text
                data = json.loads(js)
                if 'results' in data:
                    if data['total'] != 0:
                        for item in data['results']:
                            lng_84 = item['location']['lng']
                            lat_84 = item['location']['lat']
                            Lng_84 = self.bd09_to_wgs84(lng_84, lat_84)[0]
                            Lat_84 = self.bd09_to_wgs84(lng_84, lat_84)[1]
                            jss = [item['name'], float(item['location']['lng']), float(item['location']['lat']),
                                   item['address'],
                                   item['uid'], item['province'], item['city'], item['area'], float(Lng_84),
                                   float(Lat_84)]
                            jss1.append(jss)
                    else:
                        break
                else:
                    pass
            except:
                pass

        return jss1


    # 步行路径规划
    def get_data2(self, Ori, Des, radius, ak):
        global jss2
        jss2 = []
        try:
            Ori = Ori.split(',')[1] + ',' + Ori.split(',')[0]
            Des = Des.split(',')[1] + ',' + Des.split(',')[0]
            url = 'http://api.map.baidu.com/directionlite/v1/walking?origin={}&destination={}&ak={}'. \
                format(Ori, Des, ak)
            r = requests.get(url).text
            dt = json.loads(r)
            if dt['message'] == 'ok':
                dt_dic = {}
                dt_dic['distance'] = dt['result']['routes'][0]['distance']
                dt_dic['duration'] = dt['result']['routes'][0]['duration']
                if dt_dic['distance'] <= float(radius):
                    steps_lst = []
                    for m in dt['result']['routes'][0]['steps']:
                        steps_lst.append(m['path'])
                    Ori_1 = Ori.split(',')[1] + ',' + Ori.split(',')[0]
                    Des_1 = Des.split(',')[1] + ',' + Des.split(',')[0]
                    dt_dic['Ori'] = Ori_1
                    dt_dic['Des'] = Des_1
                    coords = ';'.join(steps_lst).split(';')
                    dt_dic['path_wgs84'] = [self.bd09_to_wgs84(float(i.split(',')[0]), float(i.split(',')[1])) for i in
                                            coords]
                    jss2 = [float(dt_dic['Ori'].split(',')[0]), float(dt_dic['Ori'].split(',')[1]),
                            float(dt_dic['Des'].split(',')[0]), float(dt_dic['Des'].split(',')[1]),
                            float(dt_dic['distance']), float(dt_dic['duration']), dt_dic['path_wgs84']]
                    return jss2
                else:
                    pass
            else:
                pass
        except:
            pass

    # 运行函数2
    def run1(self,loc, query, radius, ak):
        self.get_data(loc, query, radius, ak)
        global df
        df = pd.DataFrame(jss1)
        df.rename(
            columns={0: 'name', 1: 'des_lng_bd', 2: 'des_lat_bd', 3: 'address', 4: 'uid', 5: 'province', 6: 'city',
                     7: 'area', 8: 'des_lng_84', 9: 'des_lat_84'}, inplace=True)
        global jss3
        jss3 = []
        y = 0
        for r in range(len(df)):
            Des = str(df['des_lng_bd'][r]) + ',' + str(df['des_lat_bd'][r])
            Ori = loc
            self.get_data2(Ori, Des, radius, ak)
            if jss2 != []:
                jss3.append(jss2)
                y = y + 1
                self.log_signal.emit('正在爬取第{:.0f}条步行路径'.format(y))
        return jss3

    # 运行函数1
    def run(self):
        zuobiao_o = self.Crawl_Window.zuobiao_line.text()
        fenlei_o = self.Crawl_Window.fenlei_line.text()
        juli_o = self.Crawl_Window.juli_line.text()
        ak_o = self.Crawl_Window.ak_line.text()
        try:
            self.run1(zuobiao_o, fenlei_o, juli_o, ak_o)
            df1 = pd.DataFrame(jss3)
            df1.rename(
                columns={0: 'ori_lng_bd', 1: 'ori_lat_bd', 2: 'des_lng_bd', 3: 'des_lat_bd', 4: 'distance',
                         5: 'duration',
                         6: 'path_wgs84'}, inplace=True)
            df2 = pd.merge(df, df1, how='left', on=['des_lng_bd', 'des_lat_bd'])
            df3 = df2.dropna(axis=0, how='any')
            df3 = df3.drop_duplicates(subset=['des_lng_bd', 'des_lat_bd'])
            self.log_signal.emit('去掉重复步行路径,总共生成{:.0f}条有效步行路径'.format(len(df3)))
            dv = df3.reset_index()
            for b in range(len(dv)):
                self.result_signal.emit(str(dv['name'][b]),str(dv['des_lng_bd'][b]),str(dv['des_lat_bd'][b]),str(dv['address'][b]),
                                        str(dv['uid'][b]),str(dv['province'][b]),str(dv['city'][b]),str(dv['area'][b]),
                                        str(dv['des_lng_84'][b]),str(dv['des_lat_84'][b]),str(dv['ori_lng_bd'][b]),
                                        str(dv['ori_lat_bd'][b]),str(dv['distance'][b]),str(dv['duration'][b]))
            # 生成shp点o文件
            wo = shapefile.Writer(r'.\shp\point_o')
            wo.field('name', 'C')
            wo.field('ori_lng_84', 'F', decimal=10)
            wo.field('ori_lat_84', 'F', decimal=10)

            zuobiao_o_84 = self.bd09_to_wgs84(float(zuobiao_o.split(',')[0]),float(zuobiao_o.split(',')[1]))

            wo.point(zuobiao_o_84[0], zuobiao_o_84[1])
            wo.record('O点',  # arcgis10.2版本需要.encode('gbk')
                     zuobiao_o_84[0],
                     zuobiao_o_84[1])
            wo.close()
            # 生成shp点d文件
            wd = shapefile.Writer(r'.\shp\point_d')
            wd.field('name', 'C')
            wd.field('des_lng_84', 'F', decimal=10)
            wd.field('des_lat_84', 'F', decimal=10)
            wd.field('address', 'C')

            for num in range(len(dv)):
                wd.point(dv['des_lng_84'][num],dv['des_lat_84'][num])
                wd.record(
                    dv['name'][num],
                    dv['des_lng_84'][num],
                    dv['des_lat_84'][num],
                    dv['address'][num])
            wd.close()
            # 生成shp线文件
            w = shapefile.Writer(r'.\shp\lines')
            w.field('name', 'C')
            w.field('des_lng_bd', 'F', decimal=10)
            w.field('des_lat_bd', 'F', decimal=10)
            w.field('address', 'C')
            w.field('uid', 'C')
            w.field('province', 'C')
            w.field('city', 'C')
            w.field('area', 'C')
            w.field('des_lng_84', 'F', decimal=10)
            w.field('des_lat_84', 'F', decimal=10)
            w.field('ori_lng_bd', 'F', decimal=10)
            w.field('ori_lat_bd', 'F', decimal=10)
            w.field('distance', 'F')
            w.field('duration', 'F')

            for num in range(len(dv)):
                w.line([dv['path_wgs84'][num]])
                w.record(
                    dv['name'][num],
                    dv['des_lng_bd'][num],
                    dv['des_lat_bd'][num],
                    dv['address'][num],
                    dv['uid'][num],
                    dv['province'][num],
                    dv['city'][num],
                    dv['area'][num],
                    dv['des_lng_84'][num],
                    dv['des_lat_84'][num],
                    dv['ori_lng_bd'][num],
                    dv['ori_lat_bd'][num],
                    dv['distance'][num],
                    dv['duration'][num])
            w.close()
            self.log_signal.emit('<font color="red">爬取结束！</font>')
        except:
            self.log_signal.emit('<font color="red">出现错误！</font>')
            self.log_signal.emit('<font color="red">请输入正确的中心点坐标、分类、距离、AK！</font>')

        self.finished_signal.emit()

# 主函数
if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
