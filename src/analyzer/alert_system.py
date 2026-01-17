import cv2
import pyttsx3
import time
import threading
import queue

class AlertSystem:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 175)
        self.alert_queue = queue.Queue()
        self.is_speaking = False
        self.last_alert_time = {}
        self.alert_cooldown = 3.0
        self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
        self.tts_thread.start()

    def _tts_worker(self):
        while True:
            text = self.alert_queue.get()
            if text is None: break
            self.is_speaking = True
            self.engine.say(text)
            self.engine.runAndWait()
            self.is_speaking = False
            self.alert_queue.task_done()

    def add_alert(self, label, position, distance):
        current_time = time.time()
        alert_key = f"{label}_{position}"
        if alert_key in self.last_alert_time:
            if current_time - self.last_alert_time[alert_key] < self.alert_cooldown:
                return
        dist_str = f"{distance:.1f} meters" if distance >= 1 else f"{int(distance*100)} centimeters"
        alert_text = f"{label} at {position}, {dist_str} away."
        if distance < 1.0:
            alert_text = f"Warning! {alert_text}"
        self.alert_queue.put(alert_text)
        self.last_alert_time[alert_key] = current_time

    def speak_summary(self, summary_text):
        self.alert_queue.put(f"Summary: {summary_text}")

    def stop(self):
        while not self.alert_queue.empty() or self.is_speaking:
            time.sleep(0.1)
        self.alert_queue.put(None)
        try:
            self.tts_thread.join(timeout=2.0)
        except Exception:
            pass
