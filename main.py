import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import time
import argparse

def main(usr, pw):
    client = requests.Session()
    login_url = "https://w1.v2free.net/auth/login"
    sign_url = "https://w1.v2free.net/user/checkin"
    data = {
        "email": usr,
        "passwd": pw,
        "code": "",
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/76.0",
        "Referer": "https://w1.v2free.net/auth/login",
    }
    client.post(login_url, data=data, headers=headers)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/76.0",
        "Referer": "https://w1.v2free.net/user",
    }
    response = client.post(sign_url, headers=headers).json()
    print(response)

    msg = usr + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + response['msg']
    if response['ret'] == 1:
        msg +="剩余流量："+response['trafficInfo']['unUsedTraffic']
    return msg




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
    parser.add_argument('--username', type=str, help='账号')
    parser.add_argument('--password', type=str, help='密码')
    parser.add_argument('--remail', type=str, help='接收邮箱')
    parser.add_argument('--semail', type=str, help='发送邮箱')
    parser.add_argument('--secode', type=str, help='发送密码')
    args = parser.parse_args()
    msg = main(args.username,args.password)
    print(msg)
    send(info=msg,mail=[args.semail,args.secode],receivers=args.remail)

