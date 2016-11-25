import cv2
import time
import os


def snapshot_generator(device=0, sleep=0.25, img_format = 'PNG', img_quality=0, debug=False,filename=None):
    '''
    
    Returns a function that takes a snapshot and returns an buffer already formatted
    
    Parameters:
    
    device: integer, indicates which camera you will use. 
    Normally is 0, but you can check using lsusb (linux) 
    or system_profiler SPUSBDataType (osx).
    
    sleep: float, time the function waits before taking the first snapshot.
           (if there's not enough time, some webcams generate a very dark image) 
    
    img_format: 'PNG' or 'JPG'
    
    img_quality: 0 to 1 if PNG or 0 to 100 if JPG
    
    The returned function controls the generator. Call it without arguments to take a new picture
    or with False to close the device. Closing the device reduces the max frequency.
    '''
    
    if not debug:
        capture = cv2.VideoCapture(device)

        time.sleep(sleep)

        if capture.isOpened():
            print "Device initialised, ready to capture!"
        else:
            print "Device failed..."
            return -1
    
    def capture_image_gen(debug,filename):
        while True:
            if debug and filename!=None:
                frame = cv2.imread(filename)
            else:
                grabbed, frame = capture.read()

            if img_format == 'PNG':
                if 1>=img_quality>=0:
                    yield cv2.imencode('.png', cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), 
                                       [cv2.cv.CV_IMWRITE_PNG_COMPRESSION, img_quality])[1].tobytes(),frame
            elif img_format == 'JPG':
                if 100>=img_quality>=0:
                    yield cv2.imencode('.png', cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), 
                                       [cv2.cv.CV_IMWRITE_JPEG_QUALITY, img_quality])[1].tobytes(),frame
                    
            else:
                raise Exception("Error! Image format (img_format) must be \'PNG\' or \'JPG\'!")

                
    init_gen = capture_image_gen(debug,filename)  
    
    def wrapper(cmd=True,ret_orig=False):
        if cmd:
            if ret_orig:
                return init_gen.next()
            else:
                return init_gen.next()[0]
        else:
            if not debug:
                capture.release() # closes the camera, video file, etc
                print "Device closed, exiting..."
            return 0

        
    return wrapper