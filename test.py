import cv2
import numpy as np 
import pytesseract
def most_frequent(List):
    try: 
        List = [x for x in List if x!='']
        return max(set(List), key = List.count) 
    except ValueError:
        return ''
img = cv2.imread('temp/test22.png',0)
img = img[:,:]
h,w = img.shape[:2]
putih = np.zeros((h,w), np.uint8)
putih[:,:] = 255
# img = np.concatenate((putih,img,putih),axis=1)
x = [
    pytesseract.image_to_string(img, config="--psm 6 --oem 0 -c tessedit_char_whitelist=0123456789 --tessdata-dir ."),
    pytesseract.image_to_string(img, config="--psm 8 --oem 0 -c tessedit_char_whitelist=0123456789 --tessdata-dir ."),
    pytesseract.image_to_string(img, config="--psm 13 --oem 0 -c tessedit_char_whitelist=0123456789 --tessdata-dir ."),
    # pytesseract.image_to_string(img, config="--psm 6 --oem 1 -c tessedit_char_whitelist=0123456789 --tessdata-dir ."),
    pytesseract.image_to_string(img, config="--psm 6 --oem 1 -c tessedit_char_whitelist=0123456789 --tessdata-dir best"),
    pytesseract.image_to_string(img, config="--psm 8 --oem 1 -c tessedit_char_whitelist=0123456789 --tessdata-dir best"),
    # pytesseract.image_to_string(img, config="--psm 13 --oem 1 -c tessedit_char_whitelist=0123456789 --tessdata-dir best"),
    # pytesseract.image_to_string(img, config="--psm  --oem 1 -c tessedit_char_whitelist=0123456789 --tessdata-dir fast")
]
print(x)
print(most_frequent(x))
