#!/usr/bin/env python
# -*- coding: utf-8 -*-
import poplib
import email
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
import time
# 输入邮件地址, 口令和POP3服务器地址:
'''
email = input('Email: ')
password = input('Password: ')
pop3_server = input('POP3 server: ')
'''
import imaplib
import re


def LoginMail(hostname, user, password):
    r = imaplib.IMAP4_SSL(hostname)
    r.login(user, password)
    x, y = r.status('INBOX', '(MESSAGES UNSEEN)')
    unseennum  = y[0][-2] - 48
    return unseennum


def guess_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset

def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value

def print_info(msg, indent=0):
    if indent == 0:
        for header in ['From', 'To', 'Subject']:
            value = msg.get(header, '')
            if value:
                if header=='Subject':
                    value = decode_str(value)
                    # print('subject', value)
                    if value[0:7] == '[south]':
                        longitati = value
                        # print('longitati', longitati)
                        return longitati
                else:
                    hdr, addr = parseaddr(value)
                    name = decode_str(hdr)
                    value = u'%s <%s>' % (name, addr)
            # print('%s%s: %s' % ('  ' * indent, header, value))
    if (msg.is_multipart()):
        parts = msg.get_payload()
        for n, part in enumerate(parts):
            # print('%spart %s' % ('  ' * indent, n))
            # print('%s--------------------' % ('  ' * indent))
            print_info(part, indent + 1)
    else:
        content_type = msg.get_content_type()
        if content_type=='text/plain' or content_type=='text/html':
            content = msg.get_payload(decode=True)
            charset = guess_charset(msg)
            if charset:
                content = content.decode(charset)
            # print('%sText: %s' % ('  ' * indent, content + '...'))
        # else:
            # print('%sAttachment: %s' % ('  ' * indent, content_type))

    return None

# 连接到POP3服务器:

def checkemail(email,password,pop3_server,prenum):
    server = poplib.POP3_SSL(pop3_server, '995')
    # server = poplib.POP3(pop3_server)
    # 可以打开或关闭调试信息:
    # server.set_debuglevel(1)
    # 可选:打印POP3服务器的欢迎文字:
    # print(time.localtime(time.time()))
    # print(server.getwelcome())
    # 身份认证:
    server.user(email)
    server.pass_(password)
    # stat()返回邮件数量和占用空间:
    # print('Messages: %s. Size: %s' % server.stat())
    # list()返回所有邮件的编号:
    resp, mails, octets = server.list()
    # 可以查看返回的列表类似['1 82923', '2 2184', ...]
    # print(mails)
    # 获取最新一封邮件, 注意索引号从1开始:
    index = len(mails)
    if index == prenum:
        return index, None
	
    unseennum = index - prenum
    print('num of mails:', index)
    print('unseennum:', unseennum)
    for j in range(unseennum):
        ii = index - j
        # print(ii)
        try:
            resp, lines, octets = server.retr(ii)
            for i in range(len(lines)):

                lines[i] = lines[i].decode()
	       	       
                msg_content = '\r\n'.join(lines)
                # 稍后解析出邮件:
                msg = Parser().parsestr(msg_content)
                # subj = print_info(msg, specified_email)
                subj = print_info(msg)
                if subj != None:
                    print(subj)
                    for i in range(index):
		                server.dele(i+1)
                    server.quit()
                    return index,subj
        except Exception as e:
            # raise('exception:', e)
            print('exception:', e)
            continue

	# 可以根据邮件索引号直接从服务器删除邮件:
	server.dele(index)
	# 关闭连接:
	server.quit()
	return index,None

if __name__ == '__main__':
    checkemail('PolarReceiveReq@lamda.nju.edu.cn','PolarEmail1234','210.28.132.67',0)

