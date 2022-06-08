import re
import time
import json
import datetime
import logging
import requests.cookies
from bs4 import BeautifulSoup
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5
from base64 import b64decode, b64encode
from fake_useragent import UserAgent
import logging.handlers
import random
import tempfile
import sys

# python3 main.py 13651459257 hal362421 2022-06-17 am

# 请修改此处，或者保持为空
configs = {
    'username': '',  # 记住账号请填入这里
    'password': '',  # 记住密码请填入这里
    'city_index': '9',
    'unit_id': '8',
    'dep_id': '200039160',
    'doc_id': '15248',
    'days': [],
    'times': [],
    'unit_name': '深圳市宝安区妇幼保健院',
    'dep_name': '早产儿随访门诊（门诊一楼）',
    'doctor_name': '复诊号（陈朝红主任医师）',
    'start_time': '17:00:00',
    'access_token': '',
    'mid': ''
}

if len(sys.argv) == 5:
    configs['username'] = sys.argv[1]
    configs['password'] = sys.argv[2]
    configs['days'] = [sys.argv[3]]
    configs['times'] = [sys.argv[4]]

# print("您的useragent临时文件夹为，有需要请复制它：%s" % tempfile.gettempdir())
ua = UserAgent()

PUBLIC_KEY = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDWuY4Gff8FO3BAKetyvNgGrdZM9CMNoe45SzHMXxAPWw6E2idaEjqe5uJFjVx55JW" \
             "+5LUSGO1H5MdTcgGEfh62ink/cNjRGJpR25iVDImJlLi2izNs9zrQukncnpj6NGjZu" \
             "/2z7XXfJb4XBwlrmR823hpCumSD1WiMl1FMfbVorQIDAQAB "

session = requests.Session()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# 国内热门城市数据(广州 长沙 香港 上海 武汉 重庆 北京 东莞 深圳 海外 郑州 天津 淮南)
cities = [
    {
        "name": "广州",
        "cityId": "2918"
    },
    {
        "name": "长沙",
        "cityId": "3274"
    },
    {
        "name": "香港",
        "cityId": "3314"
    },
    {
        "name": "上海",
        "cityId": "3306"
    },
    {
        "name": "武汉",
        "cityId": "3276"
    },
    {
        "name": "重庆",
        "cityId": "3316"
    },
    {
        "name": "北京",
        "cityId": "2912"
    },
    {
        "name": "东莞",
        "cityId": "2920"
    },
    {
        "name": "深圳",
        "cityId": "5"
    },
    {
        "name": "海外",
        "cityId": "6145"
    },
    {
        "name": "郑州",
        "cityId": "3242"
    },
    {
        "name": "天津",
        "cityId": "3308"
    },
    {
        "name": "淮南",
        "cityId": "3014"
    }
]
time_list = [
    {
        "name": "上午",
        "value": ["am"]
    },
    {
        "name": "下午",
        "value": ["pm"]
    },
    {
        "name": "全天",
        "value": ["am", "pm"]
    }
]


def get_headers() -> json:
    return {
        "User-Agent": ua.random,
        "Referer": "https://www.91160.com",
        "Origin": "https://www.91160.com"
    }


def login(username, password) -> bool:
    token = tokens()

    firstUrl = "https://user.91160.com/checkUser.html"
    firstData = {
        "username": username,
        "password": password,
        "type": "m",
        "token": token
    }

    url = "https://user.91160.com/login.html"
    rsa_key = RSA.importKey(b64decode(PUBLIC_KEY))
    cipher = Cipher_PKCS1_v1_5.new(rsa_key)
    username = b64encode(cipher.encrypt(username.encode())).decode()
    password = b64encode(cipher.encrypt(password.encode())).decode()
    data = {
        "username": username,
        "password": password,
        "target": "https://www.91160.com",
        "error_num": 0,
        "tokens": token
    }
    res = session.post(firstUrl, data=firstData, headers=get_headers(), allow_redirects=False)
    if res.status_code == 200:
        r = session.post(url, data=data, headers=get_headers(), allow_redirects=False)
        if r.status_code == 302:
            redirect_url = r.headers["location"]
            print(redirect_url)
            if realLogin(redirect_url):
                print("登录成功")
                return testLoginInfo()
                # return True
            else:
                return False
        else:
            print("登录失败: {}".format(check_user(data)))
            return False
    else:
        return False


def testLoginInfo() -> bool:
    url = "https://user.91160.com/order.html"
    r = session.get(url, headers=get_headers())
    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, "html.parser")
    result = soup.find(attrs={"class": "ac_user_name"}).text
    print(result)
    return True


def realLogin(redirect_url) -> bool:
    r = session.get(redirect_url, headers=get_headers(), allow_redirects=False)
    print(r)
    return r.status_code == 302


def check_user(data) -> json:
    url = "https://user.91160.com/checkUser.html"
    r = session.post(url, data=data, headers=get_headers())
    return json.loads(r.content.decode('utf-8'))


def tokens() -> str:
    url = "https://user.91160.com/login.html"
    r = session.get(url, headers=get_headers())
    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, "html.parser")
    return soup.find("input", id="tokens").attrs["value"]


def brush_ticket_new(doc_id, dep_id, days, times) -> list:
    now_date = datetime.date.today().strftime("%Y-%m-%d")
    token = configs["access_token"]
    unit_id = configs["unit_id"]
    url = "https://gate.91160.com/guahao/v1/pc/sch/doctor?user_key={}&docid={}&doc_id={}&unit_id={}&dep_id={}&date={}&days=6.html".format(token, doc_id, doc_id, unit_id, dep_id, now_date)
    r = session.get(url, headers=get_headers())
    json_obj = r.json()

    doc_sch = json_obj["sch"]["{}_{}".format(dep_id, doc_id)]
    result = []
    for time in times:
        key = "{}_{}_{}".format(dep_id, doc_id, time)
        print("key-->", key)
        if key in doc_sch:
            doc_sch_day = doc_sch[key]
            for day in days:
                print("day-->", day)
                if day in doc_sch_day:
                    result.append(doc_sch_day[day])
    print("result-->", result)
    return [element for element in result if element["y_state"] == "1"]


def get_ticket(ticket, unit_id, dep_id):
    schedule_id = ticket["schedule_id"]
    url = "https://www.91160.com/guahao/ystep1/uid-{}/depid-{}/schid-{}.html".format(
        unit_id, dep_id, schedule_id)
    print(url)
    r = session.get(url, headers=get_headers())
    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, "html.parser")

    data = {
        "sch_data": soup.find(attrs={"name": "sch_data"}).attrs["value"],
        "mid": configs["mid"],
        "hisMemId": "",
        "disease_input": "",
        "order_no": "",
        "disease_content": "",
        "accept": "1",
        "unit_id": ticket["unit_id"],
        "schedule_id": ticket["schedule_id"],
        "dep_id": ticket["dep_id"],
        "his_dep_id": "",
        "sch_date": "",
        "time_type": ticket["time_type"],
        "doctor_id": ticket["doctor_id"],
        "his_doc_id": "",
        "detlid": soup.select('#delts li')[0].attrs["val"],
        "detlid_realtime": soup.find("input", id="detlid_realtime").attrs["value"],
        "level_code": ticket["level_code"],
        "is_hot": "",
        "addressId": "3317",
        "address": "China",
        "buyinsurance": 1
    }

    url = "https://www.91160.com/guahao/ysubmit.html"
    print("准备提交++++URL: {}".format(url))
    print("提交参数++++PARAM: {}".format(data))
    r = session.post(url, data=data, headers=get_headers(), allow_redirects=False)
    if r.status_code == 302:
        redirect_url = r.headers["location"]
        print(redirect_url)
        if get_ticket_result(redirect_url):
            return True
        else:
            return False
    else:
        print(r.text)
        print("预约失败")
        return False


def set_guahao_user():
    url = "https://user.91160.com/member.html"
    r = session.get(url, headers=get_headers())
    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, "html.parser")

    # 选择挂号人
    attrs = soup.find_all(attrs={"class": "_up_mem"})
    users = []
    for attr in attrs:
        users.append(attr.attrs["truename"])

    if not configs["mid"]:
        print("=====请选择挂号人=====\n")
        for index, day in enumerate(users):
            print("{}. {}".format(index + 1, users[index]))
        print()
        while True:
            mid_index = input("请输入挂号人序号: ")
            is_number = True if re.match(r'^\d+$', mid_index) else False
            if is_number and int(mid_index) in range(1, len(users) + 1):
                configs["mid"] = attrs[int(mid_index) - 1].attrs["val"]
                break
            else:
                print("输入有误，请重新输入！")


def get_ticket_result(redirect_url) -> bool:
    if redirect_url == "https://www.91160.com":
        print("提交后跳转到首页了，抢票不成功，继续抢！")
        return False
    else:
        print("提交后没有跳转到首页，抢票成功+++++++++++成功链接：%s" % redirect_url)
        return True
    # r = session.get(redirect_url, headers=get_headers())
    # r.encoding = r.apparent_encoding
    # soup = BeautifulSoup(r.text, "html.parser")
    # result = soup.find(attrs={"class": "sucess-title"}).text
    # return result == "预约成功"


def set_user_configs():
    while True:
        if configs['username'] != '':
            print("当前用户名为：%s" % configs['username'])
        else:
            configs['username'] = input("请输入用户名: ")
        if configs['password'] != '':
            print("当前密码为：%s" % configs['password'])
        else:
            configs['password'] = input("请输入密码: ")
        if configs['username'] != '' and configs['password'] != '':
            print("登录中，请稍等...")
            if login(configs['username'], configs['password']):
                time.sleep(1)
                print("登录成功")
                break
            else:
                configs['username'] = ''
                configs['password'] = ''
                time.sleep(1)
                print("用户名或密码错误，请重新输入！")
        else:
            configs['username'] = ''
            configs['password'] = ''
            time.sleep(1)
            print("用户名/密码信息不完整，已清空，请重新输入")


def set_city_configs():
    if configs['city_index'] == "":
        print("=====请选择就医城市=====\n")
        for index, city in enumerate(cities):
            print("{}{}. {}".format(" " if index <
                                    9 else "", index + 1, city["name"]))
        print()
        while True:
            city_index = input("请输入城市序号: ")
            is_number = True if re.match(r'^\d+$', city_index) else False
            if is_number and int(city_index) in range(1, len(cities) + 1):
                configs['city_index'] = city_index
                break
            else:
                print("输入有误，请重新输入！")
    else:
        print("当前选择城市为：%s" % cities[int(configs['city_index']) - 1]["name"])


def set_hospital_configs():
    url = "https://www.91160.com/ajax/getunitbycity.html"
    data = {
        "c": cities[int(configs['city_index']) - 1]["cityId"]
    }
    r = session.post(url, headers=get_headers(), data=data)
    hospitals = json.loads(r.content.decode('utf-8'))
    if configs['unit_id'] == "":
        print("=====请选择医院=====\n")
        for index, hospital in enumerate(hospitals):
            print("{}{}. {}".format(" " if index < 9 else "",
                                    index + 1, hospital["unit_name"]))
        print()
        while True:
            hospital_index = input("请输入医院序号: ")
            is_number = True if re.match(r'^\d+$', hospital_index) else False
            if is_number and int(hospital_index) in range(1, len(hospitals) + 1):
                configs["unit_id"] = hospitals[int(
                    hospital_index) - 1]["unit_id"]
                configs["unit_name"] = hospitals[int(
                    hospital_index) - 1]["unit_name"]
                break
            else:
                print("输入有误，请重新输入！")
    else:
        print("当前选择医院为：%s（%s）" % (configs["unit_name"], configs["unit_id"]))


def set_department_configs():
    url = "https://www.91160.com/ajax/getdepbyunit.html"
    data = {
        "keyValue": configs["unit_id"]
    }
    r = session.post(url, headers=get_headers(), data=data)
    departments = r.json()
    if configs['dep_id'] == "":
        print("=====请选择科室=====\n")
        dep_id_arr = []
        dep_name = {}
        for department in departments:
            print(department["pubcat"])
            for child in department["childs"]:
                dep_id_arr.append(child["dep_id"])
                dep_name[child["dep_id"]] = child["dep_name"]
                print("    {}. {}".format(child["dep_id"], child["dep_name"]))
        print()
        while True:
            department_index = input("请输入科室序号: ")
            is_number = True if re.match(r'^\d+$', department_index) else False
            if is_number and int(department_index) in dep_id_arr:
                configs["dep_id"] = department_index
                configs["dep_name"] = dep_name[int(department_index)]
                break
            else:
                print("输入有误，请重新输入！")
    else:
        print("当前选择科室为：%s（%s）" % (configs["dep_name"], configs["dep_id"]))


def set_doctor_configs():
    now_date = datetime.date.today().strftime("%Y-%m-%d")
    unit_id = configs["unit_id"]
    dep_id = configs["dep_id"]
    access_token = configs["access_token"]
    url = "https://gate.91160.com/guahao/v1/pc/sch/dep?unit_id={}&dep_id={}&date={}&p=0&user_key={}".format(unit_id, dep_id, now_date, access_token)
    r = session.get(url, headers=get_headers())
    doctors = r.json()["data"]["doc"]
    doc_id_arr = []
    doc_name = {}
    if configs["doc_id"] == "":
        print("=====请选择医生=====\n")
        for doctor in doctors:
            doc_id_arr.append(doctor["doctor_id"])
            doc_name[doctor["doctor_id"]] = doctor["doctor_name"]
            print("{}. {}".format(doctor["doctor_id"], doctor["doctor_name"]))
        print()
        while True:
            doctor_index = input("请输入医生编号: ")
            is_number = True if re.match(r'^\d+$', doctor_index) else False
            if is_number and int(doctor_index) in doc_id_arr:
                configs["doc_id"] = doctor_index
                configs["doctor_name"] = doc_name[int(doctor_index)]
                break
            else:
                print("输入有误，请重新输入！")
    else:
        print("当前选择医生为：%s（%s）" % (configs["doctor_name"], configs["doc_id"]))


def set_day_configs():
    if not configs["days"]:
        while True:
            day_str = str(input("请输入抢号日期(格式：MM-dd 如抢6月6号的 则输入: 06-06）: "))
            is_format_correct = True if re.match(r'\d{2}-\d{2}', day_str) else False
            if is_format_correct:
                day = str(datetime.datetime.now().year) + "-" + day_str
                configs["days"] = [day]
                break
            else:
                print("格式有误，请重新输入！")


def set_times_configs():
    if not configs["times"]:
        print("=====请选择时间段=====\n")
        for index, time in enumerate(time_list):
            print("{}. {}".format(index + 1, time["name"]))
        print()
        while True:
            time_index = input("请输入时间段序号: ")
            is_number = True if re.match(r'^\d+$', time_index) else False
            if is_number and int(time_index) in range(1, len(time_list) + 1):
                configs["times"] = time_list[int(time_index) - 1]["value"]
                break
            else:
                print("输入有误，请重新输入！")


def set_user_check():
    url = "https://www.91160.com/user/check.html"
    r = session.get(url, headers=get_headers())
    access_token = r.json()["access_token"]
    configs["access_token"] = access_token
    print(access_token)


def init_data():
    set_user_configs()
    set_user_check()
    set_city_configs()
    set_hospital_configs()
    set_department_configs()
    set_doctor_configs()
    set_day_configs()
    set_times_configs()
    set_guahao_user()


def run():
    init_data()
    print(configs)
    unit_id = configs["unit_id"]
    dep_id = configs["dep_id"]
    doc_id = configs["doc_id"]
    days = configs["days"]
    times = configs["times"]
    # 刷票休眠时间，频率过高会导致刷票接口拒绝请求
    sleep_time = 15

    if not configs['start_time']:
        while True:
            input_time = input("请输入刷号时间(格式 HH:mm:ss): ")
            is_format_correct = True if re.match(r'\d{2}:\d{2}:\d{2}', input_time) else False
            h = int(input_time[:2])
            mi = int(input_time[3:5])
            s = int(input_time[6:])

            if is_format_correct and h <= 24 and mi <= 60 and s <= 60:
                configs['start_time'] = input_time
                break
            else:
                print("格式有误，请重新输入！")
    else:
        h = int(configs['start_time'][:2])
        mi = int(configs['start_time'][3:5])
        s = int(configs['start_time'][6:])

    y = datetime.datetime.now().year
    m = datetime.datetime.now().month
    d = datetime.datetime.now().day
    start_time = datetime.datetime(y, m, d, h, mi, s)

    while datetime.datetime.now() < start_time:
        print("等待{}开抢...".format(start_time))
        time.sleep(0.5)

    print("刷票开始")

    while True:
        try:
            tickets = brush_ticket_new(doc_id, dep_id, days, times)
        except Exception as e:
            print(e)
            break
        if len(tickets) > 0:
            print(tickets)
            print("刷到票了，开抢了...")
            try:
                if get_ticket(tickets[ramdomMath(len(tickets) - 1)], unit_id, dep_id):
                    break
                else:
                    continue
            except Exception as e:
                print("发生错误：=获取票的参数失败了，建议多试几次=：{}".format(e))
                continue
            break
        else:
            print("努力刷票中...")
        time.sleep(sleep_time)
    print("刷票结束")
    print("当前配置为：\n\t%s" % configs)


def ramdomMath(max):
    return random.randint(0, max)


if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        print("\n=====强制退出=====")
        print("当前配置为：\n\t%s" % configs)

        exit(0)
