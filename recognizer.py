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
from time import sleep
kernel  = (5,5)

class dummytqdm:
    def __init__(self):
        self.total = 10
        pass
    def update(self,x):
        pass
    def set_description(self,x):
        pass

tqdm_i = 0
tqdm_lists = []
tqdm_ins = None
def update(img_name, count):
    global tqdm_lists, tqdm_i, tqdm_ins
    if tqdm_lists is None:
        return
    padding = " ".join(["" for i in range(25-len(f"{tqdm_lists[tqdm_i]}"))])
    if tqdm_ins.total > tqdm_i:
        tqdm_ins.set_description(f"{tqdm_lists[tqdm_i]}"+padding)
        tqdm_ins.update(count)
        tqdm_i += count

def proceed(img, img_name, config={"level":False, "deaths":False, "mobs":False, "eliminations":False, "xp":False, "gold":False, "damage":False, "healing":False}, tqdm=None, tqdm_list=None):
    global tqdm_ins, tqdm_lists, tqdm_i
    tqdm_lists = tqdm_list
    tqdm_ins = tqdm
    start = time.time()
    img = cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2BGR)
    if tqdm is None:
        tqdm = dummytqdm()
    hitungan = 0
    tqdm_i = 0
    for i in config.keys():
        if config[i]:
            hitungan+=1
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
        YCrCb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        Y,Cr,Cb = cv2.split(YCrCb)
        if changed:
            blur = cv2.GaussianBlur(Y,(5,5),0)
        else:
            blur = cv2.GaussianBlur(Y,(3,3),1)
        threshold = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        k = numpy.ones((2,2),numpy.uint8)
        if changed:
            threshold = cv2.dilate(threshold,(3,3),iterations = 1)
        else:
            threshold = cv2.erode(threshold,(3,3),iterations = 1)
        
        if threshold[1][1] < 200:
            threshold = cv2.erode(threshold,k,iterations = 1)
            threshold_inv = cv2.bitwise_not(threshold)
        else:
            threshold = cv2.erode(cv2.bitwise_not(threshold),k,iterations = 1)
            threshold_inv = cv2.bitwise_not(threshold)
        img = cv2.morphologyEx(threshold_inv, cv2.MORPH_CLOSE, kernel)
        return img
    def centroid(img):
        bimg = cv2.bitwise_not(img)
        blur = cv2.GaussianBlur(bimg,(55,55),0)
        t = cv2.threshold(blur,10,255,cv2.THRESH_BINARY)[1]
        t = numpy.uint8(t)
        cnts, _ =cv2.findContours(t,1,2)
        a,b,c,d = [blur.shape[1],blur.shape[0],0,0]
        for cnt in cnts:
            x,y,w,h = cv2.boundingRect(cnt)
            a = min(a,x)
            b = min(b,y)
            d = max(d,y+h)
            c = max(c,x+w)
        if a > c:
            a,c = c,a
        if b > d:
            b,d = d,b
        newImg = img[b:d,a:c] 
        return newImg
    ROI_firstname = [347, 447, 200, 45]
    ROI_secondname = [347, 1042, 200, 45]
    ROI_firstteam = [
        [465, 505, 505, 100],
        [465, 615, 505, 90],
        [465, 725, 505, 90],
        [465, 840, 505, 90],
        [465, 935, 505, 90],
    ]
    ROI_second = [
        [465, 1102, 505, 100],
        [465, 1212, 505, 90],
        [465, 1327, 505, 90],
        [465, 1435, 505, 90],
        [465, 1530, 505, 100],
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
    team1 = pytesseract.image_to_string(img1).replace(" ","_")
    update(img_name,1)
    x,y,w,h = ROI_secondname
    img2 = getThreshold(img[y:y+h, x:x+w])
    team2 = pytesseract.image_to_string(img2).replace(" ","_")
    update(img_name,1)
    data = {
        team1: {},
        team2: {}
    }
    ROI_firstteam.extend(ROI_second)

    for i,roi in enumerate(ROI_firstteam):
        x,y,w,h = roi
        
        img1 = getThreshold(img[y:y+h, x:x+w])
        c = centroid(img1)
        wtd = max(32, int(c.shape[1]/32)*32)
        htd = max(32, int(c.shape[0]/32)*32)
        imgs = detect({
                    "image" : c,
                    "east" : "frozen_east_text_detection.pb",
                    "width" : wtd,
                    "height" : htd, 
                    "min_confidence" : 0.5
                })
        if len(imgs) > 0:
            # cv2.imwrite(f'temp/{i}.png',c)
            string1 = pytesseract.image_to_string(c,config='-l eng --psm 4 --oem 1 -c tessedit_char_whitelist=0123456789_-abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ --tessdata-dir .').replace(" ","_")
        else:
            string1 = ""
        if y < 1000:
            f = 0
            teams = team1
        else:
            f = -2
            teams = team2
        update(img_name,1)
        if len(string1) >0:
            temp = {}
            
            for j,score in enumerate(ROI_score):
                hasil = config[label[j]]
                if not hasil:
                    continue
                a,b,c,d = score
                if j == 0:
                    if i == 3:
                        img2 = getThreshold(img[y+24+f-15:y+f+20+d, a:a+c])
                    elif i == 9:
                        img2 = getThreshold(img[y+26+f:y+33+f+d, a:a+c])
                    else:
                        img2 = getThreshold(img[y+22+f:y+30+f+d, a:a+c])
                    img2 = centroid(img2)
                    string2 = pytesseract.image_to_string(img2, config="--psm 8 --oem 1 -c tessedit_char_whitelist=0123456789 --tessdata-dir .").replace(" ","")
                else:
                    img2 = getThreshold(img[y:y+d, a:a+c])
                    img2 = centroid(img2)
                    string2 = pytesseract.image_to_string(img2, config="--psm 7 --oem 0 -c tessedit_char_whitelist=0123456789, --tessdata-dir .").replace(" ","")
                
                string2=string2.replace(",","").replace(".",'')
                if string2 == '':
                    string2 = '0'
                temp[label[j]] = int(string2)
                update(img_name,1)
            data[teams].update({string1:temp})
        else:
            for j,score in enumerate(ROI_score):
                hasil = config[label[j]]
                if not hasil:
                    continue
                update(img_name,1)
                sleep(0.1)
    end = time.time()
    result = {
        "filename" : os.path.basename(img_name),
        "request" : config,
        "data" : data,
        "time" : str(end-start)+" seconds"
    }
    return result

