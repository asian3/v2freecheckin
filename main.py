import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import time
import argparse


def main(usr, pw):
    url = 'https://w1.v2dns.xyz/user/checkin'
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Content-Length': '0',
        'Cookie': '_ga=GA1.1.1097224415.1644561485; _gcl_au=1.1.1299104476.1644561485; uid=31219; email=shenjie8278%40126.com; key=772b4f245432c928abc93ac4257dbcb1b486aa43ba89d; ip=873971ac1430cbeeed56b9b0a3781c88; expire_in=1676105429; _ga_NC10VPE6SR=GS1.1.1644803702.3.0.1644803704.0; crisp-client%2Fsession%2Fa47ae3dd-53d8-4b15-afae-fb4577f7bcd0=session_625114a8-61e3-4a99-a820-2d65e0b44b67; crisp-client%2Fsocket%2Fa47ae3dd-53d8-4b15-afae-fb4577f7bcd0=0',
        'Host': 'w1.v2dns.xyz',
        'Origin': 'https://w1.v2dns.xyz',
        'Referer': 'https://w1.v2dns.xyz/user/',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36'
    }

    data = {
        "email": usr,
        "passwd": pw,
        "code": "",
    }
    response = requests.post(url=url, data=data, headers=headers).json()

    msg = usr + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + response['msg']
    if response['ret'] == 1:
        msg += '剩余流量:' + str(response['msg']['trafficInfo']['unUsedTraffic'])

    return msg


# 发送到我的邮箱
def send(info, mail, receivers, subject='', imgpth=''):
    if receivers == '': return
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
    send(info=msg,mail=[args.semail,args.secode],receivers=args.remail)

