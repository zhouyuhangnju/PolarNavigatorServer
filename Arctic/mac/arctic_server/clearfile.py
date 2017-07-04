import os

def search_and_remove(path, word):
    for filename in os.listdir(path):
        fp = os.path.join(path, filename)
        if os.path.isfile(fp) and word in filename:
            os.remove(fp)
            # print(fp)

def clear_raster(folder = 'modisProcessing/MODIS/tiff/arcmapWorkspace/'):
    indexset = set()
    for dripath, dirnames, filenames in os.walk(folder):
        for filename in filenames:
            if not filename.startswith('.DS_') and not 'crop' in filename:
                indexset.add(int(filename.split('.')[0].split('_')[0]))
    print indexset
    if len(indexset) <= 2:
        return

    indexlist = sorted(indexset, reverse=True)
    savelist = [str(indexlist[0]), str(indexlist[1])]

    for dripath, dirnames, filenames in os.walk(folder):
        for filename in filenames:
            if filename.split('.')[0][-4:] == 'crop':
                continue
            elif filename.split('.')[0].split('_')[0] not in savelist:
                os.remove(os.path.join(folder, filename))
                # print(os.path.join(folder, filename))

def clear_files(folder = 'modisProcessing/MODIS/'):
    hdf_folder = 'hdf/'
    tif_folder = 'tiff/'
    hdf_fileset = set()
    for dripath, dirnames, filenames in os.walk(folder+hdf_folder):
        for filename in filenames:
            if filename.startswith('MOD') and filename.endswith('.hdf'):
                hdf_fileset.add('.'.join(filename.split('.')[0:-1]))
    if len(hdf_fileset) <= 2:
        return
    hdf_fileset = sorted(hdf_fileset, reverse=True)
    for i in range(2, len(hdf_fileset)):
        search_and_remove(folder+hdf_folder, hdf_fileset[i])
        search_and_remove(folder+hdf_folder+'HEGOUT/', hdf_fileset[i])

    tif_files = [hdf_fileset[0].split('.')[1]+'_'+hdf_fileset[0].split('.')[2],
                   hdf_fileset[1].split('.')[1]+'_'+hdf_fileset[1].split('.')[2]]
    for filename in os.listdir(folder+tif_folder):
        if filename.endswith('.tif') and not (tif_files[0] in filename or tif_files[1] in filename):
            os.remove(folder+tif_folder+filename)
            # print(folder+tif_folder+filename)

if __name__ == '__main__':
    clear_raster()
    clear_files()