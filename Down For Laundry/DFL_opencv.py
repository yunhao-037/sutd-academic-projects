# -*- coding: utf-8 -*-
"""
Created on Tue Oct 7 11:41:42 2018

@author: Caihao.Cui
"""
from __future__ import print_function
import pyzbar.pyzbar as pyzbar
import cv2
import time
def qrcodescan():
    # get the webcam:
    cap = cv2.VideoCapture(0)

    cap.set(3, 640)
    cap.set(4, 480)
    # 160.0 x 120.0
    # 176.0 x 144.0
    # 320.0 x 240.0
    # 352.0 x 288.0
    # 640.0 x 480.0
    # 1024.0 x 768.0
    # 1280.0 x 1024.0
    time.sleep(2)

    def decode(im):
        # Find barcodes and QR codes
        decodedObjects = pyzbar.decode(im)
        # Print results
        for obj in decodedObjects:
            print('Type : ', obj.type)
            print('Data : ', obj.data, '\n')
        return decodedObjects
    machine = None
    while (cap.isOpened()):
        # Capture frame-by-frame
        ret, frame = cap.read()
        # Our operations on the frame come here
        im = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Display the resulting frame
        cv2.imshow('frame', frame)
        key = cv2.waitKey(1)
        decodedObjects = decode(im)
        if len(decodedObjects) != 0:
            machine = decodedObjects[0].data
            break
        if key & 0xFF == ord('q'):
            break
    a = str(machine).split("'")
    b = a[1]
    print(b)
    print(b[0], b[1])
        # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
    return b