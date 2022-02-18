import cv2 as cv
import numpy as np
  
inputfile = 'test.mov'
capture = cv.VideoCapture(cv.samples.findFileOrKeep(inputfile))

with open("output.srt", "w") as f:

  if not capture.isOpened():
    print('Unable to open: ' + inputfile)
    exit(0)

  previous_timestamp = "00:00:00,000"

  while True:
    ret, frame = capture.read()
    if frame is None:
        break
    
    # convert to LAB color space
    lab = cv.cvtColor(frame, cv.COLOR_BGR2LAB)

    # separate channels
    L,A,B=cv.split(lab)

    # compute minimum and maximum in 5x5 region using erode and dilate
    kernel = np.ones((5,5),np.uint8)
    min = cv.erode(L,kernel,iterations = 1)
    max = cv.dilate(L,kernel,iterations = 1)

    # convert min and max to floats
    min = min.astype(np.float64) 
    max = max.astype(np.float64) 

    # compute local contrast
    contrast = (max-min)/(max+min)

    # get average across whole image
    average_contrast = 100*np.mean(contrast)
    
    f.write(str(capture.CAP_PROP_POS_FRAMES))

    milliseconds = capture.CAP_PROP_POS_MSEC
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    current_timestamp = f'{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{int(milliseconds):03d}'
    f.write(f'{previous_timestamp} --> {current_timestamp}')
    previous_timestamp = current_timestamp
    f.write(str(average_contrast)+'%')
    f.write('')
