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
        self.setWindowTitle('POI提取器')

        self.zuoxia_label = QLabel('左下角坐标:', self)
        self.youshang_label = QLabel('右上角坐标:', self)
        self.leibie_label = QLabel('类别:', self)
        self.ak_label = QLabel('AK:', self)
        self.zuoxia_line = QLineEdit(self)
        self.youshang_line = QLineEdit(self)
        self.leibie_line = QLineEdit(self)
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

        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(['name', 'lng_bd', 'lat_bd', 'lng_wgs84', 'lat_wgs84','address','uid','province','city','area'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def layout_init(self):

        self.koujian_h_layout.addWidget(self.zuoxia_label)
        self.koujian_h_layout.addWidget(self.zuoxia_line)
        self.koujian_h_layout.addWidget(self.youshang_label)
        self.koujian_h_layout.addWidget(self.youshang_line)
        self.koujian_h_layout.addWidget(self.leibie_label)
        self.koujian_h_layout.addWidget(self.leibie_line)
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
            self.zuoxia_line.setEnabled(False)
            self.youshang_line.setEnabled(False)
            self.leibie_line.setEnabled(False)
            self.ak_line.setEnabled(False)
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.crawl_thread.start()
        else:
            self.log_browser.append('<font color="red">停止爬取</font>')
            self.zuoxia_line.setEnabled(True)
            self.youshang_line.setEnabled(True)
            self.leibie_line.setEnabled(True)
            self.ak_line.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.start_btn.setEnabled(True)
            self.crawl_thread.terminate()

    def finish_slot(self):
        self.zuoxia_line.setEnabled(True)
        self.youshang_line.setEnabled(True)
        self.leibie_line.setEnabled(True)
        self.ak_line.setEnabled(True)
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def set_log_slot(self, new_log):
        self.log_browser.append(new_log)
    def set_table_slot(self,name,lng_bd,lat_bd,lng_wgs84,lat_wgs84,address,uid,province,city,area):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(name))
        self.table.setItem(row, 1, QTableWidgetItem(lng_bd))
        self.table.setItem(row, 2, QTableWidgetItem(lat_bd))
        self.table.setItem(row, 3, QTableWidgetItem(lng_wgs84))
        self.table.setItem(row, 4, QTableWidgetItem(lat_wgs84))
        self.table.setItem(row, 5, QTableWidgetItem(address))
        self.table.setItem(row, 6, QTableWidgetItem(uid))
        self.table.setItem(row, 7, QTableWidgetItem(province))
        self.table.setItem(row, 8, QTableWidgetItem(city))
        self.table.setItem(row, 9, QTableWidgetItem(area))

    def lineedit1_init(self):
        self.zuoxia_line.setPlaceholderText('请输入左下百度坐标')
        self.youshang_line.setPlaceholderText('请输入右上百度坐标')
        self.leibie_line.setPlaceholderText('请输入AOI分类')
        self.ak_line.setPlaceholderText('请输入AK')

        self.zuoxia_line.textChanged.connect(self.check_input1_func)
        self.youshang_line.textChanged.connect(self.check_input1_func)
        self.leibie_line.textChanged.connect(self.check_input1_func)
        self.ak_line.textChanged.connect(self.check_input1_func)

    def check_input1_func(self):
        if self.zuoxia_line.text() and self.youshang_line.text() and self.ak_line.text() and self.leibie_line.text():
            self.start_btn.setEnabled(True)
        else:
            self.start_btn.setEnabled(False)

# 爬虫代码
class CrawlThread(QThread):
    finished_signal = pyqtSignal()
    log_signal = pyqtSignal(str)
    result_signal = pyqtSignal(str,str,str,str,str,str,str,str,str,str)
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

    # 矩形POI检索
    def get_data(self,zuoxia, youshang, leibie, ak):
        self.log_signal.emit('正在搜索AOI...')
        global jss1
        jss1 = []

        zuoxia = zuoxia.split(',')[1] + ',' + zuoxia.split(',')[0]
        youshang = youshang.split(',')[1] + ',' + youshang.split(',')[0]
        urls = []
        for i in range(0, 20):
            url = 'https://api.map.baidu.com/place/v2/search?query=' + leibie \
                  + '&bounds=' + zuoxia + ',' + youshang + '&page_size=20&page_num=' + str(
                  i) + '&output=json&ak=' + ak
            urls.append(url)
        for url in urls:
            try:
                js = requests.get(url).text
                data = json.loads(js)
                if 'results' in data:
                    if data['total'] != 0:
                        for item in data['results']:
                            '''
                            'name', 'lng_bd', 'lat_bd', 'lng_wgs84', 'lat_wgs84','address','uid','province','city','area'
                            '''
                            name = item['name']
                            lng_bd = item['location']['lng']
                            lat_bd = item['location']['lat']
                            lng_wgs841 = item['location']['lng']
                            lat_wgs841 = item['location']['lat']
                            lng_wgs84 = self.bd09_to_wgs84(lng_wgs841, lat_wgs841)[0]
                            lat_wgs84 = self.bd09_to_wgs84(lng_wgs841, lat_wgs841)[1]
                            address = item['address']
                            uid = item['uid']
                            province = item['province']
                            city = item['city']
                            area = item['area']


                            jss = [name, float(lng_bd), float(lat_bd),float(lng_wgs84),float(lat_wgs84),
                                   address,
                                   uid, province, city, area]
                            jss1.append(jss)
                    else:
                        break
                else:
                    pass
            except:
                pass

        return jss1

    # AOI抓取
    def get_data2(self,uid,ak,lng_bd,lat_bd,lng_wgs84,lat_wgs84,name,r_address,r_province,r_city,r_area):
        global jss2
        jss2 = []
        try:
            url = 'https://ditu.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=ext&uid={}&c=315&ext_ver=new&l=16' \
                .format(uid)
            r = requests.get(url).text
            js = json.loads(r)
            if 'geo' in js['content'].keys():
                dt = js['content']['geo']
                coords = dt.replace(';', '').split('|')[-1].split('-')[-1].split(',')
                coords_use = [[coords[i * 2], coords[i * 2 + 1]] for i in range(int(len(coords) / 2))]

                dic = {}
                lst = []

                for i in coords_use:
                    url = 'http://api.map.baidu.com/geoconv/v1/?coords={},{}&from=6&to=5&ak={}' \
                        .format(i[0], i[1], ak)
                    r = requests.get(url).text
                    js = json.loads(r)
                    lng = js['result'][0]['x']
                    lat = js['result'][0]['y']
                    dt = [lng, lat]
                    lst.append(dt)

                dic['coords'] = lst
                dic['coords_wgs84'] = [self.bd09_to_wgs84(i[0], i[1]) for i in dic['coords']]

                jss2 = [name, float(lng_bd),
                        float(lat_bd), float(lng_wgs84),
                        float(lat_wgs84), r_address, uid, r_province, r_city, r_area, dic['coords_wgs84']]
                return jss2
            else:
                pass
        except:
            pass

    # 运行函数2
    def run1(self,zuoxia, youshang, leibie, ak):
        self.get_data(zuoxia, youshang, leibie, ak)
        global df
        df = pd.DataFrame(jss1)
        df.rename(
            columns={0: 'name', 1: 'lng_bd', 2: 'lat_bd', 3: 'lng_wgs84', 4: 'lat_wgs84',
                     5: 'address',
                     6: 'uid', 7: 'province', 8: 'city', 9: 'area'}, inplace=True)
        global jss3
        jss3 = []
        y = 0
        for r in range(len(df)):
            uid = df['uid'][r]
            name = df['name'][r]
            lng_bd = df['lng_bd'][r]
            lat_bd = df['lat_bd'][r]
            lng_wgs84 = df['lng_wgs84'][r]
            lat_wgs84 = df['lat_wgs84'][r]
            r_address = df['address'][r]
            r_province = df['province'][r]
            r_city = df['city'][r]
            r_area = df['area'][r]

            self.get_data2(uid,ak,lng_bd,lat_bd,lng_wgs84,lat_wgs84,name,r_address,r_province,r_city,r_area)
            if jss2 != []:
                jss3.append(jss2)
                y = y + 1
                self.log_signal.emit('正在爬取第{:.0f}个AOI'.format(y))
        return jss3

    # 运行函数1
    def run(self):
        zuoxia_o = self.Crawl_Window.zuoxia_line.text()
        youshang_o = self.Crawl_Window.youshang_line.text()
        leibie_o = self.Crawl_Window.leibie_line.text()
        ak_o = self.Crawl_Window.ak_line.text()
        try:
            self.run1(zuoxia_o, youshang_o, leibie_o, ak_o)
            df1 = pd.DataFrame(jss3)
            df1.rename(
                columns={0: 'name', 1: 'lng_bd', 2: 'lat_bd', 3: 'lng_wgs84', 4: 'lat_wgs84',
                         5: 'address',
                         6: 'uid', 7: 'province', 8: 'city', 9: 'area', 10:'coords_wgs84'}, inplace=True)

            df1 = df1.drop_duplicates(subset=['lng_bd', 'lat_bd'])
            if len(df1) == 0:
                self.log_signal.emit('<font color="red">总共生成0个AOI,请重新输入正确的左下点坐标、右上点坐标、分类、AK！若还是如此，此区域无此类AOI</font>')
            else:
                self.log_signal.emit('总共生成{:.0f}个有效AOI'.format(len(df1)))
            dv = df1.reset_index()
            for b in range(len(dv)):
                self.result_signal.emit(str(dv['name'][b]),str(dv['lng_bd'][b]),str(dv['lat_bd'][b]),str(dv['lng_wgs84'][b]),
                                        str(dv['lat_wgs84'][b]),str(dv['address'][b]),str(dv['uid'][b]),str(dv['province'][b]),
                                        str(dv['city'][b]),str(dv['area'][b]))
            # 生成shp文件
            wd = shapefile.Writer(r'.\shp\AOI')
            wd.field('name', 'C')
            wd.field('lng_bd', 'F', decimal=10)
            wd.field('lat_bd', 'F', decimal=10)
            wd.field('lng_wgs84', 'F', decimal=10)
            wd.field('lat_wgs84', 'F', decimal=10)
            wd.field('address', 'C')
            wd.field('uid', 'C')
            wd.field('province', 'C')
            wd.field('city', 'C')
            wd.field('area', 'C')

            for num in range(len(dv)):
                wd.poly([dv['coords_wgs84'][num]])
                wd.record(
                    dv['name'][num],
                    dv['lng_bd'][num],
                    dv['lat_bd'][num],
                    dv['lng_wgs84'][num],
                    dv['lat_wgs84'][num],
                    dv['address'][num],
                    dv['uid'][num],
                    dv['province'][num],
                    dv['city'][num],
                    dv['area'][num])

            wd.close()

            self.log_signal.emit('<font color="red">爬取结束！</font>')
        except:
            self.log_signal.emit('<font color="red">出现错误！</font>')
            self.log_signal.emit('<font color="red">请输入正确的左下点坐标、右上点坐标、分类、AK！</font>')

        self.finished_signal.emit()

# 主函数
if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())










