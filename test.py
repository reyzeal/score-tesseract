import cv2
import numpy as np 
import pytesseract
def most_frequent(List):
    try: 
        List = [x for x in List if x!='']
        return max(set(List), key = List.count) 
    except ValueError:
        return ''
img = cv2.imread('temp/test51.png',0)
img = img[:,:]
x = [
    pytesseract.image_to_string(img, config="--psm 6 --oem 0 -c tessedit_char_whitelist=0123456789 --tessdata-dir ."),
    pytesseract.image_to_string(img, config="--psm 8 --oem 0 -c tessedit_char_whitelist=0123456789 --tessdata-dir ."),
    pytesseract.image_to_string(img, config="--psm 6 --oem 1 -c tessedit_char_whitelist=0123456789 --tessdata-dir best"),
    pytesseract.image_to_string(img, config="--psm 7 --oem 1 -c tessedit_char_whitelist=0123456789 --tessdata-dir best")
]
print(x)
print(most_frequent(x))
