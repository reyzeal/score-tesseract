import cv2
import numpy
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import _thread
import time
start = time.time()
kernel  = (3,3)
img = cv2.imread('Switchblade_20200507170939.jpg')
def kmeans(img):
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
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret2,th3 = cv2.threshold(gray,126,255,cv2.THRESH_BINARY)
    opening = cv2.morphologyEx(th3, cv2.MORPH_OPEN, kernel)
    opening = cv2.bitwise_not(opening)
    opening = cv2.dilate(opening,kernel,iterations = 2)
    return opening

def getThreshold2(img):
    HSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(HSV,HSV[0][0],HSV[0][0])
    ret2,th3 = cv2.threshold(mask,127,255,cv2.THRESH_BINARY)
    opening = cv2.morphologyEx(th3, cv2.MORPH_OPEN, kernel)
    opening = cv2.dilate(opening,kernel,iterations = 3)
    return opening

scale_percent = 40 # percent of original size
width = int(img.shape[1] * scale_percent / 100)
height = int(img.shape[0] * scale_percent / 100)
dim = (width, height)

ROI_firstteam = [
    [471, 505, 505, 100],
    [471, 615, 505, 90],
    [471, 725, 505, 90],
    [471, 835, 505, 85],
    [471, 935, 505, 90],
]
ROI_second = [
    [471, 1112, 505, 100],
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
data = {}
ROI_firstteam.extend(ROI_second)

for i,roi in enumerate(ROI_firstteam):
    x,y,w,h = roi
    if y < 1000:
        f = 0
    else:
        f = -2
    # cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),5)
    img1 = getThreshold(img[y:y+h, x:x+w])
    cv2.imwrite(f'temp/roi_f1{i}.jpg', img1)
    string1 = pytesseract.image_to_string(f'temp/roi_f1{i}.jpg',config="--psm 7 --oem 3 -c tessedit_do_invert=0 --tessdata-dir .").replace(" ","_")
    print(string1, end="\t")
    if len(string1) >0:
        temp = {}
        for j,score in enumerate(ROI_score):
            a,b,c,d = score
            
            if j == 0:
                clster = kmeans(img[y+24+f:y+24+f+d, a:a+c])
                # cv2.rectangle(img,(a,y+24+f),(a+c,y+24+f+d),(0,0,255),5)
                img2 = getThreshold2(clster)
                cv2.imwrite(f'temp/roi_f1{i}{j}.jpg', img2)
                string2 = pytesseract.image_to_string(f'temp/roi_f1{i}{j}.jpg', config="--psm 7 --oem 0 -c tessedit_char_whitelist=0123456789 -c tessedit_do_invert=0 --tessdata-dir .")
            else:
                clster = kmeans(img[y:y+d, a:a+c])
                # cv2.rectangle(img,(a,y),(a+c,y+d),(0,0,255),5)
                img2 = getThreshold2(clster)
                cv2.imwrite(f'temp/roi_f1{i}{j}.jpg', img2)
                string2 = pytesseract.image_to_string(f'temp/roi_f1{i}{j}.jpg', config="--psm 8 --oem 0 -c tessedit_char_whitelist=0123456789, -c tessedit_do_invert=0 --tessdata-dir .")
            temp[label[j]] = string2
            print(string2, end="\t")
        data.update({string1:temp})
    print()

end = time.time()
print(end - start)