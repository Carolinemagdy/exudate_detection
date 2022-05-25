from misc.Dmed import Dmed
from exDetect import *
DMEDloc = './DMED'
data = Dmed( DMEDloc )
for i in range (0,1):
    rgbImg = data.getImg(i) # get original image
    [onY, onX] = data.getONloc(i) # get optic nerve location
    imgProb = exDetect( rgbImg, 1, onY, onX )# segment exudates
#     % display results
#     figure(1);
#     imagesc(rgbImg);
#     figure(2);
#     imagesc(imgProb);
#     % block execution up until an image is closed
#     uiwait;
# end
