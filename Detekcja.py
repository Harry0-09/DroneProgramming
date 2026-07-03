import cv2
import time
import keyboard
from djitellopy import Tello
from main import DroneDetector

drone = Tello()
drone.connect()
drone.streamon()
frame_read = drone.get_frame_read()

detector = DroneDetector()

print(f"Bateria: {drone.get_battery()}%")

drone.takeoff()
drone.send_rc_control(0, 0, 20, 0)

time.sleep(2)

try:
    while True:
        frame = frame_read.frame
        if frame is None:
            continue

        h, w, _ = frame.shape

        img_center_x = int(w/2)
        img_center_y = int(h/2)

        #bbox = [200, 150, 450, 400] 

        bbox = detector.get_bbox(frame) # x_min, y_min, x_max, y_max

        if bbox:

            x_min, y_min, x_max, y_max = bbox

            box_center_x = int((x_min + x_max)/2)
            box_centr_y = int((y_min + y_max)/2)

            error_x = box_center_x - img_center_x
            error_y = box_centr_y - img_center_y

            box_area = (x_max - x_min)*(y_max-y_min)
            
            # kordy, promien, kolor, grubosc
            cv2.circle(frame, (img_center_x, img_center_y), 5, (0,0,255), -1) #srodek ekranu
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0,255,0), 2) #box
            cv2.circle(frame, (box_center_x, box_centr_y), 5, (0,255,0), -1) # srodek boxa
            cv2.line(frame, (img_center_x , img_center_y), (box_center_x, box_centr_y), (255, 0,0), 2) #wektor bledu

            font = cv2.FONT_HERSHEY_SIMPLEX
            
            #text, kordy, czcionka, fontmultiplater, kolor, grubosc
            cv2.putText(frame, f"Error po x: {error_x}", (20, 40), font, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Error po y: {error_y}", (20, 70), font, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Pole: {box_area}", (20, 100), font, 0.7, (255, 255, 255), 2)


            kp_x = 0.25 # czulosc reakcji lewo/prawo
            kp_y = -0.25
            lr_speed = int(error_x * kp_x)
            lr_speed = max(-30, min(30, lr_speed))

            fb_speed = 20

            ud_speed = int(error_y * kp_y)

            if box_area > 400000:
                cv2.putText(frame, "LADOWANIE", (20, 130), font, 0.7, (0, 0, 255), 2)
                cv2.imshow("Tracker", frame)
                cv2.waitKey(1)
                
                drone.send_rc_control(0, 25, 0, 0)
                time.sleep(1.0)
                
                drone.send_rc_control(0, 0, 0, 0)
                drone.land()
                break
            else:
                drone.send_rc_control(lr_speed, fb_speed, ud_speed, 0)
        
        else:
            cv2.putText(frame, "TRYB MANUALNY", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            lr_speed = 0
            fb_speed = 0
            ud_speed = 0 # predkosc gora/dol
            
            # Odczyt klawiszy
            if keyboard.is_pressed('w'):
                fb_speed = 25
            elif keyboard.is_pressed('s'):
                fb_speed = -25
                
            if keyboard.is_pressed('a'):
                lr_speed = -25
            elif keyboard.is_pressed('d'):
                lr_speed = 25
                
            # Kontrola wysokosci (Spacja = gora, Shift = dol)
            if keyboard.is_pressed('space'):
                ud_speed = 25
            elif keyboard.is_pressed('shift'):
                ud_speed = -25
                
            drone.send_rc_control(lr_speed, fb_speed, ud_speed, 0)

        cv2.imshow("Tracker", frame) 
        
        if cv2.waitKey(1) & 0xFF == ord("q") or keyboard.is_pressed('q'):
            break
finally:
    try:
        drone.send_rc_control(0, 0, 0, 0)
        drone.land()
    except:
        pass

    drone.streamoff()
    cv2.destroyAllWindows()