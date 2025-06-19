import cv2
import mediapipe as mp
import pygame
import math
import time

# Playlist of songs
playlist = [
    "D:\\Sixth Semester\\ML Project\\Aaju Mithila Nagariya Nihal Sakhiya_320(PaglaSongs).mp3",
    "D:\\Sixth Semester\\ML Project\\Are Dwarpalo Kanhaiya Se Kehdo- [PagalWorld.NL].mp3",
    "D:\\Sixth Semester\\ML Project\\Aigiri Nandini.mp3"
]
song_index = 0

# Initialize Pygame mixer
pygame.mixer.init()
pygame.mixer.music.load(playlist[song_index])
pygame.mixer.music.play()
pygame.mixer.music.set_volume(0.5)  # Initial volume

# Mediapipe setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

cap = cv2.VideoCapture(0)

def count_fingers(hand_landmarks):
    tips_ids = [4, 8, 12, 16, 20]
    fingers = []

    # Thumb (ignored)
    fingers.append(0)

    # Index to pinky
    for id in range(1, 5):
        if hand_landmarks.landmark[tips_ids[id]].y < hand_landmarks.landmark[tips_ids[id] - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return sum(fingers)

paused = False
last_action = None
last_action_time = 0
action_text = ""
action_timeout = 2  # seconds

def play_song(index):
    pygame.mixer.music.load(playlist[index])
    pygame.mixer.music.play()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    fingers_up = 0
    current_time = time.time()

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

            fingers_up = count_fingers(handLms)

            if fingers_up != last_action:
                if fingers_up == 1:
                    if paused:
                        pygame.mixer.music.unpause()
                        action_text = "Play"
                        print("Play")
                    else:
                        pygame.mixer.music.pause()
                        action_text = "Pause"
                        print("Pause")
                    paused = not paused

                elif fingers_up == 2:
                    song_index = (song_index + 1) % len(playlist)
                    play_song(song_index)
                    action_text = "Next Song"
                    print("Next Song")

                elif fingers_up == 3:
                    song_index = (song_index - 1) % len(playlist)
                    play_song(song_index)
                    action_text = "Previous Song"
                    print("Previous Song")

                elif fingers_up == 4:
                    pygame.mixer.music.set_volume(min(1.0, pygame.mixer.music.get_volume() + 0.1))
                    action_text = "Volume Up"
                    print("Volume Up")

                elif fingers_up == 5:
                    pygame.mixer.music.set_volume(max(0.0, pygame.mixer.music.get_volume() - 0.1))
                    action_text = "Volume Down"
                    print("Volume Down")

                last_action = fingers_up
                last_action_time = current_time

    # Show number of fingers
    cv2.putText(frame, f'Fingers: {fingers_up}', (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show the action for a few seconds
    if current_time - last_action_time < action_timeout and action_text:
        cv2.putText(frame, f'Action: {action_text}', (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("Music Controller", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
