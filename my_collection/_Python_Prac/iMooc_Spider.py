# prac_3.py
import requests
import re
import random
import csv
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import pymysql as pysql

class prac_3(object):
    def __init__(self) -> None:
        self.url = 'https://www.imooc.com/{}'
        self.path = 'prac_3.csv'
    def open_db(self):
        self.db = pysql.connect(host = '172.28.87.130', user='root',password='zhl010601',db = 'target_1')
        self.cursor = self.db.cursor()
    def create_table(self):
        sql = '''create table `prac_3`(
            `course` varchar(20), 
            `name` varchar(20),
            `cover_addr` varchar(20),
            `addr` varchar(20),
            `time` varchar(20),
            `price` int(4),
            `introduction` varchar(100),
            `teacher` varchar(20)
        )
        '''
        self.cursor.execute(sql)
        self.db.commit()

    def save_to_db(self,lines):
        sql = 'insert into prac_3 values(%s, %s, %s, %s, %s)'
        self.cursor.executemany(sql, lines)
        self.db.commit()

    def show_table(self):
        sql = 'select * from prac_3'
        self.cursor.execute(sql)
        print(self.cursor.fetchall())

    def close_db(self):
        self.cursor.close()
    def open_csvfile(self):
        self.f = open('prac_3.csv', 'a', newline=  '',encoding='utf-8-sig')

        self.writer = csv.writer(self.f)
    def saveto_csv(self, lines):
        self.writer.writerows(lines)
    
    def parse_freec(self):
        self.freec_url = self.url.format('course/list?page=')
        all_refs = []
        pattern4_ref = r'<a class=\"item free \".*?href=\"//(.*?)\".*?target.*?</a>'
        finder4_refs = re.compile(pattern4_ref,re.S)
        for i in range(1, 14):
        # i = 1
            tmp_url = self.freec_url + str(i)
            print(tmp_url)
            html_context = requests.get(url = tmp_url, headers= self.headers).text
            # print(html_context)
            all_refs.extend(finder4_refs.findall(html_context))
        # print(all_refs)
        pattern4_info_name = r'<h2 class=\"l\">(.*?)</h2>.*?'
        pattern4_info_teacher = r'<a href=.*?target=\"_blank\">(.*?)</a><i class="icon-imooc">.*?'
        pattern4_info_time = r'时长</span><span class=\"meta-value\">(.*?)</span>.*?'
        pattern4_info_intro = r'<div class=\"course-description course-wrap\">简介：(.*?)</div>'
        pattern4_info = pattern4_info_name + pattern4_info_teacher + pattern4_info_time + pattern4_info_intro
        print(pattern4_info)
        finder4_info = re.compile(pattern4_info, re.S)
        lines = []
        for ref in all_refs:
            res = requests.get(url= 'https://' + ref, headers= self.headers)
            res.encoding = 'utf-8'
            page_context = res.text
            # print(page_context)
            all_items = finder4_info.findall(page_context)
            # print("[All items]",all_items)
            for item in all_items:
                line = []
                line.append(item[0])
                line.append(ref)
                line.append(item[2])
                line.append(0)
                line.append(item[3])
                line.append(item[1])
                # print(line)
                lines.append(line)
        self.open_csvfile()
        self.saveto_csv(lines)

    def parse_real_proatta(self):
        self.real_proatta = self.url.format('course/list?ct=2&page=')
        all_refs = []
        pattern4_ref = r'<a class=\"item shizhan.*?href=\"//(.*?)\".*?target.*?</a>'
        finder4_refs = re.compile(pattern4_ref,re.S)
        for i in range(1, 10):
        # i = 1
            tmp_url = self.real_proatta + str(i)
            print(tmp_url)
            html_context = requests.get(url = tmp_url, headers= self.headers).text
            # print(html_context)
            all_refs.extend(finder4_refs.findall(html_context))
        # print(all_refs)
        
        pattern4_info_name = r'<div class=\"title-box.*?<h1>(.*?)</h1>.*?'
        
        pattern4_info_price = r'<div class=\"ori-price.*?￥(.*?)\n.*?</div>.*?'
        pattern4_info_time = r'时长.*?<span class=\"nodistance\">(.*?)</span>.*?'
        pattern4_info_teacher = r'<div class=\"nickname\">(.*?)</div>.*?</div>.*?'
        
        pattern4_info_intro = r'<div class=\"item.*?<div class=\"con\">(.*?)</div>'
        pattern4_info = pattern4_info_name + pattern4_info_price + pattern4_info_time  + pattern4_info_teacher + pattern4_info_intro
        # pattern4_info = pattern4_info_teacher
        print(pattern4_info)
        finder4_info = re.compile(pattern4_info, re.S)
        lines = []
        for ref in all_refs:
            res = requests.get(url= 'https://' + ref, headers= self.headers)
            res.encoding = 'utf-8'
            page_context = res.text
            soup = BeautifulSoup(page_context, 'html.parser')
            
            
            # all_nicknames = soup.find_all("div",class_ = 'nickname')
            # print("[All nick names]",all_nicknames)
            # print(page_context)
            all_items = finder4_info.findall(soup.prettify())
            # print("[All items]",all_items)
            for item in all_items:
                line = []
                line.append(item[0].replace("\n",'').replace(" ",''))
                line.append(ref)
                line.append(item[2].replace("\n",'').replace(" ",''))
                line.append(item[1].replace("\n",'').replace(" ",''))
                line.append(item[4].replace("\n",'').replace(" ",''))
                line.append(item[3].replace("\n",'').replace(" ",''))
                print(line)
                lines.append(line)
        # self.open_csvfile()
        # self.saveto_csv(lines)
 
    def parse_real_atta(self):
        self.real_atta = 'https://coding.imooc.com/'
        html_context = requests.get(url = self.real_atta, headers= self.headers)
        print(html_context)

    def get_info(self):
        self.headers = {'User-Agent': UserAgent().random, 'Cookie': 'sajssdk_2015_cross_new_user=1; IMCDNS=0; Hm_lvt_f0cfcccd7b1393990c78efdeebff3968=1678682374; imooc_uuid=8d92ce6c-a406-41ef-8f1e-4d03f201b8c3; imooc_isnew=1; imooc_isnew_ct=1678682376; march2023=1678682297000; loginstate=1; apsid=M3MzI3MGUwY2RmZjc0NThhMTQ3MDVkNDAzMjkxZWIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMTExMjc1MDcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADIzMDRmM2M4ZmRiNThkMjg2YzJiY2FjOGFkYjRjZGEwGqkOZBqpDmQ=YT; sensorsdata2015jssdkcross={"distinct_id":"11127507","first_id":"186d9443de6301-0cf0d4629b7f0d8-26031951-921600-186d9443de79e6","props":{"$latest_traffic_source_type":"直接流量","$latest_search_keyword":"未取到值_直接打开","$latest_referrer":"","$latest_utm_source":"index","$latest_utm_medium":"hot","$latest_utm_term":"top"},"identities":"eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTg2ZDk0NDNkZTYzMDEtMGNmMGQ0NjI5YjdmMGQ4LTI2MDMxOTUxLTkyMTYwMC0xODZkOTQ0M2RlNzllNiIsIiRpZGVudGl0eV9sb2dpbl9pZCI6IjExMTI3NTA3In0=","history_login_id":{"name":"$identity_login_id","value":"11127507"},"$device_id":"186d9443de6301-0cf0d4629b7f0d8-26031951-921600-186d9443de79e6"}; Hm_lvt_c1c5f01e0fc4d75fd5cbb16f2e713d56=1678682490; mc_channel=hk; mc_marking=bb86c9071ed9b7cf12612a2a85203372; cninfo=hk-bb86c9071ed9b7cf12612a2a85203372; MEIQIA_TRACK_ID=2MwddNHgtSzawdKhggM9sDcB4zu; MEIQIA_VISIT_ID=2MwddIDOolDeFv1mrtRASyz7zMR; Hm_lpvt_c1c5f01e0fc4d75fd5cbb16f2e713d56=1678683083; Hm_lpvt_f0cfcccd7b1393990c78efdeebff3968=1678683398; cvde=640ea90805476-53'.encode("utf-8").decode("latin1")}
        # print("[Free page]:")
        # self.parse_freec()
        print("[Realpro page]:")
        self.parse_real_proatta()
        # print("[Real page]:")
        # self.parse_real_atta()
    
test = prac_3()
test.get_info()

