import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
##############################################
wCam, hCam = 640, 480
##############################################

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(detectionConfidence=0.7)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
min_vol = volRange[0]
max_vol = volRange[1]
print (min_vol, max_vol)
vol = 0



while True:
    success, img = cap.read()
    if not success:
        print("Failed to capture frame from camera. Exiting...")
        break
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        # print(lmList[4], lmList[8])
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1+x2)//2, (y1+y2)//2

        cv2.circle(img, (x1, y1), 10, (255,0,255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255,0,255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255,0,255), 3)
        cv2.circle(img, (cx, cy), 10, (255,0,255), cv2.FILLED)

        length = math.hypot(x2-x1, y2-y1)
        # print(length)
        # print(min_vol, max_vol)

        #Hand range 40 to 200
        #Volume range is from -63.5 to 0

        vol = np.interp(length, [40, 200], [min_vol, max_vol])
        print(vol)
        volume.SetMasterVolumeLevel(vol, None)

        if length<40:
            cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)


    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS : {int(fps)}', (40, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255,0,0), 2)

    cv2.imshow("Live Video", img)
    cv2.waitKey(1)