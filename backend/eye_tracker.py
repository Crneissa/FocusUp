import cv2
from eye_tracking.gaze_tracking import GazeTracking
import time
import requests
import threading

class EyeTracker:
    def __init__(self, user_id, api_url="http://127.0.0.1:5000/strike"):
        self.user_id = user_id
        self.api_url = f"{api_url}/{user_id}"
        self.gaze = GazeTracking()
        self.webcam = cv2.VideoCapture(0)
        if not self.webcam.isOpened():
            print("Error: Could not open webcam.")
        self.looking_away_start_time = None
        self.strikes = 0
        self._running = False
        self._thread = None
        print(f"EyeTracker initialized for user {user_id}") #add this line.

    def start_tracking(self):
        print(f"Starting eye tracking for user {self.user_id}") #add this line.
        self._running = True
        self._thread = threading.Thread(target=self._run)
        try:
            self._thread.start()
            print(f"Eye tracking thread started for user {self.user_id}") #add this line.
        except Exception as e:
            print(f"Error starting eye tracking thread: {e}")

    def stop_tracking(self):
        print(f"Stopping eye tracking for user {self.user_id}") #add this line.
        self._running = False
        if self._thread:
            self._thread.join()
        self.webcam.release()
        print(f"Eye tracking stopped for user {self.user_id}") #add this line.

    def _run(self):
        print(f"Eye tracking run method started for user {self.user_id}") #add this line.
        while self._running:
            _, frame = self.webcam.read()
            if frame is None:
                print("Error: Could not read frame from webcam.")
                break #exit loop.
            self.gaze.refresh(frame)

            if self.gaze.is_center():
                self.looking_away_start_time = None
            else:
                if self.looking_away_start_time is None:
                    self.looking_away_start_time = time.time()
                elif time.time() - self.looking_away_start_time >= 15:
                    self.strikes += 1
                    self.send_strike()
                    self.looking_away_start_time = time.time()

            if cv2.waitKey(1) == 27:
                break
        print(f"Eye tracking run method ended for user {self.user_id}") #add this line.

    def send_strike(self):
        try:
            requests.post(self.api_url, json={"strikes": self.strikes})
            print(f"Strike sent to {self.api_url}, strikes: {self.strikes}") #add this line.
        except requests.exceptions.RequestException as e:
            print(f"Error sending strike to {self.api_url}: {e}")

    def get_strikes(self):
        return self.strikes

    def reset_strikes(self):
        self.strikes = 0
        print(f"Strikes reset for user {self.user_id}") #add this line.