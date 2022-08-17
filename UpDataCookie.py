import os
import sys
import json
import time
import requests

Cookie_url = "https://webapi.account.mihoyo.com/Api/cookie_accountinfo_by_loginticket?login_ticket={}"
Cookie_url2 = "https://api-takumi.mihoyo.com/auth/api/getMultiTokenByLoginTicket?login_ticket={}&token_types=3&uid={}"

def LoadConfig():
    PATH = os.path.dirname(os.path.realpath(__file__))
    with open(f"{PATH}/config.json", "r",encoding="utf-8") as f:
        data = json.load(f)
        f.close()
        return data

def LoadCookie():
    PATH = os.path.dirname(os.path.realpath(__file__))
    with open(f"{PATH}/cookie.json", "r",encoding="utf-8") as f:
        data = json.load(f)
        f.close()
        return data

def Write(LoginTicket,stuid,stoken):
    params = LoadCookie()
    params["login_ticket"] = LoginTicket
    params["stuid"] = stuid
    params["stoken"] = stoken
    PATH = os.path.dirname(os.path.realpath(__file__))
    with open(f"{PATH}/cookie.json", "w",encoding="utf-8") as r:
        json.dump(params,r)
        r.close()

def Cleared():
    params = LoadCookie()
    params["login_ticket"] = ""
    params["stuid"] = ""
    params["stoken"] = ""
    PATH = os.path.dirname(os.path.realpath(__file__))
    with open(f"{PATH}/cookie.json", "w",encoding="utf-8") as r:
        json.dump(params,r)
        r.close()

def UpDataookie():
    print('更新中......')
    BBS_Cookie = LoadConfig()["BBS_Cookie"]
    if "login_ticket" in BBS_Cookie:
        c = BBS_Cookie.split(";")
        for i in c:
            if i.split("=")[0] == " login_ticket":
                LoginTicket = i.split("=")[1]
                break
        response = requests.get(url=Cookie_url.format(LoginTicket))
        data = json.loads(response.text.encode('utf-8'))
        if "成功" in data["data"]["msg"]:
            stuid = data["data"]["cookie_info"]["account_id"]
            response = requests.get(url=Cookie_url2.format(LoginTicket, stuid))
            data = json.loads(response.text.encode('utf-8'))
            stoken = data["data"]["list"][0]["token"]
            print('更新Cookie数据成功')
            return LoginTicket,stuid,stoken
        else:
            print(data)
            print("Cookie已失效,请重新抓取Cookie")
            Cleared()
            sys.exit()
    else:
        print("Cookie中没有'login_ticket'数据,请重新抓取Cookie!")
        Cleared()
        sys.exit()

if __name__ == '__main__':
    print('将在5秒后开始更新Cookie数据')
    time.sleep(5)

    params = UpDataookie()
    LoginTicket = params[0]
    stuid = params[1]
    stoken = params[2]

    print('login_ticket:{}, stuid:{}, stoken:{}'.format(LoginTicket,stuid,stoken))
    Write(LoginTicket,stuid,stoken)
    print('数据写入完毕')