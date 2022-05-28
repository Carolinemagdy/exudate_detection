from misc.Dmed import Dmed
from exDetect import *
import matplotlib.pyplot as plt

DMEDloc = './DMED'
data = Dmed( DMEDloc )
for i in range (1,2):
    rgbImg = data.getImg(i) # get original image
    [onY, onX] = data.getONloc(i) # get optic nerve location
    imgProb = exDetect( rgbImg, 1, onY, onX )# segment exudates
#     % display results
#     figure(1);
#     figure(2);
    plt.imshow(imgProb)
    plt.show()
#     imagesc(imgProb);
#     % block execution up until an image is closed
#     uiwait;
# end
