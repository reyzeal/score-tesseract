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
            alpha = 1.5 # Contrast control (1.0-3.0)
            beta = 0 # Brightness control (0-100)

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
    
        img = cv2.inRange(img,img[0][0],img[0][0])
        img = cv2.threshold(img,127,255,cv2.THRESH_BINARY)[1]
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
        # img = cv2.dilate(img,kernel,iterations = 1)
        return img

    scale_percent = 40 # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    ROI_firstname = [347, 447, 200, 45]
    ROI_secondname = [347, 1042, 200, 45]
    ROI_firstteam = [
        [471, 505, 505, 100],
        [471, 615, 505, 90],
        [471, 725, 505, 90],
        [471, 835, 505, 85],
        [471, 935, 505, 90],
    ]
    ROI_second = [
        [471, 1102, 505, 100],
        [471, 1222, 505, 90],
        [471, 1327, 505, 90],
        [471, 1435, 505, 85],
        [471, 1540, 505, 90],
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
        clster = kmeans(img[y:y+h, x:x+w], username=True)
        # cv2.imwrite(f'temp/roi_{i}_.jpg', img[y:y+h, x:x+w])
        img1 = getThreshold2(clster)
        cv2.imwrite(filename, img1)
        string1 = pytesseract.image_to_string(filename, config='--oem 1 -c tessedit_char_whitelist=0123456789-_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ --tessdata-dir ./fast').replace(" ","_")
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
                    clster = kmeans(img[y+24+f:y+24+f+d, a:a+c])
                    img2 = getThreshold2(clster)
                    cv2.imwrite(filename2, img2)
                    string2 = pytesseract.image_to_string(filename2, config="--psm 7 --oem 0 -c tessedit_char_whitelist=0123456789 -c tessedit_do_invert=0 --tessdata-dir .")
                else:
                    clster = kmeans(img[y:y+d, a:a+c])
                    img2 = getThreshold2(clster)
                    cv2.imwrite(filename2, img2)
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

