import gdal
from gdalconst import GA_Update
from osgeo import osr
import numpy as np
import math
import os, shutil
import cv2
import ConfigParser

def hdf2tiff(filename, hdffolder = 'modisProcessing/MODIS/hdf/'):
    print filename

    MODISToolsPath = '/opt/'
    os.environ['MRTDATADIR'] = MODISToolsPath+'MRT/data'
    os.environ['PGSHOME'] = MODISToolsPath+'HEG/TOOLKIT_MTD'

    folder = os.path.join(os.getcwd(), hdffolder)
    outfolder = os.path.join(os.getcwd(), hdffolder+'HEGOUT')
    if not os.path.exists(outfolder):
        os.mkdir(outfolder)
    templateprm = 'modisProcessing/baaa_swath.prm'
    headerfile = os.path.join(os.getcwd(), 'modisProcessing/Header.hdr')
    hdffile = os.path.join(folder, filename+'.hdf')
    print hdffile
    hdrfile = os.path.join(folder, filename+'.hdr')
    express = 'hegtool -n \'{0}\' \'{1}\''.format(hdffile, hdrfile)
    os.system(express)

    with open(hdrfile, 'r') as f:
        lines = f.readlines()
    with open(hdrfile, 'w') as f:
        f.writelines(open(headerfile).readlines())
        f.writelines(lines)

    cf = ConfigParser.ConfigParser()
    cf.read(hdrfile)

    OUTPUT_PIXEL_SIZE_X = cf.get("abc", "SWATH_X_PIXEL_RES_METERS")
    OUTPUT_PIXEL_SIZE_Y = cf.get("abc", "SWATH_Y_PIXEL_RES_METERS")
    SWATH_LAT_MAX = cf.get("abc", "SWATH_LAT_MAX")
    SWATH_LON_MIN = cf.get("abc", "SWATH_LON_MIN")
    SWATH_LAT_MIN = cf.get("abc", "SWATH_LAT_MIN")
    SWATH_LON_MAX = cf.get("abc", "SWATH_LON_MAX")

    with open(templateprm, 'r') as f:
        template = f.read()
    prm = template\
          .replace('outpixelx', OUTPUT_PIXEL_SIZE_X)\
          .replace('outpixely', OUTPUT_PIXEL_SIZE_Y)\
          .replace('SWATH_LAT_MAX', SWATH_LAT_MAX)\
          .replace('SWATH_LON_MIN', SWATH_LON_MIN)\
          .replace('SWATH_LAT_MIN', SWATH_LAT_MIN)\
          .replace('SWATH_LON_MAX', SWATH_LON_MAX)\
          .replace('infile', hdffile)\
          .replace('outfile', os.path.join(outfolder, filename))
    prmfile = os.path.join(folder, filename+'.prm')
    with open(prmfile, 'wb') as f:
        f.write(prm)

    express = 'swtif -p \'{0}\''.format(prmfile)
    os.system(express)
    os.remove(hdrfile)
    os.remove(prmfile)

    dir = '.'
    files = os.listdir(dir)
    for file in files:
        if file.startswith('temp'):
            os.remove(os.path.join(dir, file))
        if file.startswith('tmp'):
            os.remove(os.path.join(dir, file))

    files = os.listdir(outfolder)
    for file in files:
        if file.endswith('.met'):
            os.remove(os.path.join(outfolder, file))

    shutil.copy(folder+'HEGOUT/'+filename+'_band1.tif', 'modisProcessing/MODIS/tiff/'+filename+'_band1.tif')
    shutil.copy(folder+'HEGOUT/'+filename+'_band2.tif', 'modisProcessing/MODIS/tiff/'+filename+'_band2.tif')

def reprojectingTiff(filename, folder = 'modisProcessing/MODIS/tiff/'):
    print filename

    dataset = gdal.Open(folder+filename+'.tif', GA_Update)
    x_size = dataset.RasterXSize # Raster xsize
    y_size = dataset.RasterYSize # Raster ysize
    # transfer 16bit image to 8bit
    band = dataset.GetRasterBand(1)
    array = band.ReadAsArray()
    array /= 256
    for i in range(y_size):
        index = array[i] == 0
        array[i][index] = 1
        index = None
    band.WriteArray(array)
    band = None
    array = None

    # get projection of the origin image
    projection = dataset.GetProjection()
    spatialRef = osr.SpatialReference()
    spatialRef.ImportFromWkt(projection)
    print spatialRef

    # set the destinate (appointed) projection
    centerLat = -90.0
    centerLong = 0.0
    scale = 1.0
    falseEasting = 0
    falseNorthing = 0
    desSpatialRef = osr.SpatialReference()
    desSpatialRef.ImportFromWkt(projection)
    desSpatialRef.SetPS(centerLat, centerLong, scale, falseEasting, falseNorthing)
    print desSpatialRef

    # transfer coordinates and obtain the new geo (extent of the reprojected image)
    tx = osr.CoordinateTransformation (spatialRef, desSpatialRef)
    geo_t = dataset.GetGeoTransform()
    (ulx, uly, ulz) = tx.TransformPoint(geo_t[0], geo_t[3])
    (urx, ury, urz) = tx.TransformPoint(geo_t[0]+geo_t[1]*x_size+geo_t[2]*y_size, geo_t[3])
    (lrx, lry, lrz) = tx.TransformPoint(geo_t[0]+geo_t[1]*x_size+geo_t[2]*y_size, geo_t[3]+geo_t[4]*x_size+geo_t[5]*y_size)
    (llx, lly, llz) = tx.TransformPoint(geo_t[0], geo_t[3]+geo_t[4]*x_size+geo_t[5]*y_size)
    min_x = min([ulx, urx, lrx, llx])
    max_x = max([ulx, urx, lrx, llx])
    min_y = min([uly, ury, lry, lly])
    max_y = max([uly, ury, lry, lly])

    # reproject the image to the new projection
    drv = gdal.GetDriverByName('MEM')
    dest = drv.Create('', int((max_x - min_x)/250.0)+1, int((min_y - max_y)/-250.0)+1, 1, gdal.GDT_Byte)
    new_geo = (min_x, 250.0, 0.0, max_y, 0.0, -250.0)
    print new_geo
    dest.SetGeoTransform(new_geo)
    dest.SetProjection(desSpatialRef.ExportToWkt())
    gdal.ReprojectImage(dataset, dest, projection, desSpatialRef.ExportToWkt(), gdal.GRA_NearestNeighbour)
    dataset = None
    os.remove(folder+filename+'.tif')

    band = dest.GetRasterBand(1)
    array = band.ReadAsArray()
    x_size = dest.RasterXSize
    y_size = dest.RasterYSize
    for i in range(y_size):
        index = array[i] == 0
        array[i][index] = 255
        index = None
    band.WriteArray(array)

    top = -1
    for i in range(y_size):
        if np.all(array[i,:] == 255):
            if i > top:
                top = i
        else:
            break
    bottom = y_size
    for i in range(y_size)[::-1]:
        if np.all(array[i,:] == 255):
            if i < bottom:
                bottom = i
        else:
           break
    left = -1
    for i in range(x_size):
        if np.all(array[:,i] == 255):
            if i > left:
                left = i
        else:
            break
    right = x_size
    for i in range(x_size)[::-1]:
        if np.all(array[:,i] == 255):
            if i < right:
                right = i
        else:
            break
    array = None
    band = None

    new_drv = gdal.GetDriverByName('GTiff')
    newfilename = '_'.join(filename.split('.')[1:3]) + '.'+str(int(math.ceil(new_geo[0]+(left+1)*new_geo[1]))) + '_' + \
                  str(int(math.floor(new_geo[3]+(top+1)*new_geo[5]))) + '_250.' + filename.split('_')[1]
    new_dest = new_drv.Create(folder+newfilename+'.tif', right-left-1, bottom-top-1, 1, gdal.GDT_Byte)
    new_new_geo = (new_geo[0]+(left+1)*new_geo[1], new_geo[1], new_geo[2], new_geo[3]+(top+1)*new_geo[5], new_geo[4], new_geo[5])
    print new_new_geo
    new_dest.SetGeoTransform(new_new_geo)
    new_dest.SetProjection(dest.GetProjection())
    gdal.ReprojectImage(dest, new_dest, dest.GetProjection(), new_dest.GetProjection(), gdal.GRA_NearestNeighbour)
    new_dest = None

    return newfilename


def enhancingImage(filename, folder = 'modisProcessing/MODIS/tiff/'):
    print filename

    dataset = gdal.Open(folder+filename+'.tif', GA_Update)
    band = dataset.GetRasterBand(1)
    picarray = band.ReadAsArray()
    # print picarray

    x_size = dataset.RasterXSize # Raster xsize
    y_size = dataset.RasterYSize # Raster ysize
    picarray = homofilter(picarray, x_size, y_size)
    picarray = cv2.equalizeHist(picarray)
    # picarray = unifyGrayCenter(picarray)

    band.WriteArray(picarray)


def homofilter(orig_array, x_size, y_size):
    print orig_array.shape
    mask = orig_array == 255
    orig_array = orig_array.astype(np.float32)/255.0
    opt_x_size = cv2.getOptimalDFTSize(x_size)
    opt_y_size = cv2.getOptimalDFTSize(y_size)
    # opt_x_size = x_size
    # opt_y_size = y_size
    if opt_x_size % 2 != 0:
        opt_x_size +=1
    if opt_y_size % 2 != 0:
        opt_y_size +=1
    if opt_x_size - x_size > 0:
        orig_array = np.hstack((orig_array, np.ones((y_size, opt_x_size - x_size))))
    if opt_y_size - y_size > 0:
        orig_array = np.vstack((orig_array, np.ones((opt_y_size - y_size, opt_x_size))))
    print orig_array.shape

    print 'log ...'
    log_array = np.log(orig_array+0.0001)
    print log_array
    orig_array = None

    print 'dct ...'
    dct_array = cv2.dct(log_array)
    print dct_array
    log_array = None

    print 'filter ...'
    gammaH = 2
    gammaL = 0.3
    C = 1.0
    d0 = float((opt_y_size/2)**2 + (opt_x_size/2)**2)
    colvec = (np.arange(opt_y_size).reshape(opt_y_size, 1))**2
    rowvec = (np.arange(opt_x_size).reshape(1, opt_x_size))**2
    print (colvec+rowvec)/d0
    H = (gammaH - gammaL)*(1 - np.exp(-C*(colvec+rowvec)/d0)) + gammaL
    # H = np.ones(dct_array.shape)
    # H[colvec+rowvec<d0] = 0.0
    print H
    filtered_dct_array = dct_array*H
    print filtered_dct_array
    dct_array = None

    print 'idct ...'
    idct_array = cv2.idct(filtered_dct_array)
    print idct_array
    filtered_dct_array = None
	
    print 'exp ...'
    exp_array = np.uint8((np.floor(np.exp(idct_array)*255.0)))
    print exp_array
    array = np.copy(exp_array[0:y_size, 0:x_size])
    print array.shape

    array[mask] = 255
    return array


def unifyGrayCenter(picarray):
    mean=106.0
    picarray2 = picarray
    picarray2[picarray2 == 255] = 0
    suma = picarray2.sum(axis = 1)
    suma = suma.astype(np.uint64)
    sumb = suma.sum()
    count = np.count_nonzero(picarray2)
    picarray2 = None
    the_mean = sumb / float(count)
    coef = np.float32(mean/the_mean)
    print(coef)
    picarray = picarray * coef
    picarray[picarray > 255] = 255
    picarray[picarray == 255] = 250
    picarray[picarray == 0] = 255
    print picarray.dtype
    picarray = picarray.astype(np.uint8)

    return picarray

