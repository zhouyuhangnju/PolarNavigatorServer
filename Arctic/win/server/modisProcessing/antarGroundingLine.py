import numpy as np
from PIL import Image

antarcnicimagefile = 'antarctic.jpg'
antarcnicimage = Image.open(antarcnicimagefile)
antarcnicarray = np.array(antarcnicimage)

print antarcnicarray.shape

print antarcnicarray[0,0]
print antarcnicarray[2452,2452]
print antarcnicarray[1280,1962]

magicnum = 3426439.3551643156

l = np.floor(-magicnum/5000)*5000
u = np.ceil(magicnum/5000)*5000

print l, u

length = int((u-l)/5000)
mask = np.zeros((length, length), dtype=np.uint8)

for i in range(length):
    for j in range(length):
        x = int((float(i)/length)*antarcnicarray.shape[0])
        y = int((float(j)/length)*antarcnicarray.shape[1])
        if antarcnicarray[x,y,0] >=250 and antarcnicarray[x,y,1] >=250 and antarcnicarray[x,y,2] >=250:
            mask[i, j] = 255
        elif antarcnicarray[x,y,0]==212 and antarcnicarray[x,y,1]==212 and antarcnicarray[x,y,2]==210:
            mask[i, j] = 128

newmask = np.copy(mask)
for i in range(length):
    for j in range(length):
        if mask[i, j] != 0:
            if i-1>=0 and j-1>=0 and i+1 <length and j+1 < length:
                if mask[i-1, j-1] == 0 and mask[i-1, j] == 0 and mask[i-1, j+1] == 0 and mask[i, j-1] == 0 and \
                            mask[i, j+1] == 0 and mask[i+1, j-1] == 0 and mask[i+1, j] == 0 and mask[i+1, j+1] == 0:
                    newmask[i, j] = 0
mask = newmask

newmask = np.copy(mask)
for i in range(length):
    for j in range(length):
        if mask[i, j]==0:
            if i-4>=0 and j-4>=0 and i+4 <length and j+4 < length:
                flag = False
                margin = 4
                for k in range(margin):
                    tmp = k+1
                    if (mask [i-tmp,j-tmp] == 255 and mask[i+tmp,j+tmp] == 128) or ((mask [i-tmp,j-tmp] == 128 and mask[i+tmp,j+tmp] == 255)) or\
                            (mask [i-tmp,j-tmp] == 255 and mask[i+tmp,j+tmp] == 255) or ((mask [i-tmp,j-tmp] == 128 and mask[i+tmp,j+tmp] == 128)):
                        flag = True
                    if (mask [i-tmp,j] == 255 and mask[i+tmp,j] == 128) or ((mask [i-tmp,j] == 128 and mask[i+tmp,j] == 255)) or\
                            (mask [i-tmp,j] == 255 and mask[i+tmp,j] == 255) or ((mask [i-tmp,j] == 128 and mask[i+tmp,j] == 128)):
                        flag = True
                    if (mask [i-tmp,j+tmp] == 255 and mask[i+tmp,j-tmp] == 128) or ((mask [i-tmp,j+tmp] == 128 and mask[i+tmp,j-tmp] == 255)) or\
                            (mask [i-tmp,j+tmp] == 255 and mask[i+tmp,j-tmp] == 255) or ((mask [i-tmp,j+tmp] == 128 and mask[i+tmp,j-tmp] == 128)):
                        flag = True
                    if (mask [i,j-tmp] == 255 and mask[i,j+tmp] == 128) or ((mask [i,j-tmp] == 128 and mask[i,j+tmp] == 255)) or\
                            (mask [i,j-tmp] == 255 and mask[i,j+tmp] == 255) or ((mask [i,j-tmp] == 128 and mask[i,j+tmp] == 128)):
                        flag = True
                if flag:
                    margin = 8
                    for k in range(margin):
                        tmp = k+1
                        if mask[i-tmp, j-tmp] == 255 or mask[i-tmp, j] == 255 or mask[i-tmp, j+tmp] == 255 or mask[i, j-tmp] == 255 or \
                                mask[i, j+tmp] == 255 or mask[i+tmp, j-tmp] == 255 or mask[i+tmp, j] == 255 or mask[i+tmp, j+tmp] == 255:
                            newmask[i, j] = 255
                        if mask[i-tmp, j-tmp] == 128 or mask[i-tmp, j] == 128 or mask[i-tmp, j+tmp] == 128 or mask[i, j-tmp] == 128 or \
                                mask[i, j+tmp] == 128 or mask[i+tmp, j-tmp] == 128 or mask[i+tmp, j] == 128 or mask[i+tmp, j+tmp] == 128:
                            newmask[i, j] = 128


print newmask

np.save('mask.npy', newmask)
maskimg = Image.fromarray(newmask)
maskimg.save('mask.jpg')





