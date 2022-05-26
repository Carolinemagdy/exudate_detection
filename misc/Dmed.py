import numpy as np
from misc.DatasetRet import DatasetRet
import os
import re
import cv2
class Dmed(DatasetRet):

    def __init__(self,dirIn):
        self.__imgExt = '.jpg'
        self.__metaExt = '.meta'
        self.__baseDir = dirIn
        # store in obj.data file prefixes

        self.data =  [os.path.splitext(file)[0] for file in os.listdir(self.__baseDir) if file.endswith(self.__imgExt)]
        self.origImgNum = len(self.data)
        self.imgNum = self.origImgNum
        self.idMap = [_ for _ in range(0,self.imgNum)]
    def getNumOfImgs(self):
        return self.imgNum
    
    def getImg(self, id):
        if (id < 0 or id > self.imgNum):
            img = [];
            exit('Index exceeds dataset size of {}'.format(self.imgNum))
        else:
            imgAddress = [self.__baseDir+'/'+self.data[self.idMap[id]]+self.__imgExt]
            bgr = cv2.imread(imgAddress[0])
            img = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

        return img
    
    
    def getONloc(self, id):
        onRow = [];
        onCol = [];
        if (id < 0 or id > self.imgNum):
            exit('Index exceeds dataset size of {}'.format(self.imgNum))
        else:
            
            metaFile =  [self.__baseDir+'/'+self.data[self.idMap[id]]+self.__metaExt]
            fMeta = open(metaFile[0], 'r');
            # if( fMeta > 0 ):
            res = fMeta.read()
            fMeta.close()
            tokRow = re.findall('ONrow\W+([0-9\.]+)',res)
            tokCol = re.findall('ONcol\W+([0-9\.]+)',res)
            if( len(tokRow)>0 and len(tokCol) >0):
                onRow = int(tokRow[0]);
                onCol = int(tokCol[0]);
                    
        return [onRow, onCol]
    
      
    


