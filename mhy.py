# -*- coding: utf-8 -*-
import requests
import logging
import random
import time
import hashlib
import string
import uuid
import json
import glob
import os
import sys

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

#全局变量
VERSION = "v1.4.1"
PATH = os.path.dirname(os.path.realpath(__file__))
Multi_ConfigPath = PATH + "/MultiConfig/{}-config-{}.json"
Multi_CookiePath = PATH + "/MultiConfig/{}-cookie.json"


def LoadConfig(path=f"{PATH}/config.json"):
    '''加载配置文件'''
    with open(path, "r",encoding="utf-8") as f:
            data = json.load(f)
            f.close()
            return data

def LoadCookie(path=f"{PATH}/cookie.json"):
    '''加载缓存的cookie文件'''
    with open(path, "r",encoding="utf-8") as f:
            data = json.load(f)
            f.close()
            return data

def Write(login_ticket,stuid,stoken,path=f"{PATH}/cookie.json"):
    '''写入cookie缓存'''
    params = {"login_ticket": "{}".format(login_ticket), "stuid": "{}".format(stuid), "stoken": "{}".format(stoken)}
    with open(path, "w",encoding="utf-8") as r:
        json.dump(params,r)
        r.close()

def Cleared(path=f"{PATH}/cookie.json"):
    '''清空缓存cookie'''
    if path != f"{PATH}/cookie.json":
        os.remove(path)
    else:
        params = {"login_ticket": "", "stuid": "", "stoken": ""}
        with open(path, "w",encoding="utf-8") as r:
            json.dump(params,r)
            r.close()

def GameHeader(Referer="https://webstatic.mihoyo.com/"): #此referer为默认值
    '''游戏签到福利的header'''
    headers = {
        'Cookie': Cookie,
        'User-Agent': 'Mozilla/5.0 (Linux; Android 12; vivo-s7 Build/RKQ1.211119.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Version/4.0 Chrome/103.0.5060.71 Mobile Safari/537.36 miHoYoBBS/2.35.2',
        'Referer': Referer,
        'DS': DS_BBS(),
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate',
        'Origin': 'https://webstatic.mihoyo.com',
        'X-Requested-With': 'com.mihoyo.hyperion',
        'x-rpc-device_id': str(uuid.uuid3(uuid.NAMESPACE_URL, Cookie)),
        'x-rpc-device_name': 'vivo s7',
        'x-rpc-device_model': 'vivo-s7',
        'x-rpc-sys_version': '12',
        'x-rpc-channel': 'vivo',
        'x-rpc-client_type': mysClient_type,
        'x-rpc-app_version': mysVersion
    }
    return headers

def SleepTime():
    '''随机延迟时间'''
    if delay :
        time.sleep(random.randint(5,10))
    else:
        time.sleep(1)
      
def md5(text):
    '''md5加密'''
    md5 = hashlib.md5()
    md5.update(text.encode())
    return md5.hexdigest()

def randomStr(n):
    '''生成指定位数的随机数'''
    return (''.join(random.sample(string.digits + string.ascii_letters, n))).lower()

def DS_BBS():
    '''生成米游社DS'''
    n = Salt_BBS
    i = str(int(time.time()))
    r = randomStr(6)
    c = md5("salt=" + n + "&t=" + i + "&r=" + r)
    return "{},{},{}".format(i, r, c)

def DS_discuss(gid):
    '''生成讨论区DS'''
    n = Salt_Discuss
    i = str(int(time.time()))
    r = str(random.randint(100001, 200000))
    b = json.dumps({"gids": gid})
    c = md5("salt=" + n + "&t=" + i + "&r=" + r + "&b=" + b + "&q=") #q值为空
    return "{},{},{}".format(i, r, c)

def GetAllRoles():
    '''获取账号的全部角色信息'''
    log.info('获取账号的全部角色信息中......')
    url = 'https://api-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie'

    response = requests.get(url,headers=GameHeader())
    data = json.loads(response.text.encode('utf-8'))
    if '登录失效，请重新登录' in data["message"]:
        log.warning(data)
        log.warning('Cookie已失效,请重新抓取Cookie')
        sys.exit()
    SleepTime()
    return data

def CreateCookieCache(ConfigPath=f"{PATH}/config.json", CookiePath=f"{PATH}/cookie.json"):
    Cookie_url  = "https://webapi.account.mihoyo.com/Api/cookie_accountinfo_by_loginticket?login_ticket={}"
    Cookie_url2 = "https://api-takumi.mihoyo.com/auth/api/getMultiTokenByLoginTicket?login_ticket={}&token_types=3&uid={}"

    log.info("更新Cookie数据中......")
    CookieCache = LoadConfig(ConfigPath)
    if "login_ticket" in CookieCache["Cookie"]:
        c = CookieCache["Cookie"].split(";")
        for i in c:
            if i.split("=")[0] == " login_ticket": #login_ticket前面的空格是必须的
                LoginTicket = i.split("=")[1]
                break
        response = requests.get(url=Cookie_url.format(LoginTicket)) #获取stuid
        data = json.loads(response.text.encode('utf-8'))
        if "成功" in data["data"]["msg"]:
            stuid = data["data"]["cookie_info"]["account_id"]
            response = requests.get(url=Cookie_url2.format(LoginTicket, stuid)) #获取stoken
            data = json.loads(response.text.encode('utf-8'))
            stoken = data["data"]["list"][0]["token"]
            Write(LoginTicket,stuid,stoken,CookiePath)
            log.info('更新成功')
        else:
            log.warning(data)
            log.warning('Cookie已失效,请重新抓取Cookie')
            Cleared(CookiePath)
            sys.exit()
    else:
        log.warning('Cookie中没有"login_ticket"数据,请重新抓取Cookie!')
        sys.exit()

def Multi_Load():
    '''多账号加载'''
    MultiPath = []
    for m in range(len(glob.glob(Multi_ConfigPath.format("*","*")))):
        try:#从1开始轮询，避免顺序错误
            MultiPath.append(glob.glob(Multi_ConfigPath.format(m+1,"*"))[0])
        except:
            break
    MultiCookie = glob.glob(Multi_CookiePath.format("*"))
    TotalConfig = len(MultiPath)
    TotalCookie = len(MultiCookie)

    Cookie_url  = "https://webapi.account.mihoyo.com/Api/cookie_accountinfo_by_loginticket?login_ticket={}"
    Cookie_url2 = "https://api-takumi.mihoyo.com/auth/api/getMultiTokenByLoginTicket?login_ticket={}&token_types=3&uid={}"

    #获取备注信息
    MultiRemark = []
    for r in MultiPath:
        MultiRemark.append(r.split("/")[-1].split("-")[-1].split(".")[0])

    log.info('共找到 {} 个配置文件, {} 个缓存的Cookie数据'.format(TotalConfig,TotalCookie))

    #获取没有缓存cookie的账号序号并创建cookie缓存
    ConfigOrdinal = []
    for c1 in MultiPath:
        ConfigOrdinal.append(c1.split("/")[-1].split("-")[0])
    CookieOrdinal = []
    for c2 in MultiCookie:
        CookieOrdinal.append(c2.split("/")[-1].split("-")[0])
    if TotalCookie != TotalConfig:
        for D in ConfigOrdinal:
            if D not in CookieOrdinal:
                d = int(D)
                log.info('正在为 [{}] 更新cookie数据......'.format(MultiRemark[d-1]))
                CreateCookieCache(ConfigPath=Multi_ConfigPath.format(d, MultiRemark[d-1]), CookiePath=Multi_CookiePath.format(d))
                time.sleep(random.randint(2,5)) #写死休眠时间,防止触发风控
    return MultiPath,MultiRemark,TotalConfig

class BH3_Checkin():

    #api
    Referer_url     = 'https://webstatic.mihoyo.com/bbs/event/signin/bh3/index.html?bbs_auth_required=true&act_id={}&bbs_presentation_style=fullscreen&utm_source=bbs&utm_medium=mys&utm_campaign=icon'
    Sign_url        = 'https://api-takumi.mihoyo.com/event/luna/sign' #POST json
    Check_url       = 'https://api-takumi.mihoyo.com/event/luna/info?lang=zh-cn&act_id={}&region={}&uid={}'

    #value
    Act_id          = 'e202207181446311'
    Game_biz        = 'bh3_cn'

    def bh3_sign(self,region,uid):
        sign_data = {
            "act_id": self.Act_id,
            "region": region,
            "uid": uid,
            "lang": "zh-cn"
        }
        log.info('崩坏3: 正在为舰长「{}」签到'.format(uid))
        response = requests.post(url=self.Sign_url, headers=GameHeader(Referer=self.Referer_url.format(self.Act_id)), json=sign_data)
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
                log.warning("未能从检查api得到签到结果,下面为签到api返回的结果,有概率漏签")
                if "OK" in sign_data["message"]:
                    log.info('崩坏3: 签到成功')
                elif '已签到' in sign_data["message"]:
                    log.info('崩坏3: 重复签到')
                else:
                    log.warning(sign_data)
                    log.warning('崩坏3: 签到出现错误,请及时检查')
                break

class YS_Checkin():
    
    #api
    Referer_url     = 'https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?bbs_auth_required=true&act_id={}&utm_source=bbs&utm_medium=mys&utm_campaign=icon'
    Sign_url        = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/sign' #POST json
    Check_url       = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/info?act_id={}&region={}&uid={}'

    #value
    Act_id          = 'e202009291139501'
    Game_biz        = 'hk4e_cn'

    def ys_sign(self,region,uid):
        sign_data = {
            "act_id": self.Act_id,
            "region": region,
            "uid": uid
        }
        log.info('原神: 正在为旅行者「{}」签到'.format(uid))
        response = requests.post(url=self.Sign_url, headers=GameHeader(Referer=self.Referer_url.format(self.Act_id)), json=sign_data)
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
                log.warning("未能从检查api得到签到结果,下面为签到api返回的结果,有概率漏签")
                if "OK" in sign_data["message"]:
                    log.info('原神: 签到成功')
                elif "旅行者,你已经签到过了" in sign_data["message"]:
                    log.info('原神: 重复签到')
                else:
                    log.warning(sign_data)
                    log.warning('原神: 签到出现错误,请及时检查')
                break

class MihoyoBBS():
    #api
    Cookie_url          = "https://webapi.account.mihoyo.com/Api/cookie_accountinfo_by_loginticket?login_ticket={}"
    Cookie_url2         = "https://api-takumi.mihoyo.com/auth/api/getMultiTokenByLoginTicket?login_ticket={}&token_types=3&uid={}"
    Sign_url            = "https://bbs-api.mihoyo.com/apihub/app/api/signIn"  # POST json
    List_url            = "https://bbs-api.mihoyo.com/post/api/getForumPostList?forum_id={}&is_good=false&is_hot=false&page_size=20&sort_type=1"
    GetPostFull_url     = "https://bbs-api.mihoyo.com/post/api/getPostFull?post_id={}"
    Share_url           = "https://bbs-api.mihoyo.com/apihub/api/getShareConf?entity_id={}&entity_type=1"
    UpVote_url          = "https://bbs-api.mihoyo.com/apihub/sapi/upvotePost"  # POST json
    UserBusinesses_url  = "https://bbs-api.mihoyo.com/user/api/getUserBusinesses?uid={}" #获取"我的频道"信息
    Missions_url        = "https://bbs-api.mihoyo.com/apihub/api/getUserMissionsState?" #获取任务完成情况
    Draft_url           = "https://bbs-api.mihoyo.com/post/api/draft/save"  # POST json 草稿
    ReleasePost_url     = "https://bbs-api.mihoyo.com/post/api/releasePost/v2" # POST json 发帖
    ReleaseReply_url    = "https://bbs-api.mihoyo.com/post/api/releaseReply"# POST json 发评论
    SelfPostList_url    = "https://bbs-api.mihoyo.com/painter/api/user_instant/list?offset={}&size=20&uid={}" #offset初始值为0
    DeletePost_url      = "https://bbs-api.mihoyo.com/post/api/deletePost" # POST json 删帖

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
        self.LoginTicket = CookieCache["login_ticket"]
        self.stuid = CookieCache["stuid"]
        self.stoken = CookieCache["stoken"]

        self.CheckMission = True #检查任务完成情况

        if self.LoginTicket == "" or self.stuid == "" or self.stoken == "":
            CreateCookieCache()

        self.headers = {
            "Cookie": f'login_ticket={self.LoginTicket};stuid={self.stuid};stoken={self.stoken}',
            'User-Agent': "okhttp/4.8.0",
            "DS": "", #随用随更新，保证实时性
            "x-rpc-client_type": mysClient_type,
            "x-rpc-app_version": mysVersion,
            "x-rpc-device_id": str(uuid.uuid3(uuid.NAMESPACE_URL, Cookie)),
            "x-rpc-device_name": "vivo s7",
            "x-rpc-device_model": "vivo-s7",
            "x-rpc-sys_version": "12",
            "x-rpc-channel": "miyousheluodi",
            "Accept-Encoding": "gzip",
            "Referer": "https://app.mihoyo.com",
            "Host": "bbs-api.mihoyo.com"
        }

        self.BBS_WhiteList = self.UserBusinesses()["data"]["businesses"]

    def UserBusinesses(self):
        log.info('获取米游社"我的频道"信息中......')
        self.headers["DS"] = DS_BBS()
        response = requests.get(url=self.UserBusinesses_url.format(self.stuid), headers=self.headers)
        data = json.loads(response.text.encode('utf-8'))
        if "OK" in data["message"]:
            SleepTime()
            return data
        elif "登录失效，请重新登录" in data["message"]:
            log.warning('Cookie已失效,请重新抓取Cookie')
            Cleared()
        else:
            log.warning(data)
            log.warning('获取账号"我的频道"信息失败,退出签到')
            sys.exit()

    def SignIn(self):
        log.info('讨论区签到中......')
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
                    Cleared()
                    sys.exit()

    def Only_MYB(self):
        '''米游币任务'''
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
            response = requests.get(url=self.GetPostFull_url.format(List[Count]), headers=self.headers)
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
                log.info("检查结果: 浏览成功 {} 篇".format(Success))
            else:
                log.info('未能从检查api得到签到结果,有概率漏签')
            if Success < 3:
                log.warning('尝试了{}篇帖子,浏览成功{}篇,未能完成任务'.format(Count,Success))

        #点赞5篇
        Success = 0
        Count = 0
        log.info('点赞5篇帖子中......')
        while Success < 5 and Count < PostSum:
            self.headers["DS"] = DS_BBS()
            response = requests.post(url=self.UpVote_url, headers=self.headers,json={"post_id": List[Count], "is_cancel": False})
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
                log.info("检查结果: 点赞成功 {} 篇".format(Success))
            else:
                log.info('未能从检查api得到签到结果,有概率漏签')
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
                log.info("检查结果: 分享成功 {} 篇".format(Success))
            else:
                log.info('未能从检查api得到签到结果,有概率漏签')
            if Success < 1:
                log.warning('尝试分享了{}篇帖子,居然一篇都没有成功,未能完成任务'.format(Count))

    def Channel_UpVote(self,channel):
        '''各频道点赞任务'''
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
            response = requests.post(url=self.UpVote_url, headers=self.headers,json={"post_id": List[Count], "is_cancel": False})
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
                log.info("检查结果: 点赞成功 {} 篇".format(Success))
            else:
                log.info('未能从检查api得到签到结果,有概率漏签')
            if Success < 10:
                log.warning('尝试了{}篇帖子,点赞成功{}篇,未能完成任务'.format(Count,Success))
                sys.exit()

    #以下为实验性功能
    #↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓
    def RandomElements(self):
        '''随机标题与内容'''
        SubjectList = ["水帖一篇","水水水","今日份的水帖","水帖得经验","随手一水","灌水灌水","欸嘿水一帖","每日任务之水帖"]
        ContentList = ["水帖不知道写啥","求点赞评论收藏","为了经验大家快来水帖呀","今日份的经验我来啦","水帖多多经验多多","愿早日升级"]
        Reply1List = ["我回我自己","发帖回复一条龙","为了经验必须回帖","今日份的经验get","水个回复","回复一下愿早日升级"]
        Reply2List = ["每日任务需要的回复","什么大伟出奇迹","飞鱼丸与包菜与应急食品","勤劳的孩子升级快","Ok经验到手","回复一下加快升级"]
        Subject = SubjectList[random.randint(0,len(SubjectList) - 1)]
        Content = ContentList[random.randint(0,len(ContentList) - 1)]
        Reply1 = Reply1List[random.randint(0,len(Reply1List) - 1)]
        Reply2 = Reply2List[random.randint(0,len(Reply2List) - 1)]
        return Subject,Content,Reply1,Reply2

    def Draft(self,subject,content,forumId,id):
        '''写入草稿'''
        draft_data = {
            "collection_id": 0,
            "content": "\u003cp\u003e" + content + "\u003c/p\u003e",
            "cover": "",
            "draft_id": "",
            "forum_cate_id": "",
            "forum_id": forumId,
            "gids": id,
            "is_original": 0,
            "is_profit": False,
            "link_card_list": [],
            "republish_authorization": 1,
            "structured_content": "[{\"insert\":\"" + content + "\\n\"}]",
            "subject": subject,
            "topic_ids": ["877"], #"每日一水"话题分区id
            "view_type": 1
        }
        count = 0
        while count < 3:
            self.headers["DS"] = DS_BBS()
            response = requests.post(url=self.Draft_url, headers=self.headers, json=draft_data)
            data = json.loads(response.text.encode('utf-8'))
            if data["retcode"] == 0:
                return(data["data"]["draft_id"])
            elif data["retcode"] == -1:
                count += 1
                log.info('系统繁忙,1分钟后再次尝试')
                time.sleep(random.randint(55,65)) #写死休眠时间,防止触发风控
            else:
                log.warning(data)
                log.warning('写入草稿发生错误')
                return("err")
        else:
            log.warning(data)
            log.warning('写入草稿失败')
            return("err")

    def ReleasePost(self,subject,content,forumId,id,DraftId):
        '''发帖'''
        post_data = {
            "collection_id": 0,
            "content": "\u003cp\u003e" + content + "\u003c/p\u003e",
            "cover": "",
            "draft_id": DraftId,
            "forum_cate_id": "",
            "f_forum_id": forumId,
            "gids": id,
            "is_original": 0,
            "is_pre_publication": False,
            "is_profit": False,
            "post_id": "",
            "republish_authorization": 0,
            "structured_content": "[{\"insert\":\"" + content + "\\n\"}]",
            "subject": subject,
            "topic_ids": ["877"], #"每日一水"话题分区id
            "view_type": 1
        }
        count = 0
        while count < 3:
            self.headers["DS"] = DS_BBS()
            response = requests.post(url=self.ReleasePost_url, headers=self.headers, json=post_data)
            data = json.loads(response.text.encode('utf-8'))
            if data["retcode"] == 0:
                return(data["data"]["post_id"])
            elif data["retcode"] == -1:
                count += 1
                log.info('系统繁忙,1分钟后再次尝试')
                time.sleep(random.randint(55,65)) #写死休眠时间,防止触发风控
            else:
                log.warning(data)
                log.warning('发帖发生错误')
                return("err")
        else:
            log.warning(data)
            log.warning('发帖失败')
            return("err")

    def ReleaseReply(self,PostId,reply):
        '''发评论'''
        reply_data = {
            "content": reply,
            "post_id": PostId,
            "reply_id": "",
            "structured_content": "[{\"insert\":\"" + reply + "\"}]"
        }
        count = 0
        while count < 3:
            self.headers["DS"] = DS_BBS()
            response = requests.post(url=self.ReleaseReply_url, headers=self.headers, json=reply_data)
            data = json.loads(response.text.encode('utf-8'))
            if data["retcode"] == 0:
                return data["message"]
            elif "帖子不存在" in data["message"]:
                log.warning('帖子不存在,无法评论')
                return("err")
            elif data["retcode"] == -1: #这条if未经验证,仅为推测,"帖子不存在"的retcode值也为-1
                count += 1
                log.info('系统繁忙,1分钟后再次尝试')
                time.sleep(random.randint(55,65)) #写死休眠时间,防止触发风控
            else:
                log.warning(data)
                log.warning('发评论发生错误')
                return("err")
        else:
            log.warning(data)
            log.warning('评论失败')
            return("err")

    def DeletePost(self):
        #获取需要删除的帖子
        SelfPost = []
        offset,limit = 0,0
        last = False
        while last == False and limit < 5:
            limit += 1
            self.headers["DS"] = DS_BBS()
            response = requests.get(url=self.SelfPostList_url.format(offset,self.stuid), headers=self.headers)
            data = json.loads(response.text.encode('utf-8'))
            if data["retcode"] == 0:
                offset = data["data"]["next_offset"]
                last = data["data"]["is_last"]
                for list in data["data"]["list"]:
                    PostSubject = list["post"]["post"]["subject"]
                    #双重识别,避免误删
                    if "⨌" in PostSubject:
                        if PostSubject.split("⨌")[-1] == "(1/2)" or PostSubject.split("⨌")[-1] == "(2/2)":
                            SelfPost.append(list["post"]["post"]["post_id"])
            else:
                log.info(data)
            SleepTime()
        #开始删帖
        for id in SelfPost:
            delete_data = {
                "operate_type": 0,
                "post_id": id
                }
            self.headers["DS"] = DS_BBS()
            response = requests.post(url=self.DeletePost_url, headers=self.headers, json=delete_data)
            data = json.loads(response.text.encode('utf-8'))
            if data["retcode"] == 0:
                log.info('删除帖子(id:{}) 成功'.format(id))
            else:
                log.info(data)
            SleepTime()

    def Channel_Publish(self,channel):
        '''执行各频道发帖&发评论任务'''
        for i in range(2): #发帖2篇
            subject,content,reply1,reply2 = self.RandomElements()
            subject += " ⨌({}/2)".format(i+1) #⨌此特殊符号用于删帖时作特征识别

            #写入草稿
            DraftId = self.Draft(subject,content,channel["forumId"],channel["id"])
            time.sleep(random.randint(12,15)) #写死休眠时间,防止触发风控

            #发帖子
            if DraftId == "err":
                return("err")
            else:
                PostId = self.ReleasePost(subject,content,channel["forumId"],channel["id"],DraftId)
                time.sleep(random.randint(20,30)) #写死休眠时间,防止触发风控

            #给每篇自己的帖子回复2次
            if PostId == "err":
                Reply1Data = "未发帖"
                Reply2Data = "未发帖"
            else:
                Reply1Data = self.ReleaseReply(PostId,reply1)
                time.sleep(random.randint(150,180)) #写死休眠时间,防止触发风控
                Reply2Data = self.ReleaseReply(PostId,reply2)

            #改为全角,保证对齐,强迫症直呼满足
            PerfectName = channel["name"] #加入中间参数，避免修改源数据
            if PerfectName == "崩坏3":
                PerfectName = "崩坏３"
            elif PerfectName == "崩坏2":
                PerfectName = "崩坏２"
            elif PerfectName == "原神":
                PerfectName = "原　神"

            log.info('频道:{:　<4}, 次数:{}, DraftID:{}, PostID:{}, 评论:{},{}'.format(PerfectName, i+1, DraftId, PostId, Reply1Data, Reply2Data))
            time.sleep(random.randint(300,320)) #亲测发帖间隔5分钟以上较为安全不太会触发风控
    #↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑
    #以上为实验性功能

    def run(self):
        if Enable["BBS"]:
            log.info('开始执行米游币任务......')
            self.SignIn() #讨论区签到
            self.Only_MYB() #3次浏览,5次点赞,1次分享

        if Enable["ChannelUpVote"]:
            log.info('开始执行各频道点赞任务......')
            for channel in self.BBS_List:
                if channel["id"] in self.BBS_WhiteList:
                    self.Channel_UpVote(channel)

        if Enable["DeleteOldPost"]:
            log.info('开始删除今天之前水的贴子')
            self.DeletePost()

        if Enable["ChannelPublish"]:
            log.info('开始执行各频道发帖&评论任务......')
            log.info('!!!作者亲测发帖间隔5分钟以上较为安全不太会触发风控,故完成本项任务需要巨长时间!!!')
            log.info('预估完成本项任务需要 {} 分钟,请一定要耐心等待'.format(len(self.BBS_WhiteList) * 2 * 8)) #乘数的第一个为每频道发帖次数，第二个为间隔时间
            for channel in self.BBS_List:
                if channel["id"] in self.BBS_WhiteList:
                    result = self.Channel_Publish(channel)
                    if result == "err":
                        log.warning('退出执行各频道发帖&评论任务')
                        break

def StartRun():
    if delay:
        log.info('已启用随机延迟,请耐心等待')

    #实验性功能警告
    if Enable["ChannelPublish"] or Enable["DeleteOldPost"]:
        log.info('!!!您已开启实验性功能,可能存在未知bug,且会有各种不可预估的风险(如禁言,封号),请酌情选择使用!!!')

    #游戏每日签到
    if Enable["BH3"] or Enable["YS"]:
        for list in GetAllRoles()["data"]["list"]:
            if list["game_biz"] == "bh3_cn" and list["game_uid"] not in Game_BlackList["BH3"] and Enable["BH3"]:
                BH3_Checkin().run(list) #崩坏3福利补给
            elif list["game_biz"] == "hk4e_cn" and list["game_uid"] not in Game_BlackList["YS"] and Enable["YS"]:
                YS_Checkin().run(list) #原神每日签到

    #米游社签到
    if Enable["BBS"] or Enable["ChannelUpVote"] or Enable["ChannelPublish"] or Enable["DeleteOldPost"]:
        MihoyoBBS().run()


if __name__ == '__main__':
    if "updata" in sys.argv: #手动更新cookie
        log.info('请选择为哪个模式的config更新cookie(1:单账号  2:多账号)')
        mode = int(input("请输入对应的数字："))
        if mode == 1:
            CreateCookieCache()
        elif mode == 2:
            number = int(input('请输入多账号config文件的序号：'))
            CreateCookieCache(ConfigPath=glob.glob(Multi_ConfigPath.format(number,"*"))[0], CookiePath=Multi_CookiePath.format(number))

    elif "multi" in sys.argv: #多账号
        log.info(f'欢迎使用 MihoyoBBS-AutoSign {VERSION} (多账号版)')

        #读取多账号配置
        MultiPath,MultiRemark,TotalConfig = Multi_Load()
        for n in range(TotalConfig):
            log.info('{:=^46}'.format(f'正在执行第 {n+1} 个账号(备注信息:{MultiRemark[n]})'))
            try:
                config = LoadConfig(Multi_ConfigPath.format(n+1,MultiRemark[n]))
                delay = config["Delay"]
                Cookie = config["Cookie"]
                Game_BlackList = config["Game_BlackList"]
                Enable = config["Enable"]
                CookieCache = LoadCookie(Multi_CookiePath.format(n+1))
            except:
                log.warning('有配置信息未能读取,请检查配置文件是否有错误或是否为最新版')
                sys.exit()
            StartRun()

    else:#单账号
        log.info(f'欢迎使用 MihoyoBBS-AutoSign {VERSION}')

        #读取配置文件
        try:
            config = LoadConfig()
            delay = config["Delay"]
            Cookie = config["Cookie"]
            Game_BlackList = config["Game_BlackList"]
            Enable = config["Enable"]
            CookieCache = LoadCookie()
        except:
            log.warning('有配置信息未能读取,请检查配置文件是否有错误或是否为最新版')
            sys.exit()
        StartRun()

    log.info('任务全部完成\n')