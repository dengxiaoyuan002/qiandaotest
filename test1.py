import logging
import requests
import js2py

# import notify
date = 123
msg = ""
a = 0
hz = ".rcits.cn"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
with open("1zh.txt") as file:
    while date != "\n":
        date = file.readline()  # 账号
        # date1 = file.readline()  #密码
        date1 = date.strip('\n') + "123456"
        if date == '\n':
            break
        while True:  # 无限循环，直到成功为止
            try:
                # 登录
                url = "https://" + date.strip('\n') + hz + "/user/ajax.php?act=login"

                payload = "user=" + date.strip('\n') + "&pass=" + date1.strip('\n')
                headers = {
                    'Origin': "https://" + date.strip('\n') + hz,
                    'Referer': "https://" + date.strip('\n') + hz + "/user/login.php",
                    'Content-Type': 'application/x-www-form-urlencoded'
                }

                response = requests.request("POST", url, headers=headers, data=payload)
                a += 1
                # print("第{}个   ".format(a)+date.strip('\n'))
                # print(response.text)

                logger.info("账号: %s", "第{}个   ".format(a) + date.strip('\n'))
                logger.info("响应内容: %s", response.text)

                login_fail = response.text.find("用户名或密码不正确！")
                if login_fail != -1:
                    break  # 登录失败，跳过这次迭代

                # 获取基本cookie
                cookie = response.cookies
                PHPSESSID = cookie.values()[0]
                user_token = cookie.values()[1]
                mysid = cookie.values()[2]

                url = "https://" + date.strip('\n') + hz + "/user/qiandao.php"

                payload = {}
                headers = {
                    'authority': date.strip('\n') + hz,
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                    'cache-control': 'no-cache',
                    # 'cookie': "mysid=" + mysid + "; user_token=" + user_token + "; PHPSESSID=" + PHPSESSID + "; sec_defend=" + sec_defend + "; counter=1; _aihecong_chat_visibility=true",
                    'pragma': 'no-cache',
                    'referer': "https://" + date.strip('\n') + hz + "/user/",
                    'sec-ch-ua': '"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'document',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'same-origin',
                    'sec-fetch-user': '?1',
                    'upgrade-insecure-requests': '1',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
                }

                response = requests.request("GET", url, headers=headers, data=payload)

                # print(response.text)
                start_index = response.text.find(',(') + 1
                end_index = response.text.find(');', start_index)

                if start_index != -1 and end_index != -1:
                    string = response.text[start_index:end_index]
                    cookiess = string
                    # print(cookiess)
                    sec_defend = js2py.eval_js(cookiess)
                # print(sec_defend)

                # sec_defend有效化
                url = "https://" + date.strip('\n') + hz + "/user/qiandao.php"

                payload = {}
                headers = {
                    'authority': date.strip('\n') + hz,
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                    'cache-control': 'no-cache',
                    'cookie': "mysid=" + mysid + "; user_token=" + user_token + "; PHPSESSID=" + PHPSESSID + "; sec_defend=" + sec_defend + "; counter=1; _aihecong_chat_visibility=true",
                    'pragma': 'no-cache',
                    'referer': "https://" + date.strip('\n') + hz + "/user/",
                    'sec-ch-ua': '"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'document',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'same-origin',
                    'sec-fetch-user': '?1',
                    'upgrade-insecure-requests': '1',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
                }
                response = requests.request("GET", url, headers=headers, data=payload)

                # print(response.text)

                # 签到
                url = "https://" + date.strip('\n') + hz + "/user/ajax_user.php?act=qiandao"
                payload = {}
                headers = {
                    'Cookie': "mysid=" + mysid + "; user_token=" + user_token + "; PHPSESSID=" + PHPSESSID + "; sec_defend=" + sec_defend + "; counter=1; _aihecong_chat_visibility=true",
                    'Referer': "https://" + date.strip('\n') + hz + "/user/qiandao.php"
                }

                response = requests.request("GET", url, headers=headers, data=payload)

                # print(response.json())
                logger.info("签到状态: %s", response.json())
                msg = msg + "\n" + str(a) + "   " + date.strip('\n') + "   " + str(response.json()) + '\n'
                break  # 成功执行，退出重试循环

            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}. Retrying...")


def send_wechat(msg):
    token = '6e2a636fa73f4437ab92f48417111e46'  # 前边复制到那个token
    title = 'Github Action签到通知'
    content = msg
    template = 'html'
    url = f"https://www.pushplus.plus/send?token={token}&title={title}&content={content}&template={template}"
    # print(url)
    logger.info("url: %s", url)
    r = requests.get(url=url)
    # print(r.text)
    logger.info("推送状态: %s", r.text)


if __name__ == '__main__':
    send_wechat(msg)
