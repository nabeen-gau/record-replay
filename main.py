import pyautogui as pag
import keyboard as kb
import time
import sys
from pynput import mouse

stop_key = "F12"
record_key = "F11"
play_key = "F10"
recording = False
fps = 60

def main():
    global recording
    window_size = pag.size()
    recorded = None
    try:
        print(f"Reading inputs. <{record_key}> to start recording")
        while True:
            event = kb.read_event()
            if (kb.is_pressed(record_key)):
                recording = not recording
                if recording:
                    recorded = kb.record(until=record_key)
            elif (kb.is_pressed(play_key)):
                if recorded:
                    kb.play(recorded, speed_factor=5)
            elif (kb.is_pressed(stop_key)):
                break
            mouse_pos = pag.position()
            time.sleep(1/fps)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
