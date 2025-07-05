import pyautogui as pag
import keyboard as kb
import time
import sys
from pynput import mouse
from pynput import keyboard
from pynput.mouse import Button, Controller
from pynput.keyboard import Key
from pynput.keyboard import Controller as key_controller
from enum import Enum, auto

stop_key = Key.f12
record_key = Key.f11
play_key = Key.f10
recording = False
fps = 60
wait_time = 0.1#s

start_recording = False
stop_running = False
play_recording = False

def start_recording_msg():
    print(f"Press <{record_key.name}> to start recording, <{stop_key.name}> to exit.");

def stop_recording_msg():
    print(f"Recording started. Press <{record_key.name}> to stop recording.")

def recording_stopped_msg():
    print(f"Recording stopped. Press <{play_key.name}> to play recording.")

class ActionName(Enum):
    NoAction = auto()
    LClick = auto()
    RClick = auto()
    KeyBoardKey = auto()
    SpecialKey = auto()
    ModiferKey = auto()

class SpecialKey(Enum):
    Null = auto()
    LCtrl = auto()
    LShift = auto()
    LAlt = auto()
    RCtrl = auto()
    RShift = auto()
    RAlt = auto()

class KeyState(Enum):
    Null = auto()
    Pressed = auto()
    Released = auto()

class Point:
    x = 0
    y = 0
    def get(self):
        return (self.x, self.y)

    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"

class Action:
    name: ActionName = ActionName.NoAction
    key_state: KeyState = KeyState.Null
    position: Point = Point(0, 0)
    key = None
    modifier_key: list[Key] = []
    special: Key = None

    def __repr__(self) -> str:
        if (self.name == ActionName.NoAction): return ""
        elif (self.name == ActionName.KeyBoardKey): 
            if (self.key): return f"Key <{self.key}>"
            else: return "Error"
        elif (self.name == ActionName.ModiferKey): return f"Mod <{self.key.name} {self.key_state}>"
        return f"{self.name} {self.key_state} at {self.position}"

action_list = []
mouse_pos = None

def on_move(x, y):
    global play_recording, start_recording
    if play_recording: return
    if not start_recording: return
    mouse_pos = Point(x, y)

# if returned False will stop the listener
def on_click(x, y, button, pressed):
    global play_recording, start_recording
    if play_recording: return
    if not start_recording: return
    a = Action()
    a.position = Point(x, y)
    if button == mouse.Button.left:
        a.name = ActionName.LClick
    elif button == mouse.Button.right:
        a.name = ActionName.LClick
    if pressed:
        a.key_state = KeyState.Pressed
    else:
        a.key_state = KeyState.Released
    if (a.name != ActionName.NoAction): 
        action_list.append(a)

def on_scroll(x, y, dx, dy):
    global play_recording, start_recording
    if play_recording: return
    if not start_recording: return
    print('Scrolled {0} at {1}'.format(
        'down' if dy < 0 else 'up',
        (x, y)))

def on_press(key):
    # try:
    #     print(ord(key.char), key.char)
    #     print(key.vk, chr(key.vk))
    # except:
    #     pass
    global play_recording, start_recording, stop_running
    if play_recording: return
    if (key == record_key):
        start_recording = not start_recording
        if (start_recording): 
            stop_recording_msg()
            action_list.clear()
        else:
            recording_stopped_msg()
    elif (key == stop_key):
        print(f"<{stop_key.name}> pressed. Exiting.")
        stop_running = True
        return False
    elif (key == play_key): 
        print("Playing recorded keys..", end="")
        play_recording = True
        return
    if not start_recording: return
    add_key(key, KeyState.Pressed)

def on_release(key):
    global play_recording, start_recording
    if play_recording: return
    if not start_recording: return
    add_key(key, KeyState.Released)

def add_key(key, state: KeyState):
    global stop_running, play_recording
    try:
        a = Action()
        a.name = ActionName.KeyBoardKey
        if (ord(key.char) <= 31):
            a.key = chr(key.vk + 32)
        else:
            a.key = key.char
        a.key_state = state
        action_list.append(a)
    except AttributeError:
        if ( key == Key.ctrl_l or key == Key.ctrl_r or
        key == Key.alt_l or key == Key.alt_r or
        key == Key.shift_l or key == Key.shift_r):
            a = Action()
            a.name = ActionName.ModiferKey
            a.key_state = state
            a.key = key
            action_list.append(a)
        # TODO: this is only recording the released special key
        elif (state == KeyState.Released):
            # handle Ctrl+key
            a = Action()
            a.name = ActionName.SpecialKey
            a.key_state = state
            a.special = key
            action_list.append(a)

def play_mouse_action(action: Action):
    mc = Controller()
    mc.position = action.position.get()
    if (action.name == ActionName.LClick):
        if (action.key_state == KeyState.Pressed):
            mc.press(Button.left)
        elif (action.key_state == KeyState.Released):
            mc.release(Button.left)
    if (action.name == ActionName.RClick):
        if (action.key_state == KeyState.Pressed):
            mc.press(Button.right)
        elif (action.key_state == KeyState.Released):
            mc.release(Button.right)

def play_keyboard_action(action: Action):
    kc = key_controller()
    if (action.key_state == KeyState.Pressed):
        kc.press(action.key)
    elif (action.key_state == KeyState.Released):
        kc.release(action.key)

def play_special_action(action: Action):
    kc = key_controller()
    assert action.special != None, "Unreachable Code"
    kc.press(action.special)
    kc.release(action.special)

def play_events():
    global play_recording
    for action in action_list:
        if action.name == ActionName.NoAction:
            assert False, "Unreachable Code"
        elif action.name == ActionName.KeyBoardKey:
            play_keyboard_action(action)
        elif action.name == ActionName.SpecialKey:
            play_special_action(action)
        elif action.name == ActionName.ModiferKey:
            play_keyboard_action(action)
        else:
            play_mouse_action(action)
        time.sleep(wait_time)
    play_recording = False
    print("Done.")
    start_recording_msg()

def main():
    global stop_running, play_recording
    try:
        m_listener = mouse.Listener(
                on_move=on_move,
                on_click=on_click,
                on_scroll=on_scroll)
        kb_listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release)
        m_listener.start()
        kb_listener.start()
        start_recording_msg()
        while (not stop_running):
            if (play_recording):
                play_events()
            time.sleep(1/fps)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
