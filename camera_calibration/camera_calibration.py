import numpy as np
import cv2 as cv
import glob

# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((8*6,3), np.float32)
objp[:,:2] = np.mgrid[0:8,0:6].T.reshape(-1,2)
# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.
flag = True
camera = cv.VideoCapture(0)
while len(objpoints) < 20:
    res, img = camera.read()
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (8,6), None)
    # If found, add object points, image points (after refining them)
    if ret == True:
        print("corners: {}".format(len(corners)))
        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners)
        # Draw and display the corners
        cv.drawChessboardCorners(img, (8,6), corners2, ret)
        cv.imshow('img', img)
        cv.waitKey(500)
        print(f"len(objpoints): {len(objpoints)}")
cv.destroyAllWindows()
ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
# retval, cameraMatrix, distCoeffs, rvecs, tvecs

print("ret = {}".format(ret))
print("mtx = {}".format(mtx.tolist()))
print("dist = {}".format(dist.tolist()))
print("rvecs = {}".format(rvecs))
print("tvecs = {}".format(tvecs))


# camera #2 (1920x1080):
# ret = 0.4930916662045498
# mtx = [[432.92018461461635, 0.0, 328.8542744949321], [0.0, 431.2999010598182, 273.83191275246776], [0.0, 0.0, 1.0]]
# dist = [[0.04685816122773425, -0.0019294622916786045, 0.0005839852493213779, 0.004529919725486861, -0.027340485579360134]]
# rvecs = [array([[ 0.08616734],
#        [-0.14679519],
#        [ 0.18425918]]), array([[ 0.05770538],
#        [-0.17618515],
#        [ 0.20042916]]), array([[ 0.04598856],
#        [-0.31621142],
#        [ 0.1364377 ]]), array([[ 0.02692659],
#        [-0.32722744],
#        [ 0.11577915]]), array([[-0.00396385],
#        [-0.38998265],
#        [ 0.07152618]]), array([[-0.00394853],
#        [-0.39118633],
#        [ 0.07000139]]), array([[-0.02114244],
#        [-0.07072903],
#        [ 0.09018894]]), array([[-0.0477402 ],
#        [-0.09254282],
#        [ 0.0971236 ]]), array([[-0.08618101],
#        [ 0.02085763],
#        [ 0.12142115]]), array([[-0.08448771],
#        [ 0.02066118],
#        [ 0.12182815]]), array([[-0.07715854],
#        [ 0.04855287],
#        [ 0.13030305]]), array([[-0.07150996],
#        [ 0.05887043],
#        [ 0.14807742]]), array([[-0.07111042],
#        [ 0.07968804],
#        [ 0.14929757]]), array([[-0.06730613],
#        [ 0.08382374],
#        [ 0.15114978]]), array([[-0.06713729],
#        [ 0.07999067],
#        [ 0.15740337]]), array([[-0.06570962],
#        [ 0.05866078],
#        [ 0.13338587]]), array([[-0.06488122],
#        [ 0.05983442],
#        [ 0.13727586]]), array([[-0.09678802],
#        [ 0.0957175 ],
#        [ 0.22804171]]), array([[-0.03325634],
#        [ 0.00346045],
#        [ 0.23899067]]), array([[-0.09094335],
#        [ 0.05725029],
#        [ 0.2137047 ]])]
# tvecs = [array([[-6.43554595],
#        [-4.92254691],
#        [11.03924143]]), array([[-6.6715109 ],
#        [-4.8464052 ],
#        [10.36385788]]), array([[-5.13108142],
#        [-2.98289482],
#        [ 8.34486944]]), array([[-4.73053539],
#        [-2.80855461],
#        [ 8.14135061]]), array([[-3.94361647],
#        [-2.49462743],
#        [ 5.96901492]]), array([[-3.91554677],
#        [-2.46296218],
#        [ 5.96616223]]), array([[-4.49807784],
#        [-2.16868318],
#        [ 8.99631983]]), array([[-4.48704932],
#        [-2.19135785],
#        [ 8.32920581]]), array([[-4.82272883],
#        [-2.45438511],
#        [ 7.89790454]]), array([[-4.83718386],
#        [-2.46061067],
#        [ 7.92804599]]), array([[-5.11386125],
#        [-2.5797051 ],
#        [ 8.59151468]]), array([[-5.48044196],
#        [-2.78134054],
#        [ 8.99105013]]), array([[-5.54976476],
#        [-2.77149822],
#        [ 9.42216687]]), array([[-5.51679683],
#        [-2.6808844 ],
#        [ 9.57397846]]), array([[-5.76441156],
#        [-2.35568174],
#        [ 9.5673428 ]]), array([[-5.01458086],
#        [-2.15310458],
#        [ 8.89613138]]), array([[-4.96280922],
#        [-2.27467127],
#        [ 8.9387464 ]]), array([[-3.61145968],
#        [-3.1510877 ],
#        [10.24562863]]), array([[-4.34446726],
#        [-2.95819961],
#        [ 8.80496659]]), array([[-4.16340779],
#        [-3.09007566],
#        [ 8.70929319]])]
