__author__ = 'zhouyh'

import modisdownload.Get_Modis

done = modisdownload.Get_Modis.maindownloading(30, -30, 60, 70)

# import numpy as np
#
# mask = np.load('modisProcessing/mask.npy')
#
# print mask
#
# new_mask = np.zeros(mask.shape)
#
# print new_mask
#
# print np.sum(new_mask)
#
# np.save('modisProcessing/arctic_mask.npy', new_mask)

# import pickle
#
# prob_mat = pickle.load(open('modisProcessing/MODIS/tiff/arcmapWorkspace/0_CURRENT_RASTER_250.prob', 'rb'))
#
# print prob_mat.shape
#
# print prob_mat[300:310,300:310, 2]