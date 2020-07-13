from text_detection import detect
import cv2

imgs = detect({
                "image" : 'Switchblade_20200506182253.jpg',
                "east" : "frozen_east_text_detection.pb",
                "width" : 3200,
                "height" : 3200, 
                "min_confidence" : 0.2
            })
for i in imgs:
    cv2.imshow('x', i)
cv2.waitKey(0)