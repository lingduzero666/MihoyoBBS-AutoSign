# MihoyoBBS-AutoSign
自动完成 『崩坏3福利补给』『原神签到福利』『米游币任务』『各频道升级任务』  
(先写完了自己的需求,其他功能再说.....咕咕咕)

本项目‘米游币签到’的一部分内容参考了[XiaoMiku01/miyoubiAuto](https://github.com/XiaoMiku01/miyoubiAuto)进行编写  
感谢大佬的无私分享！！  

**为了大家的安全使用，请勿在B站、QQ、各大社交软件、论坛等任何公共平台传播！**

## 使用前请先安装第三方库
```shell
pip3 install requests
```

## 使用方法
**务必使用python3运行**  

1. 下载源码

2. 在config.json中填写米游社Cookie  
    `“Game_Cookie”` 填入从 [https://bbs.mihoyo.com/ys/](https://bbs.mihoyo.com/ys/) 获取的Cookie  
    `"BBS_Cookie"` 填入从 [https://user.mihoyo.com/](https://user.mihoyo.com/) 获取的Cookie

3. 运行mhy.py  
    ```shell
    python3 mhy.py
    ```

## 获取Cookie方法

1. 打开你的浏览器,进入**无痕模式** , edge为**新建InPrivate窗口**

2. 打开 **使用方法** 中指定的链接并登录

3. 登录完成后按下键盘上的`F12`或右键检查以进入开发者工具,点击Console或者控制台

4. 输入

   ```javascript
   var cookie=document.cookie;var ask=confirm('要复制该cookie到剪贴板吗?\n\n'+cookie);if(ask==true){copy(cookie);msg=cookie}
   ```

   回车执行，然后网页会出现确认窗口，点击确定后Cookie将复制到你的剪贴板上


## 自定义设置
修改`config.json`以自定义需求，`true`为开启`false`为关闭  
**注意拼写、大小写、json格式**  
**注意拼写、大小写、json格式**  
**注意拼写、大小写、json格式**  

- `"Delay"` 控制是否启用随机延迟

- `“Enable”` 内的各项控制是否启用相关功能  
    - `"BH3"` 控制是否自动签到『崩坏3福利补给』
    - `"YS"` 控制是否自动签到『原神签到福利』
    - `"BBS"` 控制是否执行『米游币任务』
    - `"Channel"` 控制是否执行『各频道升级任务』

- `"Game_BlackList"` 内的为不想签到的UID (是游戏内的UID)
    - `"BH3"` 内为『崩坏3』的UID
    - `"YS"` 内为『原神』的UID

## 需要使用UpDataCookie.py的情况(**一般用不到**)

1. 抓取Cookie后需要测试Cookie有效性时使用

2. 抓取Cookie后暂时不运行脚本时使用  
    （因为抓取到的`"BBS_Cookie"`有效期很短，其在脚本中的实际作用只是获取长期有效的stuid和stoken，所以该情况需要通过此文件手动获取stuid和stoken并写入cookie.json文件中）  
    PS:此结论仅为我自己账号的测试情况，之后会多测试几个账号验证的

3. 使用云函数时，请先在本地运行此文件以获取login_ticket、stuid和stoken，然后再上传  
    (虽然**目前不支持云函数**，但是先写出来再说)

- 运行指令
    ```shell
    python3 UpDataCookie.py
    ```

## 主要更新记录
- 2022/8/17  更新：通过api获取 “我的频道” 的信息，不再需要用白名单排除不需要的频道
- 2022/8/17  重构：米游币签到部分的代码，当出现 {'data': None, 'message': '帖子不存在', 'retcode': -1} 报错时会跳过该帖子，更加智能

## LICENSE
请遵守开源协议 [GNU General Public License v3.0](https://github.com/lingduzero666/MihoyoBBS-AutoSign/blob/main/LICENSE)