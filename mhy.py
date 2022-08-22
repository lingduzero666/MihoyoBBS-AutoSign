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
Salt_BBS = 'ZSHlXeQUBis52qD1kEgKt5lUYed4b7Bb' #米游社签到salt
Salt_Discuss = 't0qEgfub6cvueAPgR5m9aQWWVciEer7v' #米游社讨论区专用salt
mysVersion = "2.35.2" #米游社版本
mysClient_type = '2' # 1:ios 2:Android

#日志输出配置
log = logger = logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S')

#游戏的签到福利header
def GameHeader(Referer="https://webstatic.mihoyo.com/"): #此referer为默认值
    headers = {
        'Cookie': Game_Cookie,
        'User-Agent': 'Mozilla/5.0 (Linux; Android 12; vivo-s7 Build/RKQ1.211119.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Version/4.0 Chrome/103.0.5060.71 Mobile Safari/537.36 miHoYoBBS/2.28.1',
        'Referer': Referer,
        'DS': DS_BBS(),
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate',
        'Origin': 'https://webstatic.mihoyo.com',
        'X-Requested-With': 'com.mihoyo.hyperion',
        'x-rpc-device_id': str(uuid.uuid3(uuid.NAMESPACE_URL, Game_Cookie)),
        'x-rpc-device_name': 'vivo s7',
        'x-rpc-device_model': 'vivo-s7',
        'x-rpc-sys_version': '12',
        'x-rpc-channel': 'vivo',
        'x-rpc-client_type': mysClient_type,
        'x-rpc-app_version': mysVersion
    }
    return headers

def SleepTime():
    '''
    随机延迟时间
    '''
    if delay :
        time.sleep(random.randint(3,10))
      
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

def DS_BBS():
    '''
    生成米游社DS
    '''
    n = Salt_BBS
    i = str(int(time.time()))
    r = randomStr(6)
    c = md5("salt=" + n + "&t=" + i + "&r=" + r)
    return "{},{},{}".format(i, r, c)

def DS_discuss(gid):
    '''
    生成讨论区DS
    '''
    n = Salt_Discuss
    i = str(int(time.time()))
    r = str(random.randint(100001, 200000))
    b = json.dumps({"gids": gid})
    c = md5("salt=" + n + "&t=" + i + "&r=" + r + "&b=" + b + "&q=") #q值为空
    return "{},{},{}".format(i, r, c)

def GetAllRoles():
    '''
    获取账号的全部角色信息
    '''
    url = 'https://api-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie'

    response = requests.get(url,headers=GameHeader())
    data = json.loads(response.text.encode('utf-8'))
    if '登录失效，请重新登录' in data["message"]:
        log.warning(data)
        sys.exit()
    SleepTime()
    return data

class BH3_Checkin(object):

    #api
    Referer_url     = 'https://webstatic.mihoyo.com/bbs/event/signin/bh3/index.html?bbs_auth_required=true&act_id={}&bbs_presentation_style=fullscreen&utm_source=bbs&utm_medium=mys&utm_campaign=icon'
    Sign_url        = 'https://api-takumi.mihoyo.com/event/luna/sign' #POST json
    Check_url       = 'https://api-takumi.mihoyo.com/event/luna/info?lang=zh-cn&act_id={}&region={}&uid={}'

    #value
    Act_id          = 'e202207181446311'
    Game_biz        = 'bh3_cn'

    def bh3_sign(self,region,uid):
        sign_data = {
            "act_id" : self.Act_id,
            "region" : region,
            "uid" : uid,
            "lang" : "zh-cn"
        }
        log.info('崩坏3: 正在为舰长「{}」签到'.format(uid))
        response = requests.post(url=self.Sign_url, headers=GameHeader(Referer=self.Referer_url.format(self.Act_id)), data=json.dumps(sign_data, ensure_ascii=False))
        data = json.loads(response.text.encode('utf-8'))
        SleepTime()
        return data

    def run(self,list):
        region = list["region"]
        uid = list["game_uid"]

        for i in range(3):
            sign_data = self.bh3_sign(region,uid) #签到并返回数据
            try:
                #从专门的api检查签到结果
                response = requests.get(url=self.Check_url.format(self.Act_id,region,uid), headers=GameHeader())
                data = json.loads(response.text.encode('utf-8'))
                if "OK" in sign_data["message"]:
                    if data["data"]["is_sign"]: # "is_sign" 为布尔值
                        log.info('崩坏3: 签到成功')
                        break
                    else:
                        log.info('崩坏3: 第 {} 次请求成功但并未签上'.format(i + 1))
                elif "已签到" in sign_data["message"]:
                    log.info('崩坏3: 重复签到')
                    break
                else:
                    log.warning(sign_data)
                    log.warning('崩坏3: 签到出现错误,请及时检查')
                    break
            except:
                #直接输出签到api返回的签到结果
                log.warning(data)
                log.warning("未能从检查api得到签到结果,下面为签到api返回的结果")
                if "OK" in sign_data["message"]:
                    log.info('崩坏3: 签到成功')
                elif '已签到' in sign_data["message"]:
                    log.info('崩坏3: 重复签到')
                else:
                    log.warning(sign_data)
                    log.warning('崩坏3: 签到出现错误,请及时检查')
                break

class YS_Checkin(object):
    
    #api
    Referer_url     = 'https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?bbs_auth_required=true&act_id={}&utm_source=bbs&utm_medium=mys&utm_campaign=icon'
    Sign_url        = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/sign' #POST json
    Check_url        = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/info?act_id={}&region={}&uid={}'

    #value
    Act_id          = 'e202009291139501'
    Game_biz        = 'hk4e_cn'

    def ys_sign(self,region,uid):
        sign_data = {
            "act_id" : self.Act_id,
            "region" : region,
            "uid" : uid
        }
        log.info('原神: 正在为旅行者「{}」签到'.format(uid))
        response = requests.post(url=self.Sign_url, headers=GameHeader(Referer=self.Referer_url.format(self.Act_id)), data=json.dumps(sign_data, ensure_ascii=False))
        data = json.loads(response.text.encode('utf-8'))
        SleepTime()
        return data

    def run(self,list):
        region = list["region"]
        uid = list["game_uid"]

        for i in range(3):
            sign_data = self.ys_sign(region,uid) #签到并返回数据
            try:
                #从专门的api检查签到结果
                response = requests.get(url=self.Check_url.format(self.Act_id,region,uid), headers=GameHeader())
                data = json.loads(response.text.encode('utf-8'))
                if "OK" in sign_data["message"]:
                    if data["data"]["is_sign"]: # "is_sign" 为布尔值
                        log.info('原神: 签到成功')
                        break
                    else:
                        log.info('原神: 第 {} 次请求成功但并未签上'.format(i + 1))
                elif "旅行者,你已经签到过了" in sign_data["message"]:
                    log.info('原神: 重复签到')
                    break
                else:
                    log.warning(sign_data)
                    log.warning('原神: 签到出现错误,请及时检查')
                    break
            except:
                #直接输出签到api返回的签到结果
                log.warning(data)
                log.warning("未能从检查api得到签到结果,下面为签到api返回的结果")
                if "OK" in sign_data["message"]:
                    log.info('原神: 签到成功')
                elif "旅行者,你已经签到过了" in sign_data["message"]:
                    log.info('原神: 重复签到')
                else:
                    log.warning(sign_data)
                    log.warning('原神: 签到出现错误,请及时检查')
                break

class MiYouBi(object):
    #api
    Cookie_url = "https://webapi.account.mihoyo.com/Api/cookie_accountinfo_by_loginticket?login_ticket={}"
    Cookie_url2 = "https://api-takumi.mihoyo.com/auth/api/getMultiTokenByLoginTicket?login_ticket={}&token_types=3&uid={}"
    Sign_url = "https://bbs-api.mihoyo.com/apihub/app/api/signIn"  # POST json
    List_url = "https://bbs-api.mihoyo.com/post/api/getForumPostList?forum_id={}&is_good=false&is_hot=false&page_size=20&sort_type=1"
    Detail_url = "https://bbs-api.mihoyo.com/post/api/getPostFull?post_id={}"
    Share_url = "https://bbs-api.mihoyo.com/apihub/api/getShareConf?entity_id={}&entity_type=1"
    Vote_url = "https://bbs-api.mihoyo.com/apihub/sapi/upvotePost"  # POST json 
    UserBusinesses_url = "https://bbs-api.mihoyo.com/user/api/getUserBusinesses?uid={}" #获取"我的频道"信息
    Missions_url = "https://bbs-api.mihoyo.com/apihub/api/getUserMissionsState?" #获取任务完成情况

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
        self.CheckMission = True #检查任务完成情况

        if self.LoginTicket == "" or self.stuid == "" or self.stoken == "":
            log.info("更新Cookie数据中......")
            self.MYS_Cookie()

        self.headers = {
            "Cookie": f'login_ticket={self.LoginTicket};stuid={self.stuid};stoken={self.stoken}',
            'User-Agent': "okhttp/4.8.0",
            "DS": "",
            "x-rpc-client_type": mysClient_type,
            "x-rpc-app_version": mysVersion,
            "x-rpc-device_id": str(uuid.uuid3(uuid.NAMESPACE_URL, BBS_Cookie)),
            "x-rpc-device_name": "vivo s7",
            "x-rpc-device_model": "vivo-s7",
            "x-rpc-sys_version": "12",
            "x-rpc-channel": "miyousheluodi",
            "Accept-Encoding": "gzip",
            "Referer": "https://app.mihoyo.com",
            "Host": "bbs-api.mihoyo.com"
        }

        self.BBS_WhiteList = self.UserBusinesses()["data"]["businesses"]

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
            response = requests.get(url=self.Cookie_url.format(self.LoginTicket)) #获取stuid
            data = json.loads(response.text.encode('utf-8'))
            if "成功" in data["data"]["msg"]:
                self.stuid = data["data"]["cookie_info"]["account_id"]
                response = requests.get(url=self.Cookie_url2.format(self.LoginTicket, self.stuid)) #获取stoken
                data = json.loads(response.text.encode('utf-8'))
                self.stoken = data["data"]["list"][0]["token"]
                self.Write()
            else:
                log.warning(data)
                log.warning('Cookie已失效,请重新抓取Cookie')
                self.Cleared()
                sys.exit()
        else:
            log.warning('Cookie中没有"login_ticket"数据,请重新抓取Cookie!')
            self.Cleared()
            sys.exit()

    def UserBusinesses(self):
        self.headers["DS"] = DS_BBS()
        response = requests.get(url=self.UserBusinesses_url.format(self.stuid), headers=self.headers)
        data = json.loads(response.text.encode('utf-8'))
        if "OK" in data["message"]:
            SleepTime()
            return data
        else:
            log.warning(data)
            log.warning('获取账号"我的频道"信息失败,退出签到')
            sys.exit()

    def SignIn(self):
        for i in self.BBS_List:
            if i["id"] in self.BBS_WhiteList:
                self.headers["DS"] = DS_discuss(gid=i["id"])
                response = requests.post(url=self.Sign_url, headers=self.headers, json={"gids": i["id"]})
                data = json.loads(response.text.encode('utf-8'))
                if "登录失效，请重新登录" not in data["message"]:
                    log.info(i["name"] + ": " + data["message"])
                    SleepTime()
                else:
                    log.warning(data)
                    log.warning('签到失败,你的Cookie可能已过期,请重新抓取Cookie')
                    self.Cleared()
                    sys.exit()

    def Only_MYB(self):
        List = []
        #获取帖子列表
        self.headers["DS"] = DS_BBS()
        response = requests.get(url=self.List_url.format('26'), headers=self.headers) #获取的原神频道帖子
        data = json.loads(response.text.encode('utf-8'))
        #将获取到的帖子的id写入List
        PostSum = len(data["data"]["list"])
        for n in range(PostSum):
            List.append(data["data"]["list"][n]["post"]["post_id"])

        #看帖3篇
        Success = 0
        Count = 0
        log.info('浏览3篇帖子中......')
        while Success < 3 and Count < PostSum:
            self.headers["DS"] = DS_BBS()
            response = requests.get(url=self.Detail_url.format(List[Count]), headers=self.headers)
            data = json.loads(response.text.encode('utf-8'))
            if "OK" in data["message"]:
                Count += 1
            elif "帖子不存在" in data["message"]:
                log.warning('帖子(ID:{})可能已被作者或管理员删除'.format(List[Count]))
                Count += 1
            else:
                log.warning(data)            
                log.warning("浏览帖子出现问题,请及时检查")
                sys.exit()
            #检查任务是否完成
            if Count >= 3 and self.CheckMission:
                try:
                    response = requests.get(url=self.Missions_url + "point_sn=myb", headers=GameHeader()) #使用的是游戏签到header!!!
                    data = json.loads(response.text.encode('utf-8'))
                    for i in data["data"]["states"]:
                        if i["mission_key"] == "view_post_0": #米游币每日任务-浏览3个帖子
                            Success = i["happened_times"]
                            break
                except:
                    log.warning("检查任务是否完成失败,跳过检查")
                    log.warning(data)
                    self.CheckMission = False
            else:
                Success = Count
            SleepTime()
        else:
            if self.CheckMission:
                log.info("检查结果: 浏览成功{}篇".format(Success))
            if Success < 3:
                log.warning('尝试了{}篇帖子,浏览成功{}篇,未能完成任务'.format(Count,Success))

        #点赞5篇
        Success = 0
        Count = 0
        log.info('点赞5篇帖子中......')
        while Success < 5 and Count < PostSum:
            self.headers["DS"] = DS_BBS()
            response = requests.post(url=self.Vote_url, headers=self.headers,json={"post_id": List[Count], "is_cancel": False})
            data = json.loads(response.text.encode('utf-8'))
            if "OK" in data["message"]:
                Count += 1
            elif "帖子不存在" in data["message"]:
                log.warning('帖子(ID:{})可能已被作者或管理员删除'.format(List[Count]))
                Count += 1
            else:
                log.warning(data)            
                log.warning("点赞出现问题,请及时检查")
                sys.exit()
            #检查任务是否完成
            if Count >= 5 and self.CheckMission:
                response = requests.get(url=self.Missions_url + "point_sn=myb", headers=GameHeader()) #使用的是游戏签到header!!!
                data = json.loads(response.text.encode('utf-8'))
                #上一步"看帖3篇"try过了
                for i in data["data"]["states"]:
                    if i["mission_key"] == "post_up_0": #米游币每日任务-完成5次点赞
                        Success = i["happened_times"]
                        break
            else:
                Success = Count
            SleepTime()
        else:
            if self.CheckMission:
                log.info("检查结果: 点赞成功{}篇".format(Success))
            if Success < 5:
                log.warning('尝试了{}篇帖子,点赞成功{}篇,未能完成任务'.format(Count,Success))

        #分享1篇
        Success = 0
        Count = 0
        log.info('分享1篇帖子中......')
        while Success < 1 and Count < PostSum:
            self.headers["DS"] = DS_BBS()
            response = requests.get(url=self.Share_url.format(List[Count]), headers=self.headers)
            data = json.loads(response.text.encode('utf-8'))
            if "OK" in data["message"]:
                Count += 1
            elif "帖子不存在" in data["message"]:
                log.warning('帖子(ID:{})可能已被作者或管理员删除'.format(List[Count]))
                Count += 1
            else:
                log.warning(data)            
                log.warning("点赞出现问题,请及时检查")
                sys.exit()
            #检查任务是否完成
            if Count >= 1 and self.CheckMission:
                response = requests.get(url=self.Missions_url + "point_sn=myb", headers=GameHeader()) #使用的是游戏签到header!!!
                data = json.loads(response.text.encode('utf-8'))
                #上上步"看帖3篇"try过了
                for i in data["data"]["states"]:
                    if i["mission_key"] == "share_post_0": #米游币每日任务-分享帖子
                        Success = i["happened_times"]
                        break
            else:
                Success = Count
            SleepTime()
        else:
            if self.CheckMission:
                log.info("检查结果: 分享成功{}篇".format(Success))
            if Success < 1:
                log.warning('尝试分享了{}篇帖子,居然一篇都没有成功,未能完成任务'.format(Count))

    def Channel(self,channel):
        List = []
        log.info("正在执行「{}」频道 “点赞10篇帖子” 任务......".format(channel["name"]))
        #获取该频道帖子列表
        self.headers["DS"] = DS_BBS()
        response = requests.get(url=self.List_url.format(channel["forumId"]), headers=self.headers)
        data = json.loads(response.text.encode('utf-8'))
        #将获取到的帖子的id写入List
        PostSum = len(data["data"]["list"])
        for n in range(PostSum):
            List.append(data["data"]["list"][n]["post"]["post_id"])

        #点赞10篇
        Success = 0
        Count = 0
        while Success < 10 and Count < PostSum:
            self.headers["DS"] = DS_BBS()
            response = requests.post(url=self.Vote_url, headers=self.headers,json={"post_id": List[Count], "is_cancel": False})
            data = json.loads(response.text.encode('utf-8'))
            if "OK" in data["message"]:
                Count += 1
            elif "帖子不存在" in data["message"]:
                log.warning('帖子(ID:{})可能已被作者或管理员删除'.format(List[Count]))
                Count += 1
            else:
                log.warning(data)            
                log.warning("点赞出现问题,请及时检查")
                sys.exit()
            #检查任务是否完成
            if Count >= 10 and self.CheckMission:
                try:
                    response = requests.get(url=self.Missions_url + "gids={}".format(channel["id"]), headers=GameHeader()) #使用的是游戏签到header!!!
                    data = json.loads(response.text.encode('utf-8'))
                    for i in data["data"]["states"]:
                        if i["mission_key"] == "post_up_{}".format(channel["id"]):
                            Success = i["happened_times"]
                            break
                except:
                    log.warning("检查任务是否完成失败,跳过检查")
                    self.CheckMission = False
            else:
                Success = Count
            SleepTime()
        else:
            if self.CheckMission:
                log.info("检查结果: 点赞成功{}篇".format(Success))
            if Success < 10:
                log.warning('尝试了{}篇帖子,点赞成功{}篇,未能完成任务'.format(Count,Success))
                sys.exit()

    def run(self):
        log.info("开始执行讨论区签到......")
        self.SignIn()

        if Enable["BBS"]:
            log.info('开始执行米游币任务......')
            self.Only_MYB()

        if Enable["Channel"]:
            log.info('开始执行各频道升级任务......')
            for channel in self.BBS_List:
                if channel["id"] in self.BBS_WhiteList:
                    self.Channel(channel)


if __name__ == '__main__':
    delay = LoadConfig()["Delay"]
    Game_Cookie = LoadConfig()["Game_Cookie"]
    BBS_Cookie = LoadConfig()["BBS_Cookie"]
    Game_BlackList = LoadConfig()["Game_BlackList"]
    Enable = LoadConfig()["Enable"]

    log.info('欢迎使用 MihoyoBBS-AutoSign v1.2')
    if delay:
        log.info('已启用随机延迟,请耐心等待')

    #游戏每日签到
    if Enable["BH3"] or Enable["YS"]:
        for list in GetAllRoles()["data"]["list"]:
            if list["game_biz"] == "bh3_cn" and list["game_uid"] not in Game_BlackList["BH3"] and Enable["BH3"]:
                BH3_Checkin().run(list) #崩坏3福利补给
            elif list["game_biz"] == "hk4e_cn" and list["game_uid"] not in Game_BlackList["YS"] and Enable["YS"]:
                YS_Checkin().run(list) #原神每日签到
    else:
        if Game_Cookie == "":
            log.info('虽然关闭了所有的游戏签到,但是米游币签到结果校验需要用到"Game_Cookie",请务必填写')

    #米游社签到
    if Enable["BBS"] or Enable["Channel"]:
        MiYouBi().run()
    
    log.info('任务全部完成\n')