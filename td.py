import os
import cv2
import pytesseract
import numpy as np
for i in os.listdir('temp'):
    if "roi_" in i and len(i) == 9:
        y = cv2.imread(f'temp/{i}',0)
        # k = np.ones((2,2),np.uint8)
        # y = cv2.erode(cv2.bitwise_not(y),k, iterations=1)
        # cv2.imwrite(f'temp/x{i}',cv2.bitwise_not(y))
        print(pytesseract.image_to_string(f'temp/{i}',config="-l eng --oem 1 --psm 6 -c tessedit_char_whitelist=0123456789_-abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ --tessdata-dir ."), i)