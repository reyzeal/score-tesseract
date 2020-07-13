import cv2
import numpy
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import _thread
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
    if w < 3840 or h < 2160:
        img = cv2.resize(img, (3840, 2160), interpolation=cv2.INTER_CUBIC)
    def kmeans(img, username = False):
        if username:
            img = cv2.resize(img, None, fx=1.2, fy=1.2, interpolation=cv2.INTER_CUBIC)
            img=cv2.medianBlur(img, 1)
            alpha = 1.5 # Contrast control (1.0-3.0)
            beta = 5 # Brightness control (0-100)

            img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
        Z = img.reshape((-1,3))

        # convert to np.float32
        Z = numpy.float32(Z)

        # define criteria, number of clusters(K) and apply kmeans()
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        K = 2
        ret,label,center=cv2.kmeans(Z,K,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)

        # Now convert back into uint8, and make original image
        center = numpy.uint8(center)
        res = center[label.flatten()]
        res2 = res.reshape((img.shape))
        return res2

    def getThreshold(img):
        img = cv2.resize(img, None, fx=1.2, fy=1.2, interpolation=cv2.INTER_CUBIC)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        k = numpy.ones((1, 1), numpy.uint8)
        # img = cv2.threshold(cv2.bilateralFilter(img, 5, 75, 75), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        img = cv2.threshold(cv2.medianBlur(img, 5), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # th3 = cv2.dilate(gray, kernel, iterations=1)
        # th3 = cv2.dilate(gray, kernel, iterations=1)
        img = cv2.threshold(img,127,255,cv2.THRESH_BINARY)[1]
        
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
        img = cv2.bitwise_not(img)
        img = cv2.dilate(img,kernel,iterations = 1)
        return img

    def getThreshold2(img):
        # img = cv2.resize(img, None, fx=1.2, fy=1.2, interpolation=cv2.INTER_CUBIC)
        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
        img = cv2.inRange(img,img[10][10],img[10][10])
        img = cv2.threshold(img,127,255,cv2.THRESH_BINARY)[1]
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
        return img      
        
    def getThreshold3(img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
        img = cv2.inRange(img,img[10][10],img[10][10])
        img = cv2.threshold(img,127,255,cv2.THRESH_BINARY)[1]
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
        xi = cv2.bitwise_not(img)
        blur = cv2.GaussianBlur(xi,(5,5),0)
        ximage = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
        contours,hierarchy = cv2.findContours(ximage, 1, 2)
        xmin, ymin, xmax, ymax = [img.shape[1], img.shape[0], 0, 0]
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area >= 10:
                x,y,w,h = cv2.boundingRect(cnt)
                # ximage = img[y:y+h,x:x+w] 
                xmin = min(xmin,x)
                xmax = max(xmax,x+w)
                ymin = min(ymin,y)
                ymax = max(ymax,y+h)
        return img[ymin-15:ymax+15,xmin-15:xmax+15]
    scale_percent = 40 # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
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
    clster = kmeans(img[y:y+h, x:x+w])
    img1 = getThreshold2(clster)
    id = uuid.uuid4()
    cv2.imwrite(f'temp/roi_t1{id}.jpg', img1)
    
    team1 = pytesseract.image_to_string(f'temp/roi_t1{id}.jpg').replace(" ","_")
    os.unlink(f'temp/roi_t1{id}.jpg')
    x,y,w,h = ROI_secondname
    clster = kmeans(img[y:y+h, x:x+w])
    img2 = getThreshold2(clster)
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
        clster = cv2.resize(img[y:y+h, x:x+w], None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
        clster = kmeans(clster, username=True)
        cv2.imwrite(f'temp/roi_{i}.jpg', img[y:y+h, x:x+w])
        img1 = getThreshold2(clster)
        cv2.imwrite(filename, img1)
        string1 = pytesseract.image_to_string(filename).replace(" ","_")
        if len(string1) == 0:
            
            img1 = getThreshold3(clster)
            if not img1.empty():
                cv2.imwrite(filename, img1)
                w,h = img1.shape[:2]
                w = int(w/32)*32
                if w == 0:
                    w = 32
                imgs = detect({
                    "image" : filename,
                    "east" : "frozen_east_text_detection.pb",
                    "width" : w,
                    "height" : 32, 
                    "min_confidence" : 0.5
                })
                if len(imgs) > 0:
                    cv2.imwrite(filename, imgs[0])
                    string1 = pytesseract.image_to_string(filename, config='--psm 13 --oem 3 --tessdata-dir .').replace(" ","_")
        # os.unlink(filename)
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
                    clster = kmeans(img[y+24+f:y+24+f+d, a:a+c])
                    img2 = getThreshold2(clster)
                    cv2.imwrite(filename2, img2)
                    cv2.imwrite(f'temp/roi_{i}{j}.jpg', img[y+24+f:y+24+f+d, a:a+c])
                    string2 = pytesseract.image_to_string(filename2, config="--psm 7 --oem 0 -c tessedit_char_whitelist=0123456789 -c tessedit_do_invert=0 --tessdata-dir .")
                else:
                    clster = kmeans(img[y:y+d, a:a+c])
                    img2 = getThreshold2(clster)
                    cv2.imwrite(filename2, img2)
                    cv2.imwrite(f'temp/roi_{i}{j}.jpg', img[y:y+d, a:a+c])
                    string2 = pytesseract.image_to_string(filename2, config="--psm 8 --oem 0 -c tessedit_char_whitelist=0123456789, -c tessedit_do_invert=0 --tessdata-dir .")
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

