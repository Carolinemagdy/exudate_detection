from matplotlib.pyplot import close
import numpy as np
from requests import delete
import DatasetRet
import os
import re
import cv2
from genericpath import exists
import gzip
class Dmed(DatasetRet):
    #   data
    #    origImgNum % real img num
    #    imgNum % current imgNum
    #    idMap % maps abstract id to real id
    #    roiExt
    #    imgExt
    #    metaExt
    #    gndExt
    #    mapGzExt
    #    mapExt
    #    baseDir
    def __init__(self,dirIn):
        self.__roiExt = '.jpg.ROI'
        self.__imgExt = '.jpg'
        self.__metaExt = '.meta'
        self.__gndExt = '.GND'
        self.__mapGzExt = '.map.gz'
        self.__mapExt = '.map'
        self.__baseDir = dirIn
        # store in obj.data file prefixes

        self.data =  [os.path.splitext(file)[0] for file in os.listdir(self.__baseDir) if file.endswith(self.__imgExt)]
        self.origImgNum = len(self.data)
        self.imgNum = self.origImgNum
        self.idMap = [_ for _ in range(1,1+self.imgNum)]
        
    def getNumOfImgs(self):
        return self.imgNum
    
    def getImg(self, id):
        if (id < 1 or id > self.imgNum):
            img = [];
            exit('Index exceeds dataset size of {}'.format(self.imgNum))
        else:
            imgAddress = [self.__baseDir+'/'+self.data[self.idMap[id]]+self.__imgExt]
            img = cv2.imread(imgAddress[0])
        return img
    
    
    def getONloc(self, id):
        onRow = [];
        onCol = [];
        if (id < 1 or id > self.imgNum):
            exit('Index exceeds dataset size of {}'.format(self.imgNum))
        else:
            
            metaFile =  [self.__baseDir+'/'+self.data[self.idMap[id]]+self.__metaExt]
            fMeta = open(metaFile[0], 'r');
            if( fMeta > 0 ):
                res = fMeta.read()
                close(fMeta);
                #regex
                tokRow = re.findall('ONrow\W+([0-9\.]+)',res)
                tokCol = re.findall('ONcol\W+([0-9\.]+)',res)
                if( len(tokRow)>0 and len(tokCol) >0):
                    onRow = int(tokRow[0]);
                    onCol = int(tokCol[0]);
                    
        return [onRow, onCol]
    
      
    # def getGT(self, id):
    #     if (id < 1 or id > self.imgNum):
    #         imgGT = [];
    #         exit('Index exceeds dataset size of {}'.format(self.imgNum))
    #     else:
    #         mapGzFile = [self.__baseDir+'/'+self.data[self.idMap[id]]+self.__mapGzExt]
    #         # if (exists(mapGzFile[0])):
    #         #     gzip(mapGzFile, obj.baseDir);
    #         gndFile = [self.__baseDir+'/'+self.data[self.idMap[id]]+ self.__gndExt];
    #         mapFile = [self.__baseDir+'/'+self.data[self.idMap[id]]+ self.__mapExt];
    #         fMap = open(mapFile[0], 'r')
    #         if( fMap > 0 ):
    #             resImg = open(fMap, 3, 'int');
    #             imgGT = open(fMap, [resImg[2] , resImg[3]], 'int');
    #             close(fMap);
    #             imgGT = imgGT.T

    #             #get description
    #             [blobInfo] = ReadGNDFile( gndFile );
    #         else: 
    #             #if there is not any GND file available consider it as healthy
    #             blobInfo = {};
    #             img = self.getImg( id );
    #             imgGT = np.zeros( [img.shape[0],img.shape[1]] );
    #             if( exists( mapGzFile) ):
    #                 delete( mapFile );

        
        
    #     return [imgGT, blobInfo]
    # def isHealthy(self, id):
    #     healthy = 1;
    #     if (id < 1 or id > self.imgNum):
    #         imgGT = [];
    #         exit('Index exceeds dataset size of {}'.format(self.imgNum))
    #     else:
    #         gndFile = [self.__baseDir+'/'+self.data[self.idMap[id]]+ self.__gndExt];

    #         if( exists(gndFile) ):
    #             #% get description
    #             [blobInfo] = ReadGNDFile( gndFile )
    #             lesList = regexpi( blobInfo, 'MicroAneurysm|Exudate' )
        
        
        
        # return healthy


