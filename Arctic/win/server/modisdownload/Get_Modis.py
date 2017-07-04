#!/usr/bin/python
# -*- coding: utf-8 -*-
import ftplib
import os
import socket
import datetime
import time
import sys
import shutil
import threading
import collections
import numpy as np

HOST = 'ladsweb.nascom.nasa.gov'

class Range():
    def __init__(self, EastBoundingCoord, WestBoundingCoord, SouthBoundingCoord, NorthBoundingCoord):
        self.EastBoundingCoord = EastBoundingCoord
        self.WestBoundingCoord = WestBoundingCoord
        self.SouthBoundingCoord = SouthBoundingCoord
        self.NorthBoundingCoord = NorthBoundingCoord

def downloaded_info_from_FTP_new(DIRN, FILE, save_file_name, Finish_Modis_data = ""):
    print('*** exec wget '+ 'ftp://'+HOST+'/'+DIRN+'/'+FILE)    
    os.popen('wget '+ 'ftp://'+HOST+'/'+DIRN+'/'+FILE)
    if os.path.exists(FILE):
        print('*** exec mv '+ os.getcwd() + '/'+FILE + ' '+save_file_name+FILE)
        os.popen('mv '+ os.getcwd() + '/'+FILE + ' '+save_file_name+FILE)
        return
    else:
        print('*** No such file ' + FILE)
        return -1
    


def downloaded_info_from_FTP(DIRN, FILE, save_file_name, Finish_Modis_data = ""):

    try:
        f = ftplib.FTP(HOST)
    except:
        print('ERROR:cannot reach " %s"' % HOST)
        return

    print('***Connected to host "%s"' % HOST)

    try:
        f.login()
    except:
        print('ERROR: cannot login anonymously')
        # f.quit()
        return

    print('*** Logged in as "anonymously"')
 
    try:
        f.cwd(DIRN)
        list_name = f.nlst()
    except:
        canot_download_file = DIRN+'/'+FILE
        print('ERRORL cannot CD to "%s"' % canot_download_file)
        f.quit()
        return

    print('*** Changed to "%s" folder' % DIRN)

    try:
        file_name = get_name(list_name,FILE)
        if file_name == -1:
            print('Warning: cannot find file "%s", Continue to find the previous day\'s data' % FILE)
            return -1
        if file_name==False:
            f.quit()
            print('ERROR: cannot find file "%s"' % FILE)
            return
        save_file_name_w = save_file_name + file_name + ".w"

        print('*** Downloading "%s" ***' % file_name)

        f.retrbinary('RETR %s' % file_name, open(save_file_name_w, 'wb').write)
    except Exception, e:
        print('ERROR: cannot read file "%s"' % file_name)
        print Exception,':',e
    else:
        print('*** Downloaded "%s" to Data' % file_name)
        save_file_name_new = save_file_name + file_name
        try:
            os.rename(save_file_name_w, save_file_name_new)
        except:
            print("Rename error")
        file_flag = file_name.split(".")[-1]
        if file_flag == 'hdf':
            try:
                Finish_file_object = open(Finish_Modis_data, 'a')
                try:
                    Finish_file_object.write(file_name+'\n')
                except:
                    print("Warning: write error")
                finally:
                    Finish_file_object.close()
            except:
                print("Warning: can’t open file")
        f.quit()
    return


def get_name(list_name, FILE):
    flag_name = FILE.split('.')[-1]
    if flag_name == 'txt':
        for txt in list_name:
            if (txt==FILE):
                return FILE
        return -1
    for line in list_name:
        file_name = line.split('.')[-2]
        set_file_name = str(line).replace(file_name,'*')
        if(set_file_name==FILE):
            return str(line)
    return False


def downloaded_Modis_from_FTP(Save_data_name, download_Modis_name_cover, download_Modis_name_intersect ,Modis_ftp_name, modis_name_cover,
                              modis_name_intersect, Finish_Modis_data, year, postion):
    del_Modis_files(download_Modis_name_cover,Save_data_name, modis_name_cover, Finish_Modis_data)
    file_object = open(download_Modis_name_cover, 'r')

    #Finish_Modis_data list
    Finish_Modis_name = open(Finish_Modis_data, 'r')
    Finish_modis_list = []
    for line in Finish_Modis_name:
        file_name = str(line).replace(str(line).split(".")[4],'*')
        Finish_modis_list.append(file_name.strip('\n'))
    Finish_Modis_name.close()

    #Download cover modis data
    cntDict = {}
    for line in file_object:
        modis_file_name = str(line).strip('\n')
        file_name_arr = modis_file_name.split('.')
        str_time = file_name_arr[1].replace(year,'.').split('.')[1] + file_name_arr[2]
        New_time = int(str_time)
        cntDict[New_time] = modis_file_name
    keys = list(cntDict.keys())
    keys.sort(reverse = True)
    for key in keys:
        file_name_arr = cntDict[key].split('.')
        se_name = file_name_arr[1].replace(year,'.').split('.')[-1]
        ftp_name = Modis_ftp_name + '/' + se_name
        if cntDict[key] in Finish_modis_list:
            print('*** Have downloaded "%s" ' % cntDict[key])
            return True
        downloaded_info_from_FTP(ftp_name, cntDict[key], Save_data_name, Finish_Modis_data)
        FileNames=os.listdir(Save_data_name)
        if len(FileNames)>0:
            for fn in FileNames:
                Modis_name = fn.strip('\n').replace(fn.strip('\n').split('.')[-2],'*')
                if Modis_name.split('.')[-1]=='hdf':
                    file_n = Save_data_name+'/'+fn
                    if os.path.getsize(file_n)<83886080:
                        os.remove(file_n)
                    else:
                        file_object.close()
                        return True
    file_object.close()

    #if cover modis data can't find then download intersect modis data
    del_Modis_files(download_Modis_name_intersect,Save_data_name, modis_name_intersect, Finish_Modis_data)
    file_object_intersect = open(download_Modis_name_intersect, 'r')
    cntDict_intersect = {}
    for line in file_object_intersect:
        modis_file_name = str(line).strip('\n')
        file_name_arr = modis_file_name.split('.')
        str_time = file_name_arr[1].replace(year,'.').split('.')[1] + file_name_arr[2]
        New_time = int(str_time)
        cntDict_intersect[New_time] = modis_file_name
    keys = list(cntDict_intersect.keys())
    keys.sort(reverse = True)
    hdf_list = []
    M_n,M_s = int(postion.NorthBoundingCoord),int(postion.SouthBoundingCoord)
    M_l, M_r = trans(postion.WestBoundingCoord, postion.EastBoundingCoord)
    x = M_r - M_l
    y = M_n - M_s
    A = np.zeros((x,y))
    for key in keys:
        file_name_arr = cntDict_intersect[key].split('.')
        se_name = file_name_arr[1].replace(year,'.').split('.')[-1]
        ftp_name = Modis_ftp_name + '/' + se_name
        if cntDict_intersect[key] in Finish_modis_list:
            A = Cal_intersect(A,cntDict_intersect[key],M_l, M_r, M_n, M_s,x,y,modis_name_intersect)
            print('*** Have downloaded "%s" ' % cntDict_intersect[key])
        else:
            downloaded_info_from_FTP(ftp_name, cntDict_intersect[key], Save_data_name, Finish_Modis_data)
            FileNames=os.listdir(Save_data_name)
            if (len(FileNames)>0):
                for fn in FileNames:
                    Modis_name = fn.strip('\n').replace(fn.strip('\n').split('.')[-2],'*')
                    if Modis_name.split('.')[-1]=='hdf' and Modis_name not in hdf_list:
                        file_n = Save_data_name+'/'+fn
                        if os.path.getsize(file_n)<83886080:
                            os.remove(file_n)
                        else:
                            hdf_list.append(Modis_name)
                            A = Cal_intersect(A,Modis_name,M_l, M_r, M_n, M_s,x,y,modis_name_intersect)
        if len(A[np.where(A==0)])==0:
            return True
    file_object_intersect.close()
    return False

def Cal_intersect(A,Modis_name,M_l, M_r, M_n, M_s,x,y,modis_name_intersect):
    intersect_file = open(modis_name_intersect,'r')
    for inter_file in intersect_file:
        file_name_arr = inter_file.strip('\n').split(',')
        file_name = file_name_arr[0]
        if file_name == Modis_name:
            M_l_c, M_r_c = trans(float(file_name_arr[2]), float(file_name_arr[1]))
            M_n_c = float(file_name_arr[4])
            M_s_c = float(file_name_arr[3])
            J_r,J_l,W_s,W_n = flag_lrns(M_l_c, M_r_c,M_n_c, M_s_c, M_l, M_r,M_n, M_s)
            for i in range(x):
                for j in range(y):
                    AJ = i + M_l
                    AN = y - j - 1 + M_s
                    if J_l <= AJ <= J_r and W_s <= AN <= W_n:
                        A[i,j]=1
            break
    intersect_file.close()
    return A



def flag_lrns(M_l_c, M_r_c,M_n_c, M_s_c, M_l, M_r,M_n, M_s):
    new_l = int(min(M_l,M_l_c))
    new_s = int(min( M_s,M_s_c))
    new_n = int(max( M_n,M_n_c))
    new_r = int(max(M_r_c,M_r))
    new_x = new_r - new_l
    new_y = new_n - new_s
    W_s,W_n,J_r,J_l = 100,-100,-10,1500
    for i in range(new_x):
        for j in range(new_y):
            J = new_l + i
            W = new_y - j - 1 + new_s
            if M_s <= W <= M_n and M_s_c <= W <= M_n_c and M_l <= J <= M_r and M_l_c <= J <= M_r_c:
                if W_s > W:
                    W_s = W
                if W_n < W:
                    W_n = W
                if J_r < J:
                    J_r = J
                if J_l > J:
                    J_l = J
    return J_r,J_l,W_s,W_n

def del_Modis_files(download_Modis_name, path, modis_list_file_name, Finish_Modis_data):
    modie_object = open(modis_list_file_name, 'r')
    if os.path.exists(Finish_Modis_data)==False:
        f = open(Finish_Modis_data, 'w')
        f.close()
    Finish_Modis_name = open(Finish_Modis_data, 'r')
    modis_list = []
    Finish_modis_list = []
    for line in Finish_Modis_name:
        file_name = str(line).replace(str(line).split(".")[4],'*')
        Finish_modis_list.append(file_name.strip('\n'))
    Finish_Modis_name.close()
    for line in modie_object:
        modis_list.append(str(line).strip('\n').split(',')[0])
    modie_object.close()
    download_Modis_file_name = open(download_Modis_name, 'w')
    # for root , dirs, files in os.walk(path):
    #     for name in files:
    #         os.remove(os.path.join(root, name))
    for file_Modis in modis_list:
        download_Modis_file_name.write(file_Modis+'\n')
    download_Modis_file_name.close()


def del_txt_files(path):
    for root, dirs, files in os.walk(path):
        for name in files:
            os.remove(os.path.join(root, name))



def trans(l, r):
    if l < 0:
        if r > l:
            l += 360
            r += 360
        else:
            l += 360
            r += 720
    else:
        if r < l:
            r += 360
    return int(l), int(r)

def check_EW_cover(WestBoundingCoord, EastBoundingCoord, WCoord, ECoord):
    l1, r1 = trans(WestBoundingCoord, EastBoundingCoord)
    l2, r2 = trans(WCoord, ECoord)

    if l2 <= l1 and r2 >= r1:
        return True
    if l1 <= l2 and r1 >= r2:
        return True
    return  False



def check_NS_cover(n, s, Sd, Nd):
    if Sd<=s and Nd>=n:
        return True
    if s<=Sd and Nd<=n:
        return True
    return False



def check_EW_intersect(WestBoundingCoord, EastBoundingCoord, WCoord, ECoord):
    l1, r1 = trans(WestBoundingCoord, EastBoundingCoord)
    l2, r2 = trans(WCoord, ECoord)
    return True if (l1 < l2 < r1) or (l1 < r2 < r1) else False

def check_NS_intersect(n, s, d):
    if d < n and d > s:
        return True
    return False


def get_Modis_file_name(modis_name_cover,modis_name_intersect,modis_list_file_name,postion):
    file_object_cover = open(modis_name_cover, 'w')
    file_object_intersect = open(modis_name_intersect, 'w')
    for file in os.listdir(modis_list_file_name):
        f = open(modis_list_file_name+file, "r")
        line = f.readline().replace('\n', '')
        line = f.readline().replace('\n', '')
        line = f.readline().replace('\n', '')
        while True:
            line = f.readline().replace('\n', '')
            if line:
                tmp = line.split(',')
                ECoord = float(tmp[5])
                NCoord = float(tmp[6])
                SCoord = float(tmp[7])
                WCoord = float(tmp[8])
                if tmp[4]!="N":
                    if check_EW_cover(postion.WestBoundingCoord, postion.EastBoundingCoord, WCoord, ECoord) and  \
                            check_NS_cover(postion.NorthBoundingCoord, postion.SouthBoundingCoord, SCoord,NCoord):
                        str0 = tmp[0]
                        str1 = str0.replace("MOD03","MOD02QKM")
                        strall = str1.split(".")
                        str2 = str1.replace(strall[4],'*')
                        str2 = str2 + ',' + str(ECoord) + ',' + str(WCoord) + ',' + str(SCoord) + ',' + str(NCoord)
                        file_object_cover.write(str2+'\n')
                    elif check_EW_intersect(postion.WestBoundingCoord, postion.EastBoundingCoord, WCoord, ECoord) and  \
                            (check_NS_intersect(postion.NorthBoundingCoord, postion.SouthBoundingCoord, SCoord) or
                                 check_NS_intersect(postion.NorthBoundingCoord, postion.SouthBoundingCoord, NCoord) or
                                 check_NS_cover(postion.NorthBoundingCoord, postion.SouthBoundingCoord, SCoord,NCoord)) or \
                                    (check_NS_intersect(postion.NorthBoundingCoord, postion.SouthBoundingCoord, SCoord) or
                                         check_NS_intersect(postion.NorthBoundingCoord, postion.SouthBoundingCoord, NCoord)) and \
                                    (check_EW_intersect(postion.WestBoundingCoord, postion.EastBoundingCoord, WCoord, ECoord) or
                                         check_EW_cover(postion.WestBoundingCoord, postion.EastBoundingCoord, WCoord, ECoord)):
                        str0 = tmp[0]
                        str1 = str0.replace("MOD03","MOD02QKM")
                        strall = str1.split(".")
                        str2 = str1.replace(strall[4],'*')
                        str2 = str2 + ',' + str(ECoord) + ',' + str(WCoord) + ',' + str(SCoord) + ',' + str(NCoord)
                        file_object_intersect.write(str2+'\n')
            else:
                break
        f.close()
    file_object_cover.close( )
    file_object_intersect.close( )

def maindownloading(EastBoundingCoord, WestBoundingCoord, SouthBoundingCoord, NorthBoundingCoord):
    now = datetime.datetime.now()
    print('*** Current time: "%s"' % now)
    postion = Range(EastBoundingCoord, WestBoundingCoord, SouthBoundingCoord, NorthBoundingCoord)
    # print('*** Please Enter the latitude and longitude and separated by spaces:')
    # try:
    #     EastBoundingCoord, WestBoundingCoord, SouthBoundingCoord, NorthBoundingCoord = \
    #         map(float, input('***EastBoundingCoord, WestBoundingCoord, SouthBoundingCoord, NorthBoundingCoord:\n').split())
    # except:
    #     print("Input error")

    # print("***Enter Successful***")

    save_txt_name = os.getcwd() + '/modisdownload/Data/Modis_information_file/'
    modis_list_file_name = os.getcwd() + '/modisdownload/Data/Modis_information_file/'
    modis_name_cover = os.getcwd() + '/modisdownload/Data/Modis_filename_cover.txt'
    modis_name_intersect = os.getcwd() + '/modisdownload/Data/Modis_filename_intersect.txt'
    download_Modis_name_cover = os.getcwd() + '/modisdownload/Data/Download_Modis_filename_cover.txt'
    download_Modis_name_intersect = os.getcwd() + '/modisdownload/Data/Download_Modis_filename_intersect.txt'
    save_data_name = os.getcwd() + '/modisdownload/Data/Modis_data/'
    Finish_Modis_data = os.getcwd() + '/modisdownload/Data/Finish_modis_info.txt'

    today = datetime.date.today()
    year = today.strftime("%Y")
    DIRN = 'geoMeta/6/TERRA/'+year
    modis_ftp_name='allData/6/MOD02QKM/'+year
    info_FILE = 'MOD03_'+ str(today) +'.txt'
    del_txt_files(save_txt_name)
    downloaded_info_from_FTP(DIRN,info_FILE,save_txt_name)

    yesterday = today - datetime.timedelta(days=1)
    year = yesterday.strftime("%Y")
    DIRN = 'geoMeta/6/TERRA/' + year
    modis_ftp_name = 'allData/6/MOD02QKM/' + year
    info_FILE = 'MOD03_' + str(yesterday) + '.txt'
    downloaded_info_from_FTP(DIRN, info_FILE, save_txt_name)

    # before_yesterday = today - datetime.timedelta(days=2)
    # year = before_yesterday.strftime("%Y")
    # DIRN = 'geoMeta/6/TERRA/' + year
    # modis_ftp_name = 'allData/6/MOD02QKM/' + year
    # info_FILE = 'MOD03_' + str(before_yesterday) + '.txt'
    # downloaded_info_from_FTP(DIRN, info_FILE, save_txt_name)

    # print '*****judge exists******'
    if os.path.exists(Finish_Modis_data):
        Finish_day = time.strftime('%j', time.localtime(os.stat(Finish_Modis_data).st_mtime))
        Cur_day = time.strftime('%j',time.localtime(time.time()))
        if abs(int(Finish_day) - int(Cur_day))>0:
            os.remove(Finish_Modis_data)

    # print '************get modis file name****************'
    get_Modis_file_name(modis_name_cover,modis_name_intersect, modis_list_file_name, postion)
    # print '*****************download modis info from ftp******************'
    B = downloaded_Modis_from_FTP(save_data_name, download_Modis_name_cover, download_Modis_name_intersect,
                                  modis_ftp_name, modis_name_cover, modis_name_intersect, Finish_Modis_data, year, postion)

    FileNames=os.listdir(save_data_name)
    if len(FileNames)>0:
        for fn in FileNames:
            Modis_name = fn.strip('\n').replace(fn.strip('\n').split('.')[-2],'*')
            if Modis_name.split('.')[-1]=='hdf':
                if B==False:
                    print("Complete to download the latest data, but data DOES NOT cover the scope")
                else:
                    print("Complete to download the latest data, and data CAN cover the scope")
                break
    else:
        if B==True:
            print('Have downloaded the latest data and no update now')
        else:
            print("Fail to download")
    return B
    #如果中途人为终止程序或断网，请直接使用下载好的数据或者删除下载好的数据并将对应的Finish_modis_info.txt里面的Modis文件名删除
    #一天之内0点到24点，若下载不同经纬度的范围的modis图像请手动清空Finish_modis_info.txt文件，若不清空，下载的数据不能保证最新

if __name__ == '__main__':
    now = datetime.datetime.now()
    print('*** Current time: "%s"' % now)
    print('*** Please Enter the latitude and longitude and separated by spaces:')
    try:
        EastBoundingCoord, WestBoundingCoord, SouthBoundingCoord, NorthBoundingCoord = \
            map(float, input('***EastBoundingCoord, WestBoundingCoord, SouthBoundingCoord, NorthBoundingCoord:\n').split())
    except:
        print("Input error")

    print("***Enter Successful***")

    save_txt_name = 'Data/Modis_information_file/'
    modis_list_file_name = 'Data/Modis_information_file/'
    modis_name_cover = 'Data/Modis_filename_cover.txt'
    modis_name_intersect = 'Data/Modis_filename_intersect.txt'
    download_Modis_name_cover = 'Data/Download_Modis_filename_cover.txt'
    download_Modis_name_intersect = 'Data/Download_Modis_filename_intersect.txt'
    save_data_name = 'Data/Modis_data/'
    Finish_Modis_data = 'Data/Finish_modis_info.txt'

    today = datetime.date.today()
    year = today.strftime("%Y")
    DIRN = 'geoMeta/6/TERRA/'+year
    modis_ftp_name='allData/6/MOD02QKM/'+year
    info_FILE = 'MOD03_'+ str(today) +'.txt'
    del_txt_files(save_txt_name)
    downloaded_info_from_FTP(DIRN,info_FILE,save_txt_name)

    yesterday = today - datetime.timedelta(days=1)
    year = yesterday.strftime("%Y")
    DIRN = 'geoMeta/6/TERRA/' + year
    modis_ftp_name = 'allData/6/MOD02QKM/' + year
    info_FILE = 'MOD03_' + str(yesterday) + '.txt'
    downloaded_info_from_FTP(DIRN, info_FILE, save_txt_name)


    if os.path.exists(Finish_Modis_data):
        Finish_day = time.strftime('%j', time.localtime(os.stat(Finish_Modis_data).st_mtime))
        Cur_day = time.strftime('%j',time.localtime(time.time()))
        if abs(int(Finish_day) - int(Cur_day))>0:
            os.remove(Finish_Modis_data)

    get_Modis_file_name(modis_name_cover,modis_name_intersect, modis_list_file_name, EastBoundingCoord, WestBoundingCoord, SouthBoundingCoord, NorthBoundingCoord)
    B = downloaded_Modis_from_FTP(save_data_name, download_Modis_name_cover, download_Modis_name_intersect ,modis_ftp_name, modis_name_cover, modis_name_intersect, Finish_Modis_data, year,  EastBoundingCoord, WestBoundingCoord, SouthBoundingCoord, NorthBoundingCoord)

    FileNames=os.listdir(save_data_name)
    if len(FileNames)>0:
        for fn in FileNames:
            Modis_name = fn.strip('\n').replace(fn.strip('\n').split('.')[-2],'*')
            if Modis_name.split('.')[-1]=='hdf':
                if B==False:
                    print("完成最新数据下载,但数据不能覆盖该范围")
                else:
                    print("完成最新数据下载，数据完全覆盖该范围")
                break
    else:
        if B==True:
            print('已经下载过最新数据,暂无数据更新')
        else:
            print("数据下载失败")
    #如果中途人为终止程序或断网，请直接使用下载好的数据或者删除下载好的数据并将对应的Finish_modis_info.txt里面的Modis文件名删除
    #一天之内0点到24点，若下载不同经纬度的范围的modis图像请手动清空Finish_modis_info.txt文件，若不清空，下载的数据不能保证最新




