# -*- coding: utf-8 -*-
import requests
import logging
import random
import time
import hashlib
import string
import uuid
import json
import os
import sys

def LoadConfig():
    '''
    加载配置文件
    '''
    PATH = os.path.dirname(os.path.realpath(__file__))
    with open(f"{PATH}/config.json", "r",encoding="utf-8") as f:
            data = json.load(f)
            f.close()
            return data

#重要参数
Game_Cookie = LoadConfig()["Game_Cookie"]
BBS_Cookie = LoadConfig()["BBS_Cookie"]
mysSalt = 'dWCcD2FsOUXEstC5f9xubswZxEeoBOTc' #米游社2.28.1版本安卓端salt值
mysVersion = "2.28.1" #米游社版本
mysClient_type = '2' # 1:ios 2:Android

#日志输出配置
log = logger = logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S')

#游戏的签到福利header
GameHeader = {
    'Cookie': Game_Cookie,
    'User-Agent': 'Mozilla/5.0 (Linux; Android 12; vivo-s7 Build/RKQ1.211119.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Version/4.0 Chrome/103.0.5060.71 Mobile Safari/537.36 miHoYoBBS/2.28.1',
    'Referer': '',
    'DS': '',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate',
    'Origin': 'https://webstatic.mihoyo.com',
    'X-Requested-With': 'com.mihoyo.hyperion',
    'x-rpc-device_id': str(uuid.uuid3(uuid.NAMESPACE_URL, Game_Cookie)),
    'x-rpc-device_name': 'WHO CARE',
    'x-rpc-device_model': 'vivo-s7',
    'x-rpc-sys_version': '12',
    'x-rpc-channel': 'vivo',
    'x-rpc-client_type': mysClient_type,
    'x-rpc-app_version': mysVersion
}

def SleepTime():
    '''
    随机延迟时间
    '''
    if delay :
        time = random.randint(3,8)
    else:
        time = 0
    return time

def md5(text):
    '''
    md5加密
    '''
    md5 = hashlib.md5()
    md5.update(text.encode())
    return md5.hexdigest()

def randomStr(n):
    '''
    生成指定位数的随机数
    '''
    return (''.join(random.sample(string.digits + string.ascii_letters, n))).lower()

def DSGet():
    '''
    生成DS
    '''
    n = mysSalt
    i = str(int(time.time()))
    r = randomStr(6)
    c = md5("salt=" + n + "&t=" + i + "&r=" + r)
    return "{},{},{}".format(i, r, c)

def GetAllRoles():
    '''
    获取账号的全部角色信息
    '''
    url = 'https://api-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie'
    header = {
            'Cookie': Game_Cookie,
            'User-Agent': 'Mozilla/5.0 (Linux; Android 12; vivo-s7 Build/RKQ1.211119.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/103.0.5060.71 Mobile Safari/537.36 miHoYoBBS/2.28.1',
            'Referer': 'https://webstatic.mihoyo.com',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Host': 'api-takumi.mihoyo.com',
            'X-Requested-With': 'com.mihoyo.hyperion'
    }
    response = requests.get(url,headers=header)
    data = json.loads(response.text.encode('utf-8'))
    if '登录失效，请重新登录' in data["message"]:
        log.warning(data)
        sys.exit()
    return data

def ProgressBar(RealTime,Sum):
    '''
    进度条
    '''
    if LoadConfig()["Bar"]:
        print("\r", end="")
        print("实时运行进度: {}/{} ".format(RealTime,Sum), end="")
        sys.stdout.flush()

class BH3_Checkin(object):

    #api
    Referer_url     = 'https://webstatic.mihoyo.com/bbs/event/signin/bh3/index.html?bbs_auth_required=true&act_id={}&bbs_presentation_style=fullscreen&utm_source=bbs&utm_medium=mys&utm_campaign=icon'
    Sign_url        = 'https://api-takumi.mihoyo.com/event/luna/sign' #POST json
   
    #value
    Act_id          = 'e202207181446311'
    Game_biz        = 'bh3_cn'

    def header(self):
        GameHeader["DS"] = DSGet()
        GameHeader["Referer"] = self.Referer_url.format(self.Act_id)
        return GameHeader

    def bh3_sign(self,region,uid):
        sign_data = {
            "act_id" : self.Act_id,
            "region" : region,
            "uid" : uid,
            "lang" : "zh-cn"
        }
        log.info('崩坏3: 正在为舰长「{}」签到'.format(uid))
        response = requests.post(self.Sign_url,headers=self.header(),data=json.dumps(sign_data, ensure_ascii=False))
        data = json.loads(response.text.encode('utf-8'))
        time.sleep(SleepTime())
        return data

    def run(self,list):
        region = list["region"]
        uid = list["game_uid"]
        sign_data = self.bh3_sign(region,uid)

        if 'OK' in sign_data['message']:
            log.info('崩坏3: 签到成功')
        elif '已签到' in sign_data['message']:
            log.info('崩坏3: 重复签到')
        else:
            log.warning(sign_data)
            log.warning('崩坏3: 签到出现错误,请及时检查')

class YS_Checkin(object):
    
    #api
    Referer_url     = 'https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?bbs_auth_required=true&act_id={}&utm_source=bbs&utm_medium=mys&utm_campaign=icon'
    Sign_url        = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/sign' #POST json

    #value
    Act_id          = 'e202009291139501'
    Game_biz        = 'hk4e_cn'

    def header(self):
        GameHeader["DS"] = DSGet()
        GameHeader["Referer"] = self.Referer_url.format(self.Act_id)
        return GameHeader

    def ys_sign(self,region,uid):
        sign_data = {
            "act_id" : self.Act_id,
            "region" : region,
            "uid" : uid
        }
        log.info('原神: 正在为旅行者「{}」签到'.format(uid))
        response = requests.post(self.Sign_url,headers=self.header(),data=json.dumps(sign_data, ensure_ascii=False))
        data = json.loads(response.text.encode('utf-8'))
        time.sleep(SleepTime())
        return data

    def run(self,list):
        region = list["region"]
        uid = list["game_uid"]
        sign_data = self.ys_sign(region,uid)

        if 'OK' in sign_data['message']:
            log.info('原神: 签到成功')
        elif '旅行者,你已经签到过了' in sign_data['message']:
            log.info('原神: 重复签到')
        else:
            log.warning(sign_data)
            log.warning('原神: 签到出现错误,请及时检查')

class MiYouBi(object):
    #api
    Cookie_url = "https://webapi.account.mihoyo.com/Api/cookie_accountinfo_by_loginticket?login_ticket={}"
    Cookie_url2 = "https://api-takumi.mihoyo.com/auth/api/getMultiTokenByLoginTicket?login_ticket={}&token_types=3&uid={}"
    Sign_url = "https://bbs-api.mihoyo.com/apihub/sapi/signIn?gids={}"  # POST
    List_url = "https://bbs-api.mihoyo.com/post/api/getForumPostList?forum_id={}&is_good=false&is_hot=false&page_size=20&sort_type=1"
    Detail_url = "https://bbs-api.mihoyo.com/post/api/getPostFull?post_id={}"
    Share_url = "https://bbs-api.mihoyo.com/apihub/api/getShareConf?entity_id={}&entity_type=1"
    Vote_url = "https://bbs-api.mihoyo.com/apihub/sapi/upvotePost"  # POST json 

    #米游社分区
    BBS_List = [
        {
            "id": "1",
            "forumId": "1",
            "name": "崩坏3",
            "url": "https://bbs.mihoyo.com/bh3/"
        },
        {
            "id": "2",
            "forumId": "26",
            "name": "原神",
            "url": "https://bbs.mihoyo.com/ys/"
        },
        {
            "id": "3",
            "forumId": "30",
            "name": "崩坏2",
            "url": "https://bbs.mihoyo.com/bh2/"
        },
        {
            "id": "4",
            "forumId": "37",
            "name": "未定事件簿",
            "url": "https://bbs.mihoyo.com/wd/"
        },
        {
            "id": "5",
            "forumId": "34",
            "name": "大别野",
            "url": "https://bbs.mihoyo.com/dby/"
        },
        {
            "id": "6",
            "forumId": "52",
            "name": "星穹铁道",
            "url": "https://bbs.mihoyo.com/sr/"
        },
        {
            "id": "8",
            "forumId": "57",
            "name": "绝区零",
            "url": "https://bbs.mihoyo.com/zzz/"       
        }
    ]
    
    def __init__(self):
        self.LoginTicket = self.LoadCookie()["login_ticket"]
        self.stuid = self.LoadCookie()["stuid"]
        self.stoken = self.LoadCookie()["stoken"]
        self.BBS_WhiteList = LoadConfig()["BBS_WhiteList"]

        if self.LoginTicket == "" or self.stuid == "" or self.stoken == "":
            log.info("更新Cookie数据中......")
            self.MYS_Cookie()

    def header(self):
        header = {
            "Cookie": f'login_ticket={self.LoginTicket};stuid={self.stuid};stoken={self.stoken}',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 12; vivo-s7 Build/RKQ1.211119.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Version/4.0 Chrome/103.0.5060.71 Mobile Safari/537.36 miHoYoBBS/2.28.1',
            "DS": DSGet(),
            "x-rpc-client_type": mysClient_type,
            "x-rpc-app_version": mysVersion,
            "x-rpc-device_id": str(uuid.uuid3(uuid.NAMESPACE_URL, BBS_Cookie)),
            "x-rpc-device_name": 'WHO CARE',
            "x-rpc-device_model": "vivo-s7",
            "x-rpc-sys_version": "12",
            "x-rpc-channel": "vivo",
            "Referer": "https://app.mihoyo.com",
            "Host": "bbs-api.mihoyo.com",
        }
        return header

    def LoadCookie(self):
        PATH = os.path.dirname(os.path.realpath(__file__))
        with open(f"{PATH}/cookie.json", "r",encoding="utf-8") as f:
                data = json.load(f)
                f.close()
                return data

    def Write(self):
        params = self.LoadCookie()
        params["login_ticket"] = self.LoginTicket
        params["stuid"] = self.stuid
        params["stoken"] = self.stoken

        PATH = os.path.dirname(os.path.realpath(__file__))
        with open(f"{PATH}/cookie.json", "w",encoding="utf-8") as r:
            json.dump(params,r)
            r.close()

    def Cleared(self):
        params = self.LoadCookie()
        params["login_ticket"] = ""
        params["stuid"] = ""
        params["stoken"] = ""

        PATH = os.path.dirname(os.path.realpath(__file__))
        with open(f"{PATH}/cookie.json", "w",encoding="utf-8") as r:
            json.dump(params,r)
            r.close()

    def MYS_Cookie(self):
        if "login_ticket" in BBS_Cookie:
            c = BBS_Cookie.split(";")
            for i in c:
                if i.split("=")[0] == " login_ticket":
                    self.LoginTicket = i.split("=")[1]
                    break
            response = requests.get(url=self.Cookie_url.format(self.LoginTicket))
            data = json.loads(response.text.encode('utf-8'))
            if "成功" in data["data"]["msg"]:
                self.stuid = data["data"]["cookie_info"]["account_id"]
                response = requests.get(url=self.Cookie_url2.format(self.LoginTicket, self.stuid))
                data = json.loads(response.text.encode('utf-8'))
                self.stoken = data["data"]["list"][0]["token"]
                self.Write()
            else:
                log.warning(data)
                log.warning("Cookie已失效,请重新抓取Cookie")
                self.Cleared()
                sys.exit()
        else:
            log.warning("Cookie中没有'login_ticket'数据,请重新抓取Cookie!")
            self.Cleared()
            sys.exit()

    def SignIn(self):
        log.info("开始为米游社签到......")
        total = 0
        for i in self.BBS_List:
            if i["name"] in self.BBS_WhiteList:
                response = requests.post(url=self.Sign_url.format(i["id"]), headers=self.header())
                data = json.loads(response.text.encode('utf-8'))
                if "登录失效，请重新登录" not in data["message"]:
                    total = total + 1
                    log.info(i["name"] + ": " + data["message"])
                    time.sleep(SleepTime())
                else:
                    log.warning("签到失败,你的Cookie可能已过期,请重新抓取Cookie")
                    self.Cleared()
                    sys.exit()
        return total

    def GetList(self):
        List = []
        for i in self.BBS_List:
            if i["name"] in self.BBS_WhiteList:
                log.info("正在获取「{}」的帖子列表......".format(i["name"]))
                response = requests.get(url=self.List_url.format(i["forumId"]), headers=self.header())
                data = json.loads(response.text.encode('utf-8'))
                for n in range(12):
                    List.append([data["data"]["list"][n]["post"]["post_id"], data["data"]["list"][n]["post"]["subject"]])
                time.sleep(SleepTime())
        return List

    def ReadArticle(self,articleList):
        log.info("正在看帖......")
        #虽然每日米游币任务只需要看帖3篇，但为了防止程序运行过程中有人删帖，故看帖5篇以确保完成任务
        for i in range(5):
            ProgressBar(RealTime=i + 1, Sum=5)
            response = requests.get(url=self.Detail_url.format(articleList[i][0]), headers=self.header())
            data = json.loads(response.text.encode('utf-8'))
            if data["message"] != "OK":
                log.warning(data)
                log.warning("看帖失败")
            time.sleep(SleepTime())

    def UpVote(self,articleList,total):
        log.info("正在点赞......")
        log.info("为了完成所有已设定频道的任务,需要点赞{}篇帖子,请务必耐心等待".format(total * 12))
        #虽然每个频道的任务只需要点赞10篇帖子，但为了防止程序运行过程中有人删帖，故每频道点赞12篇以确保完成任务
        for i in range(total * 12):
            ProgressBar(RealTime=i + 1, Sum=total * 12)
            response = requests.post(url=self.Vote_url, headers=self.header(),
                                json={"post_id": articleList[i][0], "is_cancel": False})
            data = json.loads(response.text.encode('utf-8'))
            if data["message"] != "OK":
                log.warning(data)            
                log.warning("点赞失败")
            time.sleep(SleepTime())

    def Share(self,articleList):
        log.info("正在分享......")
        response = requests.get(url=self.Share_url.format(articleList[0][0]), headers=self.header())
        data = json.loads(response.text.encode('utf-8'))
        if data["message"] != "OK":
            log.warning(data)
            log.warning("分享失败")
    
    def run(self):
        total = self.SignIn()
        articleList = self.GetList()
        self.ReadArticle(articleList)
        self.UpVote(articleList,total)
        self.Share(articleList)

if __name__ == '__main__':
    delay = LoadConfig()["Delay"]
    Game_BlackList = LoadConfig()["Game_BlackList"]
    BH3_Enable = LoadConfig()["Enable"]["BH3"]
    YS_Enable = LoadConfig()["Enable"]["YS"]

    log.info('开始签到......')
    if delay:
        log.info('已启用随机延迟,请耐心等待')

    for list in GetAllRoles()["data"]["list"]:
        if list["game_biz"] == "bh3_cn" and list["game_uid"] not in Game_BlackList["BH3"] and BH3_Enable:
            BH3_Checkin().run(list)
        elif list["game_biz"] == "hk4e_cn" and list["game_uid"] not in Game_BlackList["YS"] and YS_Enable:
            YS_Checkin().run(list)

    if LoadConfig()["Enable"]["BBS"]:
        MiYouBi().run()
    
    log.info('任务全部完成')