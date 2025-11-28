

import cv2 as cv
import time

from ultralytics import YOLO

from libss import arduinoserialsender
from libss import senddiscord


MODEL = YOLO("models/yolo11s.pt")
DOG_CLASS = 16

# cooldown between each discord messages
DISCORD_SENDING_COOLDOWN_TIME = 10 # seconds


# main ----
def main() :
    
    
    ## declare variables for main loop ----
    previous_dog_len = 0
    time_since_discord_send = 0
    
    
    ## setup ----
    try   :
        open_serial = arduinoserialsender.openSerial('COM13', True, True)
    except:
        print("cant open serial selected")
        open_serial = None

    if open_serial is not None : arduinoserialsender.sendOutput(open_serial, 13, 1.0, False)
    
    cv.namedWindow("result", cv.WINDOW_NORMAL)
    capture = cv.VideoCapture(0)
    
    
    ## loop  ----
    while capture.isOpened() :
        
        
        
        ### pre-check ----
        ret, frame = capture.read()
        
        if not ret : break 
  
        key = cv.waitKey(1) & 0xFF
        
        if key == ord("e") : break
        
        

        ### main ----
        frame = cv.flip(frame, 1)
        frame = cv.resize(frame, None, fx=0.5, fy=0.5)
        
        predict_results = MODEL.predict(frame, classes=[DOG_CLASS], verbose=False)
        
        
        
        ### drawing ----
        for detected_dog in predict_results[0].boxes : 
            x1, y1, x2, y2 = detected_dog.xyxy[0].numpy()
            
            #======================
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            #======================
            
            cv.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 255), 2)
            
            cv.circle(frame, (int(center_x), int(center_y)), 5, (255, 255, 255), 2)
            
            cv.putText(
                frame, 
                MODEL.names[int(detected_dog.cls)], 
                (int(x1), int(y1)), 
                cv.FONT_HERSHEY_SIMPLEX, 
                1,
                (0, 0, 0), 
                4
            )
            cv.putText(
                frame, 
                MODEL.names[int(detected_dog.cls)], 
                (int(x1), int(y1)), 
                cv.FONT_HERSHEY_SIMPLEX, 
                1, 
                (255, 255, 255), 
                2
            )
        
        
        
        ###  dog handle ----
        #### if saw dog ----
        if previous_dog_len == 0 and len(predict_results[0]) > 0 :
            if open_serial is not None : arduinoserialsender.sendOutput(open_serial, 13, 0.0, False)

            if time.time() - time_since_discord_send >= DISCORD_SENDING_COOLDOWN_TIME :
                time_since_discord_send = time.time()
                
                cv.imwrite(f"sendtemp/dog.jpg", frame)
                senddiscord.send_message(
                    f" -> Dog Detected !",
                    f"sendtemp/dog.jpg"
                )
        
        #### if dog gone ----
        elif previous_dog_len > 0 and len(predict_results[0]) == 0 :
            if open_serial is not None : arduinoserialsender.sendOutput(open_serial, 13, 1.0, False)
        
        
        
        ### update  ----
        previous_dog_len = len(predict_results[0])
        ### display ----
        cv.imshow("result", frame)

    
    
    ## cleanup ----
    capture.release()
    cv.destroyAllWindows()
    if open_serial is not None : arduinoserialsender.closeSerial(open_serial, True)






if __name__ == "__main__" :
    main()