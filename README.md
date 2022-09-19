# MihoyoBBS-AutoSign
自动完成 『崩坏3福利补给』『原神签到福利』『米游币任务』『频道升级任务』  
现已支持多账号(测试中,欢迎反馈bug)

本项目"米游币签到"功能的部分内容参考了[XiaoMiku01/miyoubiAuto](https://github.com/XiaoMiku01/miyoubiAuto)进行编写  
感谢大佬的无私分享！！  

**为了大家的安全使用，请勿在B站、QQ、各大社交软件、论坛等任何公共平台传播！**


## 使用前请先安装第三方库
```shell
pip3 install requests
```


## 使用方法
**务必使用python3运行**  

1. 下载源码

2. 在config.json中的`“Cookie”`条目内填入米游社Cookie(获取cookie方法往下翻)  

3. 运行mhy.py  
    ```shell
    python3 mhy.py
    ```


## 多账号功能(测试中,欢迎反馈bug)
### 一、配置多账号功能
1. 在 `“MultiConfig”` 文件夹中填入配置文件(内有一个初始模板),配置文件的命名请严格遵守 **“序号-config-备注信息”** 例如: 1-config-qwq.json 或 2-config-test.json  
![配置多账号功能图解](https://upload-bbs.mihoyo.com/upload/2022/09/04/79828707/36449c1bf9802a6873ab963f3f67db6d_3701744741000984365.png
)
2. 运行mhy.py **注意后面有参数**  
    ```shell
    python3 mhy.py multi
    ```
    注：运行后会自动生成cookie缓存文件，名称为 **序号-cookie.json**
### 二、更新配置文件
- 更新配置文件前需要先删除对应配置文件的cookie缓存文件，然后再获取新的cookie并填入配置文件
### 三、删除配置文件
- 请一定要把配置文件和对应的cookie缓存文件一起删除掉，**并保证删除后剩余配置文件序号的连续性**

## 手动更新cookie
输入以下命令可以手动更新cookie缓存数据
```shell
python3 mhy.py updata
```

## 获取Cookie方法

1. 打开你的浏览器,进入**无痕模式** , edge为**新建InPrivate窗口**

2.  先登录 [https://bbs.mihoyo.com/ys/](https://bbs.mihoyo.com/ys/)  
    再登录 [https://user.mihoyo.com/](https://user.mihoyo.com/)  
    **(请严格按照步骤顺序登录,否则可能cookie不全导致功能异常)**  
    **(请严格按照步骤顺序登录,否则可能cookie不全导致功能异常)**  
    **(请严格按照步骤顺序登录,否则可能cookie不全导致功能异常)**

3. 登录完成后按下键盘上的`F12`或右键检查以进入开发者工具,点击Console或者控制台 **(是在第二个打开的网页上操作)**

4. 输入以下内容

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
    - `"BBS"` 控制是否执行『米游币任务』(包括讨论区签到)
    - `"ChannelUpVote"` 控制是否执行『频道点赞任务』
    - `"ChannelPublish"` 控制是否执行『频道发帖&评论任务』**(实验性功能,默认关闭)**
    - `"DeleteOldPost"` 控制是否删除今天之前水的帖子(仅本次更新后水的帖子有效) **(实验性功能,默认关闭)**

- `"Game_BlackList"` 内的为不想签到的UID (是游戏内的UID)
    - `"BH3"` 内为『崩坏3』的UID
    - `"YS"` 内为『原神』的UID

## LICENSE
请遵守开源协议 [GNU General Public License v3.0](https://github.com/lingduzero666/MihoyoBBS-AutoSign/blob/main/LICENSE)
