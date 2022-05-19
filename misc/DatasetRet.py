from abc import ABC, abstractmethod
class DatasetRet(ABC):
     
    @abstractmethod
    def getNumOfImgs(self):
        pass
    def getImg(self, id):
        pass
    def getGT(self, id):
        pass
    def getVesselSeg(self, id, newSize):
        pass
    def getONloc(self, id):
        pass
    def getMacLoc(self, id):
        pass
    def isHealthy(self, id):
        pass