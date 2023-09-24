import json
import os
from pyDes import des, ECB, PAD_PKCS5
import binascii
import requests
import time, datetime

headers = {
    'standardUA': '{"channelName": "dmkj_Android", "countryCode": "CN", "createTime": 1604663529774, "device": "HUAWEI vmos","hardware": "vphw71", "modifyTime": 1604663529774, "operator": "%E4%B8%AD%E5%9B%BD%E7%A7%BB%E5%8A%A8","screenResolution": "1080-2115", "startTime": 1605884705024, "sysVersion": "Android 25 7.1.2","system": "android", "uuid": "12:34:56:31:97:80", "version": "4.3.6"}',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Content-Length': '309',
    'Host': 'appdmkj.5idream.net',
    'Connection': 'Keep-Alive',
    'Accept-Encoding': 'gzip',
    'User-Agent': 'okhttp/3.11.0',
}


def Apply(account, pwd):
    """
    账号登陆,返回uid和token
    account  登陆账号
    pwd      加密后的密码
    :param account:
    :param pwd:
    :return:
    """
    pwd_ = get_pwd(pwd)
    url = 'https://appdmkj.5idream.net/v2/login/phone'
    data = {
        'pwd': pwd_,
        'account': account,
        'version': '4.3.6'
    }

    response = requests.post(url=url, headers=headers, data=data).json()
    response.update(account=account, pwd=pwd)
    response1 = json.dumps(response)
    with open('token', mode='w', encoding='utf-8') as f:
        f.write(response1)

    return response


def get_time(accounts_data, id):
    """
    获取活动开始时间
    :param accounts_data:
    :param id:
    :return:
    """
    url = 'https://appdmkj.5idream.net/v2/activity/detail'
    token = accounts_data['token']
    uid = accounts_data['uid']
    data_get_time = {
        'uid': uid,  # 登陆接口获取
        'token': token,  # 登陆接口获取
        'activityId': int(id),  # 活动ID
        'version': '4.3.6',
    }

    set_data = requests.post(url=url, headers=headers, data=data_get_time).json()
    time_ = set_data['data']['joindate'].split('-')[0]
    time_data = [time_[0:4], time_[5:7], time_[8:10], time_[11:13], time_[14:16], set_data['data']['activityName']]
    print(set_data['data']['activityName'])
    return time_data


def get_activit(accounts_data):
    """
    获取可以报名的活动
    uid     每个账号不同的uid
    token   账号的token
    :param accounts_data
    :return:
    """
    activitys = []
    url = 'https://appdmkj.5idream.net/v2/activity/activities'
    token = accounts_data['token']
    uid = accounts_data['uid']
    data = {
        'joinStartTime': '',
        'token': token,  # 登陆接口获取
        'startTime': '',
        'endTime': '',
        'joinFlag': '1',
        'collegeFlag': '',
        'catalogId': '',
        'joinEndTime': '',
        'specialFlag': '',
        'status': '',
        'keyword': '',
        'version': '4.3.6',
        'uid': uid,  # 登陆接口获取
        'sort': '',
        'page': '1',
        'catalogId2': '',
        'level': '',
    }
    response = requests.post(url=url, headers=headers, data=data).json()
    lists_data = response['data']['list']
    for data_ in lists_data:
        activityId = data_['activityId']
        name = data_['name']
        statusText = data_['statusText']
        activity = {'activityId': activityId, 'name': name, 'statusText': statusText}
        activitys.append(activity)
    return activitys


def main(passwd, id):
    """
    提交报名函数
    :param passwd:
    :param id:
    :return:
    """
    while True:
        info = [{"conent": "", "content": "", "fullid": "79857", "key": 1, "notList": "false", "notNull": "false",
                 "system": 0,
                 "title": "姓名"}]

        data1 = {
            'uid': passwd['uid'],  # 登陆接口获取
            'token': str(passwd['token']),  # 登陆接口获取
            'remark': '',
            'data': str(info),  # 活动报名参数
            'activityId': id,  # 活动ID
            'version': '4.3.6',
        }
        response1 = requests.post(url='https://appdmkj.5idream.net/v2/signup/submit', data=data1,
                                  headers=headers).json()
        print(response1)
        try:
            if response1['msg'] == '此活动你已经报名,不能重复报名':
                break
        except KeyError:
            ...


def get_pwd(s):
    """
    获取密码加密结果
    :param s:
    :return:
    """
    KEY = '51434574'
    secret_key = KEY
    k = des(secret_key, ECB, pad=None, padmode=PAD_PKCS5)
    en = k.encrypt(s, padmode=PAD_PKCS5)
    return binascii.b2a_hex(en).upper().decode('utf-8')


if __name__ == '__main__':
    print('欢迎使用,软件抢的效率取决于你的网速!')
    if os.path.exists('token'):
        with open('token', mode='r', encoding='utf-8') as f:
            datas = f.readlines()[0]
            data_s = json.loads(datas)
            account = data_s['account']
            pwd = data_s['pwd']
    else:
        account = input('请输入你的账号(手机号):')
        pwd = input('请输入你的密码:')
    passwd = Apply(account=account, pwd=pwd)
    passwd1 = {}
    huodong_id = get_activit(passwd['data'])
    print(f"{passwd['data']['name']} 你好,你可报名的活动有:\n序号\t\t活动ID\t\t活动名称\t\t活动状态")
    i = 1
    for activity in huodong_id:  # 遍历活动输出
        num = i
        activityId = activity['activityId']
        name = activity['name']
        statusText = activity['statusText']
        i += 1
        print(f"{num}\t\t{activityId}\t\t{name}\t\t{statusText}")

    number = int(input('请输入你准备抢的活动的序号(如果没有你要抢的活动请输入0):'))
    ID = huodong_id[number - 1]['activityId']
    if number == 0:
        ID = input('请输入你要抢的活动的ID,ID在活动详情页可以查看: ')
    time_sleep = input('请输入你想要的延迟(推荐0.1-0.5)')
    passwd1['token'] = passwd['data']['token']
    passwd1['uid'] = passwd['data']['uid']
    time_ = get_time(passwd['data'], ID)
    startTime = datetime.datetime(int(time_[0]), int(time_[1]), int(time_[2]), int(time_[3]), int(time_[4]), 00)
    print(f'登陆成功,活动名为{time_[5]}\n开抢时间为{startTime}\n等待中...')
    print('延迟为:', float(time_sleep))
    while datetime.datetime.now() < startTime:
        time.sleep(float(time_sleep))
    print('开始抢...')

    main(passwd1, ID)
    input('按回车退出程序')
