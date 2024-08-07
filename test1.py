import requests
import js2py
import logging
import os
date = 123
msg = ""
a = 0
hz = ".rcits.cn"
txt = "第二批.txt"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
max_retries = 5  # 每个账号的最大重试次数
# 读取原始文件中的所有行
with open(txt, 'r') as file:
    lines = file.readlines()

# 记录需要删除的账号密码对的索引
failed_indices = set()
# 删除的账号密码对的数量
deleted_count = 0
# 尝试登录并检查结果
for i in range(0, len(lines), 2):  # 每两行处理一次，账号和密码
    date, date1 = lines[i].strip(), lines[i + 1].strip()

    if i in failed_indices:  # 如果这个索引已经被标记为失败，跳过
        continue
    retries = 0  # 当前账号的重试次数

    while retries < max_retries:
        try:
            # 登录
            url = "https://" + date.strip('\n') + hz + "/user/ajax.php?act=login"
            payload = "user=" + date.strip('\n') + "&pass=" + date1.strip('\n')
            headers = {
                'Origin': "https://" + date.strip('\n') + hz,
                'Referer': "https://" + date.strip('\n') + hz + "/user/login.php",
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            response = requests.post(url, headers=headers, data=payload)
            # print(date.strip('\n'))
            # print(response.text)
            a += 1
            logger.info("账号: %s", "第{}个   ".format(a) + date.strip('\n'))
            logger.info("响应内容: %s", response.text)
            login_fail = response.text.find("用户名或密码不正确！")
            if login_fail != -1:
                failed_indices.add(i)  # 记录失败的账号密码对的索引
                deleted_count += 1  # 增加删除计数
                break  # 登录失败，跳过这次迭代

            # 获取基本cookie
            cookie = response.cookies
            PHPSESSID = list(cookie.values())[0]
            user_token = list(cookie.values())[1]
            mysid = list(cookie.values())[2]

            url = "https://" + date.strip('\n') + hz + "/user/qiandao.php"

            payload = {}
            headers = {
                'authority': date.strip('\n') + hz,
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                'cache-control': 'no-cache',
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

            response = requests.get(url, headers=headers, data=payload)

            start_index = response.text.find(',(') + 1
            end_index = response.text.find(');', start_index)

            if start_index != -1 and end_index != -1:
                string = response.text[start_index:end_index]
                cookiess = string
                sec_defend = js2py.eval_js(cookiess)

            # sec_defend有效化
            url = "https://" + date.strip('\n') + hz + "/user/qiandao.php"

            headers[
                'cookie'] = "mysid=" + mysid + "; user_token=" + user_token + "; PHPSESSID=" + PHPSESSID + "; sec_defend=" + sec_defend + "; counter=1; _aihecong_chat_visibility=true"

            response = requests.get(url, headers=headers, data=payload)

            # 签到
            url = "https://" + date.strip('\n') + hz + "/user/ajax_user.php?act=qiandao"
            headers['Referer'] = "https://" + date.strip('\n') + hz + "/user/qiandao.php"

            response = requests.get(url, headers=headers, data=payload)
            logger.info("签到状态: %s", response.json())
            msg = msg + "\n\n" + str(a) + "   " + date

            break  # 成功执行，退出重试循环

        except requests.exceptions.RequestException as e:
            retries += 1
            logger.info("运行状态: %s", f"Request failed: {e}. Retrying {retries}/{max_retries}")
            if retries == max_retries:
                logger.error("连续5次请求失败，停止运行")
                exit()
# 重新写入文件，跳过失败的账号密码对
with open(txt, 'w') as file:
    for i in range(0, len(lines), 2):
        if i not in failed_indices:
            file.write(lines[i] + lines[i + 1])  # 写入成功的账号密码对
logger.info(f"处理完成，失败的账号密码已被删除。共删除了 {deleted_count} 个账号密码对。")

# print(f"处理完成，失败的账号密码已被删除。共删除了 {deleted_count} 个账号密码对。")
msg = msg + "\n\n" + "共删除了 {} 个账号密码对".format(deleted_count)
# notify.pushplus_bot("签到通知", msg)
# print(msg)

# def post_weichat_2():
#     token = os.getenv('ANPUSH_TOKEN')
#     if not token:
#         logger.error("ANPUSH_TOKEN is not set.")
#         return

#     url = "https://api.anpush.com/push/"+token
#     # 从环境变量中获取token
    
   
#     # post发送的字典参数
#     data_dict = {
#         'title': '签到002',
#         'content': msg,  # 确保变量在此处之前已经被定义
#         "channel": "56466"
#     }
#     headers = {
#     "Content-Type": "application/x-www-form-urlencoded"
#     }
#     r = requests.post(url, headers=headers, data=data_dict)  # 发起请求
#     print(r.text)
#     logger.info("推送状态: %s", r.text)

# if __name__ == '__main__':
#     post_weichat_2()

def send_webhook(content):
    token = os.getenv('WEBHOOK')
    webhook_url = token   # 请在这里填入你的key
    headers = {'Content-Type': 'application/json'}
    payload = {
        "msgtype": "text",
        "text": {
            "content": content
        }
    }

    try:
        response = requests.post(webhook_url, json=payload, headers=headers)
        if response.json().get('errcode') == 0:
            return response.json()  # 如果请求成功，返回响应数据
        else:
            raise Exception(response.json().get('errmsg', '发送失败'))
    except Exception as e:
        print(f"An error occurred: {e}")


# 使用函数示例
content = "这里是你想要发送的消息内容"
result = send_webhook(msg)
print(result)
logger.info("推送状态: %s", result)
