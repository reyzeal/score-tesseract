import cv2
import numpy
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import imutils
import time
import os
import uuid 
from text_detection import detect
kernel  = (5,5)
def proceed(img_path, config={"level":False, "deaths":False, "mobs":False, "eliminations":False, "xp":False, "gold":False, "damage":False, "healing":False}):
    start = time.time()
    img = cv2.imread(img_path)

    w = img.shape[1]
    h = img.shape[0]
    changed = False
    if w < 3840 or h < 2160:
        changed = True
        img = cv2.resize(img, (3840, 2160), interpolation=cv2.INTER_CUBIC)

    def getThreshold(img):
        w = img.shape[1]
        h = img.shape[0]
        if w < 300 and h < 300:
            img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
        kernel  = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2,2))
        # get V part
        # alpha = 1.0 # Contrast control (1.0-3.0)
        # beta = 5 # Brightness control (0-100)

        # img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
        # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        YCrCb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        # h,s,v = cv2.split(hsv)
        Y,Cr,Cb = cv2.split(YCrCb)
        # temp = numpy.concatenate((gray,h,s,v,Y,Cr,Cb), axis=0)
        # cv2.imwrite('temp/'+str(uuid.uuid4())+'.jpg',temp)
        blur = cv2.GaussianBlur(Y,(5,5),0)
        # threshold = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
        # threshold = cv2.threshold(cv2.medianBlur(Y, 3), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        threshold = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        threshold = cv2.dilate(threshold,(3,3),iterations = 1)
        if threshold[1][1] < 200:
            
            threshold_inv = cv2.bitwise_not(threshold)
        else:
            threshold_inv = threshold
        img = cv2.morphologyEx(threshold_inv, cv2.MORPH_CLOSE, kernel)
        return img

    ROI_firstname = [347, 447, 200, 45]
    ROI_secondname = [347, 1042, 200, 45]
    ROI_firstteam = [
        [465, 505, 505, 100],
        [465, 615, 505, 90],
        [465, 725, 505, 90],
        [465, 835, 505, 85],
        [465, 935, 505, 90],
    ]
    ROI_second = [
        [465, 1102, 505, 100],
        [465, 1222, 505, 90],
        [465, 1327, 505, 90],
        [465, 1435, 505, 85],
        [465, 1540, 505, 90],
    ]
    ROI_score = [
        [1350, 530, 37, 52],
        [1547, 512, 80, 80],
        [1775, 512, 205, 80],
        [2022, 512, 200, 80],
        [2270, 517, 207, 80],
        [2515, 520, 210, 80],
        [2762, 520, 202, 80],
        [3025, 515, 165, 80]
    ]
    label = [
        'level',
        'eliminations',
        'deaths',
        'mobs',
        'gold',
        'xp',
        'damage',
        'healing'
    ]
    x,y,w,h = ROI_firstname
    img1 = getThreshold(img[y:y+h, x:x+w])
    id = uuid.uuid4()
    cv2.imwrite(f'temp/roi_t1{id}.jpg', img1)
    
    team1 = pytesseract.image_to_string(f'temp/roi_t1{id}.jpg').replace(" ","_")
    os.unlink(f'temp/roi_t1{id}.jpg')
    x,y,w,h = ROI_secondname
    img2 = getThreshold(img[y:y+h, x:x+w])
    id = uuid.uuid4()
    cv2.imwrite(f'temp/roi_t2{id}.jpg', img2)
    team2 = pytesseract.image_to_string(f'temp/roi_t2{id}.jpg').replace(" ","_")
    os.unlink(f'temp/roi_t2{id}.jpg')
    # test
    cv2.imwrite(f'temp/roi_t1.jpg', img1)
    cv2.imwrite(f'temp/roi_t2.jpg', img2)
    data = {
        team1: {},
        team2: {}
    }
    ROI_firstteam.extend(ROI_second)

    for i,roi in enumerate(ROI_firstteam):
        id = uuid.uuid4()
        filename = f'temp/roi_{id}.jpg'
        # filename = f'temp/roi_{i}.jpg'
        x,y,w,h = roi
        
        # cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),5)
        img1 = getThreshold(img[y:y+h, x:x+w])
        
        
        cv2.imwrite(filename, img1)
        
        imgs = detect({
                    "image" : filename,
                    "east" : "frozen_east_text_detection.pb",
                    "width" : 128,
                    "height" : 32, 
                    "min_confidence" : 0.5
                })
        if len(imgs) > 0:
            if changed:
                string1 = pytesseract.image_to_string(filename,config='--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789-_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -c tessedit_do_invert=0 --tessdata-dir ./fast').replace(" ","_")
            else:
                string1 = pytesseract.image_to_string(filename,config='--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789-_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -c tessedit_do_invert=0 --tessdata-dir .').replace(" ","_")
        else:
            string1 = ""
        # if len(string1) == 0:
            
        #     img1 = getThreshold(clster)
        #     if not img1.empty():
        #         cv2.imwrite(filename, img1)
        #         w,h = img1.shape[:2]
        #         w = int(w/32)*32
        #         if w == 0:
        #             w = 32
        #         imgs = detect({
        #             "image" : filename,
        #             "east" : "frozen_east_text_detection.pb",
        #             "width" : w,
        #             "height" : 32, 
        #             "min_confidence" : 0.5
        #         })
        #         if len(imgs) > 0:
        #             cv2.imwrite(filename, imgs[0])
        #             string1 = pytesseract.image_to_string(filename, config='--psm 13 --oem 3 --tessdata-dir .').replace(" ","_")
        os.unlink(filename)
        if y < 1000:
            f = 0
            teams = team1
        else:
            f = -2
            teams = team2
        # print(string1, end="\t")
        if len(string1) >0:
            temp = {}
            
            for j,score in enumerate(ROI_score):
                id = uuid.uuid4()
                filename2 = f'temp/roi_{id}{j}.jpg'
                # filename2 = f'temp/roi_{string1}_{label[j]}.jpg'
                hasil = config[label[j]]
                # print(hasil)
                if not hasil:
                    continue
                
                a,b,c,d = score
                
                if j == 0:
                    img2 = getThreshold(img[y+24+f:y+24+f+d, a:a+c])
                    cv2.imwrite(filename2, img2)
                    # cv2.imwrite(f'temp/roi_{string1}_{label[j]}.jpg', img2)
                    string2 = pytesseract.image_to_string(filename2, config="--psm 13 --oem 0 -c tessedit_char_whitelist=0123456789 -c tessedit_do_invert=0 --tessdata-dir .").replace(" ","")
                else:
                    img2 = getThreshold(img[y:y+d, a:a+c])
                    cv2.imwrite(filename2, img2)
                    # cv2.imwrite(f'temp/roi_{string1}_{label[j]}.jpg', img2)
                    string2 = pytesseract.image_to_string(filename2, config="--psm 13 --oem 0 -c tessedit_char_whitelist=0123456789, -c tessedit_do_invert=0 --tessdata-dir .").replace(" ","")
                
                os.unlink(filename2)
                string2=string2.replace(",","").replace(".",'')
                if string2 == '':
                    string2 = '0'
                temp[label[j]] = int(string2)
                # print(string2, end="\t")
            data[teams].update({string1:temp})
        # print()
    os.unlink(img_path)
    end = time.time()
# print(end - start)
    result = {
        "filename" : os.path.basename(img_path),
        "request" : config,
        "data" : data,
        "time" : str(end-start)+" seconds"
    }
    return result

