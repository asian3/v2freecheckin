import requests
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import time
import argparse

BASE_URL = "https://www.v2free.net"  # 新版登录/签到域名

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def main(usr, pw):
    client = requests.Session()
    client.headers.update({"User-Agent": UA})

    # 1. 访问登录页，获取初始 Cookie
    client.get(BASE_URL + "/auth/login")

    # 2. 登录（新版表单字段：email/passwd/code/agree/remember_me）
    login_data = {
        "email": usr,
        "passwd": pw,
        "code": "",
        "agree": "1",       # 新版登录必须携带 agree=1
        "remember_me": "",
    }
    resp = client.post(
        BASE_URL + "/auth/login",
        data=login_data,
        headers={
            "Referer": BASE_URL + "/auth/login",
            "X-Requested-With": "XMLHttpRequest",
        },
    )
    try:
        login_result = resp.json()
    except ValueError:
        return usr + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " 登录失败：返回内容不是 JSON"
    if login_result.get("ret") != 1:
        return usr + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " 登录失败：" + str(login_result.get("msg", resp.text))

    # 3. 签到（接口未变：POST /user/checkin）
    resp = client.post(
        BASE_URL + "/user/checkin",
        headers={
            "Referer": BASE_URL + "/user",
            "X-Requested-With": "XMLHttpRequest",
        },
    )
    try:
        checkin_result = resp.json()
    except ValueError:
        return usr + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " 签到失败：返回内容不是 JSON"

    if checkin_result.get("ret") == 1:
        msg = str(checkin_result.get("msg", "签到成功"))
    else:
        msg = "签到失败：" + str(checkin_result.get("msg", resp.text))

    # 4. 从用户中心页面获取当前流量信息（签到已过/失败时也能拿到）
    info = fetch_user_info(client)
    extra = ""
    if info:
        extra = "，剩余流量：" + info.get("剩余流量", "?") + "，今日已用：" + info.get("今日已用", "?")
    return usr + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " " + msg + extra


def fetch_user_info(client):
    """登录后读取用户中心页面的账号流量信息"""
    try:
        html = client.get(BASE_URL + "/user").text
        info = {}
        m = re.search(r'id="remain"[^>]*>([^<]+)<', html)
        if m:
            info["剩余流量"] = m.group(1).strip()
        m = re.search(r'今日已用:\s*<a[^>]*>([^<]+)<', html)
        if m:
            info["今日已用"] = m.group(1).strip()
        return info
    except Exception:
        return {}




# 发送到我的邮箱
def send(info, mail, receivers, subject='', imgpth=''):
    #if info or mail[0] or mail[1] or receivers == '': return
    sender,key = mail
    message = MIMEMultipart('mixed')
    if subject == "": subject = info
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = receivers
    try:  # 尝试发送图片和文字
        fp = open(imgpth, 'rb')  # 打开文件
        msgImage = MIMEImage(fp.read())  # 创建MIMEImage对象，读取图片内容并作为参数
        fp.close()  # 关闭文件
        msgImage.add_header('Content-ID', '<image1>')  # 指定图片文件的Content-ID，imgid，<img>标签中的src用到
        html_img = f'<p>{info}<br><img src="cid:image1"></br></p>'  # html格式添加图片
        message.attach(msgImage)
        message.attach(MIMEText(html_img, 'html', 'utf-8'))  # 添加到邮件正文
    except:  # 只发送文字
        content = MIMEText('%s' % info)
        message.attach(content)

    try:
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)
        server.login(sender, key)
        server.sendmail(sender, receivers, message.as_string())
        server.quit()
        # print("send OK")
    except smtplib.SMTPException as e:
        print(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='V2free签到脚本')
    parser.add_argument('--username', type=str,help='账号')
    parser.add_argument('--password', type=str, help='密码')
    parser.add_argument('--remail', type=str, help='接收邮箱')
    parser.add_argument('--semail', type=str, help='发送邮箱')
    parser.add_argument('--secode', type=str, help='发送密码')
    args = parser.parse_args()
    msg = main(args.username,args.password)
    print(msg)
    if int(time.strftime("%d", time.localtime()))% 3== 0:
        send(info=msg,mail=[args.semail,args.secode],receivers=args.remail)

