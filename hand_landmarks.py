import cv2
import serial # pip install pyserial
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
n_leds = index2thumb_dist =  0

port_name = 'COM6'
baudrate = 115200
arduino = serial.Serial(port_name, baudrate=baudrate, timeout=0.1)

cap = cv2.VideoCapture(0)

def count_finges(hand):
    # Function to count the three middle fingers (if raised)
    one = int(hand.landmark[8].y < hand.landmark[7].y)
    two = int(hand.landmark[12].y < hand.landmark[11].y)
    three = int(hand.landmark[16].y < hand.landmark[15].y)
    return one + two + three

def get_fingers_dist(hand):
    # Function to calculate distance (X-axis) from index to thumb
    index_finger_x = hand.landmark[4].x
    thumb_finger_x = hand.landmark[8].x
    index2thumb_dist = min(25,int(abs(index_finger_x - thumb_finger_x) * 100))
    return index2thumb_dist

def send_arduino(message):
    # Function to send message to arduino
    arduino.write(bytes(message, 'utf-8')) 

with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
  while cap.isOpened():
    success, image = cap.read()

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:
        all_hands = results.multi_hand_landmarks

        # if one hand detected, control brightness
        if len(all_hands) == 1:
            index2thumb_dist = get_fingers_dist(all_hands[0])

        # if two hands, control brightness & switch between leds
        elif len(all_hands) == 2:
            index2thumb_dist = get_fingers_dist(all_hands[0])
            n_leds = count_finges(all_hands[1])
            
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                image,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())
        
        # Signal to send to arduino
        value_to_send = str(n_leds) + "|" + str(index2thumb_dist)
        send_arduino(value_to_send)
        print(value_to_send, end='\r')
        
    # Flip the image horizontally for a selfie-view display.
    flipped_img = cv2.flip(image, 1)
    cv2.imshow('MediaPipe Hands', flipped_img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break
    
cap.release()
cv2.destroyAllWindows()
arduino.close()