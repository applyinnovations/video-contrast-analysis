import cv2 as cv
import numpy as np
  
inputfile = 'test.mp4'
capture = cv.VideoCapture(cv.samples.findFileOrKeep(inputfile))

with open("output.srt", "w") as f:

  if not capture.isOpened():
    print('Unable to open: ' + inputfile)
    exit(0)

  previous_timestamp = "00:00:00,000"
  line_count = 0

  while True:
    ret, frame = capture.read()
    if frame is None:
        break
    pos = capture.get(cv.CAP_PROP_POS_FRAMES)
    milliseconds = capture.get(cv.CAP_PROP_POS_MSEC)
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    current_timestamp = f'{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{int(milliseconds):03d}'
    valid = previous_timestamp != current_timestamp

    if valid:
      line_count = line_count + 1
      f.write(f'{int(line_count)}\n')
      f.write(f'{previous_timestamp} --> {current_timestamp}\n')

      # Contrast
      gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
      average_contrast = gray.std()
      
      # Lightness
      lab = cv.cvtColor(frame, cv.COLOR_BGR2LAB)
      L,A,B=cv.split(lab)
      average_lightness = np.mean(L) / 2.55

      # Brightness
      hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
      H,S,V=cv.split(hsv)    
      average_brightness = np.mean(V) / 2.55

      # Color count
      rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
      colors = np.dot(rgb.astype(np.uint32),[1,256,65536]) 
      unique_color_count = len(np.unique(colors))

      # Warmth
      R,G,B=cv.split(rgb) 
      red = np.mean(R)
      blue = np.mean(B)
      temperature = 'warm' if red > blue else 'cool'

      # write to output
      f.write(f'contrast {float(round(np.nan_to_num(average_contrast, 0), 3)):.0f}%\n')
      f.write(f'lightness {float(round(average_lightness, 3)):.0f}%\n')
      f.write(f'brightness {float(round(average_brightness, 3)):.0f}%\n')
      f.write(f'colors {int(round(unique_color_count / 1000, 3))}k\n')
      f.write(f'temperature {temperature}\n')

      f.write('\n')
    previous_timestamp = current_timestamp
