import os
import time
import argparse
import shutil
from getemail import checkemail
import modisdownload.Get_Modis
import modisProcessing.main_processing

def print_ts(message):
    print("[%s] %s"%(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), message))

def run(interval, command):
    print_ts("-"*100)
    print_ts("Command %s"%command)
    print_ts("Starting every %s seconds."%interval)
    print_ts("-"*100)
    start = True
    while True:
        try:
            # sleep for the remaining seconds of interval
            time_remaining = interval-time.time()%interval
            print_ts("Sleeping until %s (%s seconds)..."%((time.ctime(time.time()+time_remaining)), time_remaining))
            time.sleep(time_remaining)
            print_ts("Starting command.")
            # execute the command
            # unseennum = LoginMail('imap.163.com', 'fanying_yt@163.com', 'fy1259680')
	   
            if start == True:
                # status = os.system(command)
                prenum = 0   
                start = False
                            
            prenum, subj = checkemail(args.email,args.password,args.pop3_server,prenum)
            if subj != None:
                value = subj[7:]
                print(value)
                values = value.split(' ')
                print(values)
                EastBoundingCoord = float(values[1])
                WestBoundingCoord = float(values[0])
                SouthBoundingCoord = float(values[3])
                NorthBoundingCoord = float(values[2])

                # EastBoundingCoord = 170.0
                # WestBoundingCoord = 165.0
                # SouthBoundingCoord = -70.0
                # NorthBoundingCoord = -65.0

                print(EastBoundingCoord)
                print(WestBoundingCoord)
                print(SouthBoundingCoord)
                print(NorthBoundingCoord)

                modisdownload.Get_Modis.maindownloading(EastBoundingCoord, WestBoundingCoord, SouthBoundingCoord, NorthBoundingCoord)

                # copy .hdf files to folder modisProcessing/MODIS/hdf
                src = os.getcwd() + '\\modisdownload\\Data\\Modis_data\\'
                dst = os.getcwd() + '\\modisProcessing\\MODIS\\hdf\\'

                filelist = []
                
                for dirpath, dirnames, filenames in os.walk(src):
                    for filename in filenames:
                        if filename.startswith('MOD') and filename.endswith('.hdf'):
                            filelist.append('.'.join(filename.split('.')[0:-1]))
                filelist.sort()
                print(filelist)

                newfilename = ''
                
                for filename in filelist:
                    src_file = src + filename + ".hdf"
                    dst_file = dst + filename + ".hdf"
                    if os.path.exists(dst_file):
                        continue
                    else:
                        from shutil import copyfile
                        copyfile(src_file, dst_file)
                
                        print('preprocess file "%s"......' % filename)
                        newfilename = modisProcessing.main_processing.updateRaster(filename, WestBoundingCoord, NorthBoundingCoord, EastBoundingCoord, SouthBoundingCoord)

                zero_mark = False
                if len(filelist) != 0:
                    # clear old files
                    import clearfile
                    clearfile.clear_raster()
                    clearfile.clear_files()
                else:
                    zero_mark = True

                # newfilename = '0_CURRENT_RASTER_1000'
                # from modisProcessing.RasterManagement import cropandmask
                # cropandmask(WestBoundingCoord, NorthBoundingCoord, EastBoundingCoord, SouthBoundingCoord, newfilename)

                # modis file update
                if not zero_mark:
                    fileset = set()
                    for dripath, dirnames, filenames in os.walk('modisProcessing/MODIS/tiff/arcmapWorkspace/'):
                        for filename in filenames:
                            if filename.split('.')[0].endswith('_crop'):
                                fileset.add(filename.split('.')[0])
                    fileset = sorted(fileset, reverse=True)
                    print fileset

                    if os.path.exists('test/'):
                        shutil.rmtree('test/')
                    os.mkdir('test/')
                    # for dripath, dirnames, filenames in os.walk('modisProcessing/MODIS/tiff/arcmapWorkspace/'):
                    #     for filename in filenames:
                    #         if fileset[0] in filename and (not filename.endswith('.tif')):
                    #             print filename
                    #             shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + filename, 'test/' + filename)

                    shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + newfilename + '_crop.lonlat', 'test/' + newfilename + '.lonlat')
                    shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + newfilename + '_crop.prob', 'test/' + newfilename + '.prob')
                    shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + newfilename + '_crop.jpg', 'test/' + newfilename + '.jpg')
                    shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + newfilename + '_crop.cost', 'test/' + newfilename + '.cost')
                    shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + newfilename + '_crop.ice', 'test/' + newfilename + '.ice')

                    import sendemail
                    sendemail.send_file_zipped('test', ['PolarRecieveZip@163.com'], 'PolarEmail1234', 'PolarSendZip@lamda.nju.edu.cn')
                else:
                    print 'no modis file updated'



            print_ts("-"*100)
            # print_ts("Command status = %s."%status)
            
        except Exception as e:
            print(e)

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--email', help = 'email', type = str, default = 'PolarReceiveReq@163.com')
    parser.add_argument('--password', help = 'password', type = str, default = 'PolarEmail1234')
    parser.add_argument('--pop3_server', help = 'pop3_server', type = str, default = 'pop.163.com')
    # parser.add_argument('--specified_email', help = 'specified_email', type = str, default = '1584743373@qq.com')
    args = parser.parse_args()
    interval = 60

    # run(interval,parser)
    # import sendemail
    # sendemail.send_file_zipped('test', ['PolarRecieveZip@lamda.nju.edu.cn'], 'PolarEmail1234', 'PolarSendZip@lamda.nju.edu.cn')

    eastlon = 106
    southlat = -65
    westlon = 86
    northlat = -60
    from transfer import transfer
    ulx, uly, lrx, lry = transfer(westlon, eastlon, northlat, southlat)

    from modisProcessing.RasterManagement import cropandmask
    cropandmask(ulx, uly, lrx, lry, '17_CURRENT_RASTER_250', folder = 'modisProcessing/MODIS/tiff/arcmapWorkspace/')

