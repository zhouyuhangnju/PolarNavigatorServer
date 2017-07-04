import os, shutil, time
import gdal
from gdalconst import GA_ReadOnly
from osgeo import osr
import math
import numpy as np
import pickle
from PIL import Image
import scipy.misc


def add2CurrentRaster(filename, folder = 'modisProcessing/MODIS/tiff/'):
    # dst_folder = '../modisPath/data/'
    workspace = folder + 'arcmapWorkspace/'
    if not os.path.exists(workspace):
        os.makedirs(workspace)

    tiff_list = []
    for dripath, dirnames, filenames in os.walk(workspace):
        for workspacefilename in filenames:
            if workspacefilename.endswith('_CURRENT_RASTER_250.tif'):
                tiff_list.append(int(workspacefilename.split('_')[0]))

    if not tiff_list:
        next_no = 0
        shutil.copy(folder+filename, workspace + 'tmp.tif')

        dataset = gdal.Open(workspace +  'tmp.tif', GA_ReadOnly)
        x_size = dataset.RasterXSize # Raster xsize
        y_size = dataset.RasterYSize # Raster ysize
        geo_t = dataset.GetGeoTransform()
        new_ulx = min(geo_t[0], -5000)
        new_uly = max(geo_t[3], 5000)
        new_lrx = max(geo_t[0]+geo_t[1]*x_size, 5000)
        new_lry = min(geo_t[3]+geo_t[5]*y_size, -5000)
        new_x_size = math.ceil((new_lrx-new_ulx)/250.0)
        new_y_size = math.ceil((new_uly-new_lry)/250.0)
        drv = gdal.GetDriverByName('GTiff')
        dest = drv.Create(workspace+str(next_no)+'_CURRENT_RASTER_250.tif', int(new_x_size), int(new_y_size), 1, gdal.GDT_Byte)
        new_geo = (new_ulx, 250.0, 0.0, new_uly, 0.0, -250.0)
        print new_geo
        dest.SetGeoTransform(new_geo)
        dest.SetProjection(dataset.GetProjection())
        gdal.ReprojectImage(dataset, dest, dataset.GetProjection(), dest.GetProjection(), gdal.GRA_NearestNeighbour)
        band = dest.GetRasterBand(1)
        array = band.ReadAsArray()
        array[array==0] = 255
        band.WriteArray(array)
        dataset = None
        os.remove(workspace +  'tmp.tif')
        dest = None
    else:
        curr_no = max(tiff_list)
        next_no = curr_no + 1
        curr_dataset = gdal.Open(workspace+str(curr_no)+'_CURRENT_RASTER_250.tif', GA_ReadOnly)
        curr_x_size = curr_dataset.RasterXSize # Raster xsize
        curr_y_size = curr_dataset.RasterYSize # Raster ysize
        curr_geo_t = curr_dataset.GetGeoTransform()
        curr_ulx = curr_geo_t[0]
        curr_uly = curr_geo_t[3]
        curr_lrx = curr_geo_t[0] + curr_geo_t[1]*curr_x_size
        curr_lry = curr_geo_t[3] + curr_geo_t[5]*curr_y_size
        print (curr_ulx, curr_uly, curr_lrx, curr_lry)

        new_dataset = gdal.Open(folder+filename, GA_ReadOnly)
        new_band = new_dataset.GetRasterBand(1)
        new_array = new_band.ReadAsArray()
        new_x_size = new_dataset.RasterXSize # Raster xsize
        new_y_size = new_dataset.RasterYSize # Raster ysize
        print new_x_size, new_y_size
        new_geo_t = new_dataset.GetGeoTransform()
        new_ulx = new_geo_t[0]
        new_uly = new_geo_t[3]
        new_lrx = new_geo_t[0] + new_geo_t[1]*new_x_size
        new_lry = new_geo_t[3] + new_geo_t[5]*new_y_size
        print (new_ulx, new_uly, new_lrx, new_lry)

        ulx = min(curr_ulx, new_ulx)
        uly = max(curr_uly, new_uly)
        lrx = max(curr_lrx, new_lrx)
        lry = min(curr_lry, new_lry)

        print (ulx, uly, lrx, lry)

        x_size = math.ceil((lrx - ulx)/250.0)
        y_size = math.ceil((uly - lry)/250.0)
        print (x_size, y_size)

        drv = gdal.GetDriverByName('GTiff')
        dest = drv.Create(workspace + str(next_no) + '_CURRENT_RASTER_250.tif', int(x_size), int(y_size), 1, gdal.GDT_Byte)
        geo = (ulx, 250.0, 0.0, uly, 0.0, -250.0)
        print geo
        dest.SetGeoTransform(geo)
        dest.SetProjection(curr_dataset.GetProjection())
        gdal.ReprojectImage(curr_dataset, dest, curr_dataset.GetProjection(), dest.GetProjection(), gdal.GRA_NearestNeighbour)

        band = dest.GetRasterBand(1)
        array = band.ReadAsArray()
        array[array==0] = 255
        new_start_x = int((new_ulx - ulx)/250.0)
        new_start_y = int((uly - new_uly)/250.0)
        index = new_array != 255
        array[new_start_y:new_start_y+new_y_size, new_start_x:new_start_x+new_x_size][index] = np.copy(new_array[index])
        band.WriteArray(array)
        curr_dataset = None
        dest = None

    # dest = gdal.Open(workspace + str(next_no) + '_CURRENT_RASTER_250.tif', GA_ReadOnly)
    # x_size = dest.RasterXSize # Raster xsize
    # y_size = dest.RasterYSize # Raster ysize
    # new_drv = gdal.GetDriverByName('GTiff')
    # new_dest = new_drv.Create(workspace + str(next_no) + '_CURRENT_RASTER_1000.tif', int(x_size/(1000/250)), int(y_size/(1000/250)), 1, gdal.GDT_Byte)
    # geo_t = dest.GetGeoTransform()
    # geo = (geo_t[0], 1000.0, 0.0, geo_t[3], 0.0, -1000.0)
    # print geo
    # new_dest.SetGeoTransform(geo)
    # new_dest.SetProjection(dest.GetProjection())
    # gdal.ReprojectImage(dest, new_dest, dest.GetProjection(), new_dest.GetProjection(), gdal.GRA_NearestNeighbour)
    # new_dest = None

    dataset = gdal.Open(workspace + str(next_no) + '_CURRENT_RASTER_250.tif', GA_ReadOnly)
    band = dataset.GetRasterBand(1)
    array = band.ReadAsArray()
    tifimg = Image.fromarray(array)
    tifimg.save(workspace + str(next_no) + '_CURRENT_RASTER_250.jpg')

    return str(next_no) + '_CURRENT_RASTER_250'


def getLonLat(filename, folder = 'modisProcessing/MODIS/tiff/arcmapWorkspace/'):

    dataset = gdal.Open(folder+filename+'.tif', GA_ReadOnly)

    x_size = dataset.RasterXSize # Raster xsize
    y_size = dataset.RasterYSize # Raster ysize
    print x_size, y_size
    projection = dataset.GetProjection()
    spatialRef = osr.SpatialReference()
    spatialRef.ImportFromWkt(projection)

    wgs84_wkt = """
    GEOGCS["WGS 84",
        DATUM["WGS_1984",
            SPHEROID["WGS 84",6378137,298.257223563,
                AUTHORITY["EPSG","7030"]],
            AUTHORITY["EPSG","6326"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.01745329251994328,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4326"]]"""
    wgs84SpatialRef = osr.SpatialReference()
    wgs84SpatialRef.ImportFromWkt(wgs84_wkt)

    tx = osr.CoordinateTransformation(spatialRef, wgs84SpatialRef)

    geo_t = dataset.GetGeoTransform()
    print geo_t
    new_y_size = int(math.floor(y_size/20))
    new_x_size = int(math.floor(x_size/20))
    print new_x_size, new_y_size
    lonlats = np.ones((new_y_size, new_x_size, 2))

    for i in range(new_x_size):
        for j in range(new_y_size):
            # print geo_t[0]+geo_t[1]*(i*5+2.5), geo_t[3]+geo_t[5]*(j*5+2.5)
            (lonlats[j, i, 0] ,lonlats[j, i, 1], tmp) = tx.TransformPoint(geo_t[0]+geo_t[1]*(i*20+10), geo_t[3]+geo_t[5]*(j*20+10))

    file = open(folder+filename+'.lonlat', 'wb')
    pickle.dump(lonlats, file, protocol=2)
    file.close()


def getProb(tiff_name, prob_folder = 'modisProcessing/MODIS/Proba/', ice_folder = 'modisProcessing/MODIS/Ice/', tiff_folder = 'modisProcessing/MODIS/tiff/arcmapWorkspace/'):

    file_list = []
    for dripath, dirnames, filenames in os.walk(prob_folder):
        for filename in filenames:
            if not filename.startswith('.'):
                print filename
                file_info = []
                # print filename
                file_info.append(filename)
                segs = filename.split('.')
                tmps1 = segs[0].split('_')
                time = int(tmps1[0][1:]+tmps1[1])
                # print time
                file_info.append(time)
                tmps2 = segs[1].split('_')
                ulx = int(tmps2[0])
                uly = int(tmps2[1])
                resolution = int(tmps2[2])
                # print ulx, uly, resolution
                file_info.append(ulx)
                file_info.append(uly)
                file_info.append(resolution)
                tmps3 = segs[2].split('_')
                print tmps3
                xsize = int(tmps3[2])
                ysize = int(tmps3[4])
                # print xsize, ysize
                file_info.append(xsize)
                file_info.append(ysize)
                file_list.append(file_info)

    file_list = sorted(file_list, key = lambda d:d[1], reverse=True)
    print file_list

    prob_results_list = []
    ice_results_list = []
    for file_info in file_list:
        file = open(prob_folder+file_info[0], 'rb')
        prob_results_list.append(pickle.load(file))
        file.close()
        file = open(ice_folder+file_info[0], 'rb')
        ice_results_list.append(pickle.load(file))
        file.close()

    dataset = gdal.Open(tiff_folder+tiff_name+'.tif', GA_ReadOnly)
    band = dataset.GetRasterBand(1)
    array = band.ReadAsArray()
    x_size = dataset.RasterXSize # Raster xsize
    y_size = dataset.RasterYSize # Raster ysize

    geo_t = dataset.GetGeoTransform()
    print geo_t
    new_y_size = int(math.floor(y_size/20))
    new_x_size = int(math.floor(x_size/20))
    print new_x_size, new_y_size
    probs = np.ones((new_y_size, new_x_size, 3))
    ices = np.ones((new_y_size, new_x_size))

    for i in range(new_x_size):
        for j in range(new_y_size):
            x = geo_t[0]+geo_t[1]*(i*20+10)
            y = geo_t[3]+geo_t[5]*(j*20+10)
            probs[j, i] = [np.nan, np.nan, np.nan]
            ices[j, i] = 0
            if array[j*20+8, i*20+8] != 255:
                for k in range(len(file_list)):
                    file_info = file_list[k]
                    if x >= file_info[2] and y <= file_info[3] and x <= file_info[2]+file_info[5]*file_info[4] and y >= file_info[3] \
                        -file_info[6]*file_info[4]:
                            prob_results = prob_results_list[k]
                            ice_results = ice_results_list[k]
                            i1 = int(math.floor((x - file_info[2])/file_info[4]/20))
                            j1 = int(math.floor((y - file_info[3])/(-file_info[4])/20))
                            # print i1, j1
                            if not np.isnan(prob_results[j1, i1, 0]) and not np.isnan(ice_results[j1, i1]):
                                probs[j, i, 0] = prob_results[j1, i1, 0]
                                probs[j, i, 1] = prob_results[j1, i1, 1]
                                probs[j, i, 2] = prob_results[j1, i1, 2]
                                ices[j, i] = ice_results[j1, i1]
                                break

    file = open(tiff_folder+tiff_name+'.prob', 'wb')
    pickle.dump(probs, file, protocol=2)
    file = open(tiff_folder+tiff_name+'.ice', 'wb')
    pickle.dump(ices, file, protocol=2)


def putpixel(fname, folder = 'modisProcessing/MODIS/tiff/arcmapWorkspace/'):

    picname = fname + '.tif'
    filename = fname + '.prob'

    crop_size = 5

    outpath = folder

    f = open(folder+filename, 'rb')
    predict_array = pickle.load(f)
    dataset = gdal.Open(folder+picname, GA_ReadOnly)
    band = dataset.GetRasterBand(1)
    array = band.ReadAsArray()
    img = Image.fromarray(array)
    print(np.array(img).shape)
    print(img.size)
    img_sea = img.copy()
    img_paper = img.copy()
    img_thick = img.copy()

    startpx = int(math.floor(crop_size / 2))
    startpy = int(math.floor(crop_size / 2))
    print(np.shape(predict_array))

    endpx = int(np.shape(predict_array)[1] * crop_size)
    endpy = int(np.shape(predict_array)[0] * crop_size)

    pxnum = endpx - startpx + int(crop_size / 2)
    pynum = endpy - startpy + int(crop_size / 2)
    pro_matrix = np.zeros((pynum, pxnum, 3), float)
    i_index = 0
    t1 = time.time()
    for i in range(startpx, endpx, crop_size):
        j_index = 0
        for j in range(startpy, endpy, crop_size):

            y_predicted = predict_array[j_index][i_index]
            color_sea = y_predicted[0] * 255
            color_paper = y_predicted[1] * 255
            color_thick = y_predicted[2] * 255
            bxs = int(i - crop_size / 2)
            bxe = int(j - crop_size / 2)
            if crop_size % 2 == 0:
                bys = int(i + crop_size / 2)
                bye = int(j + crop_size / 2)
            else:
                bys = int(i + crop_size / 2) + 1
                bye = int(j + crop_size / 2) + 1
            box = (bxs, bxe, bys, bye)

            for ii in range(box[0], box[2]):
                for jj in range(box[1], box[3]):

                        try:
                            img_sea.putpixel([ii, jj], int(color_sea))
                        except Exception as e:
                            color_sea = 0
                            img_sea.putpixel([ii, jj], int(color_sea))

                        try:
                            img_paper.putpixel([ii, jj], int(color_paper))
                        except Exception as e:
                            color_paper = 0
                            img_paper.putpixel([ii, jj], int(color_paper))

                        try:
                            img_thick.putpixel([ii, jj], int(color_thick))
                        except Exception as e:
                            color_thick = 0
                            img_thick.putpixel([ii, jj], int(color_thick))
            j_index += 1
        i_index += 1

    # print(pro_matrix[0, 0, 0], pro_matrix[0, 0, 1], pro_matrix[0, 0, 2])
    t3 = time.time()
    print('label time', t3 - t1)
    imgname = os.path.split(picname)[1]
    savepath_sea = os.path.join(outpath, imgname[0:len(imgname) - 4] + 'sea.tif')
    img_sea.save(savepath_sea)
    savepath_paper = os.path.join(outpath, imgname[0:len(imgname) - 4] + 'paper.tif')
    img_paper.save(savepath_paper)
    savepath_thick = os.path.join(outpath, imgname[0:len(imgname) - 4] + 'thick.tif')
    img_thick.save(savepath_thick)
    savepath_pri = os.path.join(outpath, imgname[0:len(imgname) - 4] + 'cropimg_pri.tif')
    img.save(savepath_pri)

def getRGBfromProb(prob):
    l, w = prob.shape
    flat_prob = prob.flatten()
    print prob

    Rslipts = [0, 0, 0, 55, 155, 255, 255, 255, 225, 180, 128]
    Gslipts = [0, 0, 0, 55, 155, 255, 150, 50, 0, 0, 0]
    Bslipts = [80, 150, 220, 255, 255, 255, 150, 50, 0, 0, 0]

    flat_R = np.zeros((len(flat_prob), 1))
    flat_G = np.zeros((len(flat_prob), 1))
    flat_B = np.zeros((len(flat_prob), 1))
    for i in range(len(flat_prob)):
        if np.isnan(flat_prob[i]):
            flat_R[i] = 0
            flat_G[i] = 0
            flat_B[i] = 0
        else:
            currprob = flat_prob[i]
            currinterval = int(flat_prob[i]/0.1)
            # print flat_prob[i]
            # print int(flat_prob[i]/0.1)
            if currinterval != 10:
                flat_R[i] = int(Rslipts[currinterval]+(Rslipts[currinterval+1]-Rslipts[currinterval])*(currprob-currinterval*0.1)/0.1)
                flat_G[i] = int(Gslipts[currinterval]+(Gslipts[currinterval+1]-Gslipts[currinterval])*(currprob-currinterval*0.1)/0.1)
                flat_B[i] = int(Bslipts[currinterval]+(Bslipts[currinterval+1]-Bslipts[currinterval])*(currprob-currinterval*0.1)/0.1)
            else:
                flat_R[i] = 96
            # print flat_R[i], flat_G[i], flat_B[i]

    R = np.reshape(flat_R, (l, w))
    G = np.reshape(flat_G, (l, w))
    B = np.reshape(flat_B, (l, w))
    color = np.dstack((R, G, B))
    return color


def cropandmask(ulx, uly, lrx, lry, fname, folder = 'modisProcessing/MODIS/tiff/arcmapWorkspace/'):
    tiffile = folder + fname + '.tif'
    lonlatfile = folder + fname + '.lonlat'
    probfile = folder + fname + '.prob'
    icefile = folder + fname + '.ice'
    jpgfile = folder + fname + '.jpg'

    dataset = gdal.Open(tiffile, GA_ReadOnly)

    x_size = dataset.RasterXSize # Raster xsize
    y_size = dataset.RasterYSize # Raster ysize
    print x_size, y_size
    projection = dataset.GetProjection()
    spatialRef = osr.SpatialReference()
    spatialRef.ImportFromWkt(projection)
    print spatialRef

    wgs84_wkt = """
    GEOGCS["WGS 84",
        DATUM["WGS_1984",
            SPHEROID["WGS 84",6378137,298.257223563,
                AUTHORITY["EPSG","7030"]],
            AUTHORITY["EPSG","6326"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.01745329251994328,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4326"]]"""
    wgs84SpatialRef = osr.SpatialReference()
    wgs84SpatialRef.ImportFromWkt(wgs84_wkt)

    # tx = osr.CoordinateTransformation(wgs84SpatialRef, spatialRef)
    # (ulx, uly, tmp) = tx.TransformPoint(ullon, ullat)
    # (lrx, lry, tmp) = tx.TransformPoint(lrlon, lrlat)

    geo_t = dataset.GetGeoTransform()
    print geo_t
    print (geo_t[0], geo_t[3])
    print (geo_t[0]+geo_t[1]*x_size, geo_t[3]+geo_t[5]*y_size)
    print (ulx, uly)
    print (lrx, lry)

    ulx = ulx - 400000 if ulx - 400000 > geo_t[0] else geo_t[0]
    uly = uly + 400000 if uly + 400000 < geo_t[3] else geo_t[3]
    lrx = lrx + 400000 if lrx + 400000 < geo_t[0] + geo_t[1]*x_size else geo_t[0] + geo_t[1]*x_size
    lry = lry - 400000 if lry - 400000 > geo_t[3] + geo_t[5]*y_size else geo_t[3] + geo_t[5]*y_size

    uli =  int(np.floor(np.round((ulx-geo_t[0])/geo_t[1])/20))*20
    ulj =  int(np.floor(np.round((uly-geo_t[3])/geo_t[5])/20))*20
    lri =  int(np.floor(np.round((lrx-geo_t[0])/geo_t[1])/20))*20
    lrj =  int(np.floor(np.round((lry-geo_t[3])/geo_t[5])/20))*20
    print (uli, ulj)
    print (lri, lrj)

    lonlat = pickle.load(open(lonlatfile, 'rb'))
    # print lonlat.shape
    prob = pickle.load(open(probfile, 'rb'))
    ice = pickle.load(open(icefile, 'rb'))

    colorfull = getRGBfromProb(prob[:,:,2])
    namefull = folder + fname + '.png'
    scipy.misc.imsave(namefull, colorfull)
    if os.path.exists(folder + fname + '.cost'):
        os.remove(folder + fname + '.cost')
    os.rename(namefull, folder + fname + '.cost')
    # print prob.shape

    jpg = Image.open(jpgfile)
    width = jpg.size[0]
    height = jpg.size[1]
    if not (uli >=0 and ulj >=0 and lri <= width and lrj <= height):
        return False, ''

    cu_time = time.strftime("%Y%m%d%H%M%S",time.localtime(time.time()))
    crop_name = cu_time + '_CURRENT_RASTER_250'
    # print jpg.size
    jpg_crop = jpg.crop((uli, ulj, lri, lrj))
    # print jpg_crop.size
    jpg_crop.save(folder + crop_name + '_crop.jpg')

    lonlat_crop = lonlat[ulj/20:lrj/20, uli/20:lri/20, :]
    # print lonlat_crop.shape
    pickle.dump(lonlat_crop, open(folder + crop_name + '_crop.lonlat', 'wb'), protocol=2)

    # jpg_crop_mask_array = np.array(jpg_crop)
    # print jpg_crop_mask_array.shape

    magicnum = 3430000
    tx2 = osr.CoordinateTransformation(wgs84SpatialRef, spatialRef)
    mask = np.load('modisProcessing/mask.npy')

    # print mask.shape
    prob_crop = np.copy(prob[ulj/20:lrj/20, uli/20:lri/20, :])
    ice_crop = np.copy(ice[ulj/20:lrj/20, uli/20:lri/20])
    for i in range(0, lrj/20-ulj/20):
        for j in range(0, lri/20-uli/20):
            # print i, j
            (x, y, tmp) = tx2.TransformPoint(lonlat_crop[i,j,0], lonlat_crop[i,j,1])
            # print x, y
            if x>-magicnum and x<magicnum and y>-magicnum and y< magicnum:
                maskj = int(np.floor((x + magicnum)/5000))
                maski = int(np.floor((y - magicnum)/-5000))
                masknum = mask[maski, maskj]
                # print maski, maskj, masknum
                if masknum == 255:
                    prob_crop[i,j,0] = 0.0
                    prob_crop[i,j,1] = 0.0
                    prob_crop[i,j,2] = 1.0
                    ice_crop[i,j] = 1
                elif masknum == 128:
                    if np.isnan(prob_crop[i,j,0]):
                        prob_crop[i,j,0] = 0.0
                        prob_crop[i,j,1] = 0.05
                        prob_crop[i,j,2] = 0.95
                        ice_crop[i,j] = 1
                    else:
                        prob_crop[i,j,0] = 0.2*prob_crop[i,j,0]
                        prob_crop[i,j,1] = 0.2*prob_crop[i,j,1]
                        prob_crop[i,j,2] = 0.2*prob_crop[i,j,2]+0.8
                        ice_crop[i,j] = 1
                # else:
                #     prob_crop[i,j,0] = 0.8*prob_crop[i,j,0]
                #     prob_crop[i,j,1] = 0.8*prob_crop[i,j,1]
                #     prob_crop[i,j,2] = 0.8*prob_crop[i,j,2]
    # print prob_crop.shape
    pickle.dump(prob_crop, open(folder + crop_name + '_crop.prob', 'wb'), protocol=2)
    pickle.dump(ice_crop, open(folder + crop_name + '_crop.ice', 'wb'), protocol=2)

    # jpg_crop_mask = Image.fromarray(jpg_crop_mask_array)
    # jpg_crop_mask.save(folder + fname + '_crop_mask.jpg')

    color = getRGBfromProb(prob_crop[:,:,2])
    name = folder + crop_name + '_crop.png'
    scipy.misc.imsave(name, color)
    if os.path.exists(folder + crop_name + '_crop.cost'):
        os.remove(folder + crop_name + '_crop.cost')
    os.rename(name, folder + crop_name + '_crop.cost')

    return True, crop_name

