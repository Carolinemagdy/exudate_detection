imgExt = '.jpg'
baseDir = './DMED'
import shutil
from genericpath import exists
import gzip
import os,numpy
import matplotlib.pyplot as plt
import zipfile
import cv2
a =  [_ for _ in os.listdir(baseDir) if _.endswith(imgExt)]
# print(a)
k=[os.path.splitext(file)[0] for file in os.listdir(baseDir) if file.endswith(imgExt)]
# for file in a:
#     k.append(os.path.splitext(file)[0])
b=[_ for _ in range(1,170)]
# # print(b)

imgAddress = [baseDir+'/'+k[b[0]]+ imgExt]
# x=3
print(imgAddress[0])


# imgAddress = [baseDir+'/'+k[b[8]]+'.map.gz'];
# # print(imgAddress)
# # img = cv2.imread( imgAddress[0] );
# # print(img)
# # print(exists(imgAddress[0]))

# #path_to_file_to_be_extracted


# #output file to be filled
# add = [baseDir+'/'+k[b[8]]+'.meta'];

# # with open(add[0], 'r') as f:

# #     contents = f.read()
# #     print(contents)
# fMeta = open(add[0], 'r');
# # if( fMeta > 0 ):
# contents = fMeta.read()
# print(type(fMeta))
import cv2
bgr=cv2.imread(imgAddress[0])
print(bgr[:,:,0])
im_rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
print(im_rgb[:,:,2])
plt.imshow(im_rgb)