# encoding:utf-8

import os, shutil
import PreprocessingManagement
import Get_Proba
import RasterManagement


def updateRaster(filename, ulx, uly, lrx, lry):
    newfilename = preprocessing(filename)
    Get_Proba.predict(newfilename+'.band1.tif')
    newnewfilename, iscrop, crop_name = postprocessing(newfilename, ulx, uly, lrx, lry)
    # shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + newnewfilename + '.tif', 'modispath/data/' + newnewfilename + '.tif')
    # shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + newnewfilename + '_crop.lonlat', 'test/' + newnewfilename + '.lonlat')
    # shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + newnewfilename + '_crop.prob', 'test/' + newnewfilename + '.prob')
    # shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + newnewfilename + '_crop.jpg', 'test/' + newnewfilename + '.jpg')
    # shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + newnewfilename + '_crop.cost', 'test/' + newnewfilename + '.cost')
    # shutil.copy('modisProcessing/MODIS/tiff/arcmapWorkspace/' + newnewfilename + '_crop.ice', 'test/' + newnewfilename + '.ice')
    return newnewfilename, iscrop, crop_name

def preprocessing(filename):
    PreprocessingManagement.hdf2tiff(filename)
    newfilename1 = PreprocessingManagement.reprojectingTiff(filename + '_band1')
    newfilename2 = PreprocessingManagement.reprojectingTiff(filename + '_band2')
    PreprocessingManagement.enhancingImage(newfilename1)
    PreprocessingManagement.enhancingImage(newfilename2)
    print newfilename1
    return '.'.join(newfilename1.split('.')[0:-1])


def postprocessing(filename, ulx, uly, lrx, lry):
    newfilename = RasterManagement.add2CurrentRaster(filename+'.band2.tif')
    RasterManagement.getLonLat(newfilename)
    RasterManagement.getProb(newfilename)
    # RasterManagement.putpixel(newfilename)
    iscrop, crop_name = RasterManagement.cropandmask(ulx, uly, lrx, lry, newfilename)
    print newfilename
    return newfilename, iscrop, crop_name


if __name__=="__main__":

    folder = 'modisProcessing/MODIS/hdf'
    filelist = []
    for dripath, dirnames, filenames in os.walk(folder):
        for filename in filenames:
            if filename.startswith('MOD') and filename.endswith('.hdf'):
                filelist.append('.'.join(filename.split('.')[0:-1]))
    print filelist
    for filename in filelist:
        updateRaster(filename)
