# Exudate_Detection
<img src="src/1.PNG" >

### How to use
- Run main.py
- Click the browse button and choose a photo
- Wait until both images appear (original & exudates)
<img src="src/2.PNG" >

#### Flow of Functions Used
- Browse(): Browse an image to extract its exudates.
- get_on_loc(): [onRow, onCol] Get the hand identified location of the optic nerve.
- get_lesions(img,removeON, onY, onX) Display the image indicated by imgID with the lesions.
- find_good_resolution_for_wavelet(size): Find the best resolution for the wavelet transform.
- get_fov_mask(img, erodeFlag, seSize): Construct Field of view mask for the eye.
- get_median_filt(img, newSize): Perform morphological reconstruction for the median background then subtract the background from the image.
- get_reconstructed_bkg(img, medBg): Perform a reconstruction of the background.
- get_subtracted_img(img, medBg, imgFovMask): Perform morphological reconstruction for the median background then subtract the background from the image.
- kirsch_edges(img): detect edges using Kirsch operator. 
