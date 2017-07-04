import smtplib
import zipfile
import tempfile
from email import encoders
from email.message import Message
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
import os
def zip_dir(zf,dirname):
    filelist = []
    if os.path.isfile(dirname):
        filelist.append(dirname)
    else :
        for root, dirs, files in os.walk(dirname):
            for name in files:
                filelist.append(os.path.join(root, name))

    zip = zipfile.ZipFile(zf, "w", zipfile.zlib.DEFLATED)
    for tar in filelist:
        print('tar:', tar)
        print('dirname:', dirname)
        arcname = tar[len(dirname) + 1:]
        #print arcname
        print('arcname: ', arcname)
        zip.write(tar,arcname)
    zip.close()

def send_file_zipped(the_file, recipients, passwd, sender, num):
    zf = tempfile.TemporaryFile(prefix='mail', suffix='.zip')
    # zip = zipfile.ZipFile(zf, 'w')
    # zip.write(the_file)
    # zip.close()
    # zf = zipfile.ZipFile('south.zip', "w", zipfile.zlib.DEFLATED)
    zip_dir(zf,the_file)
    zf.seek(0)
    mail_host = "lamda.nju.edu.cn"
    # Create the message
    themsg = MIMEMultipart()

    import time
    statinfo = os.stat('range.txt')
    c_time = time.localtime(statinfo.st_ctime)
    l_time = ''
    for i in range(0, 5):
        l_time = l_time + '{:02d}'.format(c_time[i])

    themsg['Subject'] = '[south]File %s' % the_file + ' ' + l_time + str(num)
    print num
    print themsg['Subject']
    themsg['To'] = ', '.join(recipients)
    themsg['From'] = sender
    themsg.preamble = 'I am not using a MIME-aware mail reader.\n'
    msg = MIMEBase('application', 'zip')
    msg.set_payload(zf.read())
    encoders.encode_base64(msg)
    msg.add_header('Content-Disposition', 'attachment',
                   filename=the_file + '.zip')
    themsg.attach(msg)
    themsg = themsg.as_string()

    '''
    # send the message
    smtp = smtplib.SMTP()
    # smtp.connect()
    smtp.login(sender,passwd)

    smtp.sendmail(sender, recipients, themsg)
    smtp.close()
    '''
    smtp = smtplib.SMTP_SSL()
    smtp.connect(mail_host, 465)
    smtp.ehlo()
    smtp.login(sender, passwd)
    smtp.sendmail(sender, recipients, themsg)
    smtp.quit()
# send_file_zipped('test', ['fanying_yt@163.com'], 'fy1259680')
