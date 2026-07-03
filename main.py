import cv2
import numpy as np

class DroneDetector:
    def __init__(self):
        # Hue (Odcień)
        # Saturation (Nasycenie)
        # Value (Jasność)
        self.lower_green = np.array([35, 60, 60])
        self.upper_green = np.array([85, 255, 255])
        
        self.min_area = 1500

    def get_bbox(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        mask = cv2.inRange(hsv, self.lower_green, self.upper_green)
        
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        largest_contour = None
        max_area = 0
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > self.min_area and area > max_area:
                max_area = area
                largest_contour = cnt
        
        if largest_contour is not None:
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            return [x, y, x + w, y + h]
        
        return None