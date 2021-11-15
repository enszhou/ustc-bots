import requests
from bs4 import BeautifulSoup
import re
import os
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import sys


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, "utf-8").encode(), addr))


def send_mail(subject, message, to_addr):
    from_addr = config["src_email"]
    password = config["src_email_password"]
    smtp_server = "smtp.126.com"

    msg = MIMEText(message, "plain", "utf-8")
    msg["Subject"] = Header(subject, "utf-8").encode()

    msg["From"] = _format_addr("<%s>" % from_addr)
    msg["To"] = _format_addr("<%s>" % to_addr)
    server = smtplib.SMTP_SSL(smtp_server, 465)
    server.login(from_addr, password)
    server.sendmail(from_addr, [from_addr, to_addr], msg.as_string())
    server.quit()


config = {
    "userid": sys.argv[1],
    "password": sys.argv[2],
    "src_email": sys.argv[3],
    "src_email_password": sys.argv[4],
    "dest_email": sys.argv[5],
}


session = requests.session()

url_login = "https://yjs.ustc.edu.cn/default_yjsy.asp"
url_query = "http://yjs.ustc.edu.cn/bgzy/m_bgxk_up.asp"

payload_login = "userid=%s&userpwd=%s" % (config["userid"], config["password"])
payload_query = "queryname=&submit=%25B2%25E9%2B%25D1%25AF"
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
}

session.request("POST", url_login, headers=headers, data=payload_login)
response = session.request("POST", url_query, data=payload_query)

soup = BeautifulSoup(response.content, "lxml")

td = str(soup.find("td", "bt05"))
res = re.search(r"共\d+条记录", td)
span = res.span()
total_num = int(td[span[0] + 1 : span[1] - 3])

tag = str(total_num)

tds = soup.find_all("td", "bt06")
for i in range(1, 62, 12):
    if i >= len(tds):
        break
    tag += "/" + tds[i].string

if not os.path.exists("tag.txt"):
    with open("tag.txt", "w+") as fp:
        fp.write(tag)

with open("tag.txt", "r") as fp:
    old_tag = fp.readline()

if tag != old_tag:
    with open("tag.txt", "w+") as fp:
        fp.write(tag)
    print("Find new report.")
    send_mail("New report", tag, config["dest_email"])
else:
    print("No new report.")
