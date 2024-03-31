import math

from utils.grabbers.mss import Grabber
from utils.fps import FPS
import cv2
import multiprocessing
import numpy as np
from utils.nms import non_max_suppression_fast
from utils.cv2 import filter_rectangles

from utils.controls.mouse.win32 import MouseControls
from utils.win32 import WinHelper
import keyboard

import time
from utils.time import sleep

from screen_to_world import get_move_angle


def mouseposition():
    coordinates = []
    mouse = MouseControls()
    x, y = mouse.get_position()
    if keyboard.is_pressed('F9'):  # нажми сука F9 и будет тебе счастье и корды твоей хаты
        coordinates.append((x, y))
        print(f'Координаты сохранены: {x}, {y}')
        time.sleep(0.2)
        print(coordinates)


# CONFIG
GAME_WINDOW_TITLE = "Rust"  # aimlab_tb, FallGuys_client, Counter-Strike: Global Offens33
ACTIVATION_HOTKEY = "F10"
_show_cv2 = True
# used by the script
game_window_rect = WinHelper.GetWindowRect(GAME_WINDOW_TITLE, (8, 30, 16, 39))  # cut the borders

sleep_cfg = 0.01


# coordinates_inventory = [(709, 606), (800, 609), (896, 610), (994, 612), (1085, 611), (1185, 610), (698, 707), (800, 706), (891, 705), (991, 706), (1085, 706), (1182, 710), (704, 804), (797, 800), (893, 800), (994, 801), (1088, 797), (1184, 804), (703, 893), (797, 899), (890, 897), (990, 904), (1086, 899), (1184, 902), (706, 1006), (801, 1002), (897, 1004), (986, 1004), (1085, 1002), (1183, 1004)]


# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
def grab_process(q, _activated, _button_was_pressed):
    grabber = Grabber()

    while True:
        # print(_activated)
        if _activated.is_set():
            img = grabber.get_image(
                {"left": int(game_window_rect[0]), "top": int(game_window_rect[1]), "width": int(game_window_rect[2]),
                 "height": int(game_window_rect[3])})

            if img is None:
                continue

            q.put_nowait(img)
            q.join()


def cv2_process(q, activated, button_was_pressed):
    global _show_cv2
    font = cv2.FONT_HERSHEY_SIMPLEX
    fps = FPS()  # Создание объекта класса FPS
    mouse = MouseControls()
    record_activated = False
    recorded_actions = []
    degreeX = 8.34
    degreeY = degreeX/2
    fovX = 80
    fovY = fovX/2
    i = 0
    while True:
        if not q.empty() and activated.is_set() and i < 361:
            frame = q.get()
            q.task_done()

            if keyboard.is_pressed('e'):
                print(i)

            mouse.move(degree*i*10, 1430)
            sleep(0.3)
            i += 1


def switch_active_state():
    if _activated.is_set():
        # DEACTIVATE
        _activated.clear()

        print("AUTO-ACCEPT DEACTIVATED")

        if _button_was_pressed.is_set():
            _button_was_pressed.clear()

    else:
        # ACTIVATE
        _activated.set()

        print("AUTO-ACCEPT ACTIVATED")


if __name__ == "__main__":
    print("Starting AUTO-ACCEPT bot by Priler ...")
    print(f"Press {ACTIVATION_HOTKEY} to activate/deactivate the bot.")

    q = multiprocessing.JoinableQueue()
    _activated = multiprocessing.Event()
    _button_was_pressed = multiprocessing.Event()

    p1 = multiprocessing.Process(target=grab_process, args=(q, _activated, _button_was_pressed))
    p2 = multiprocessing.Process(target=cv2_process, args=(q, _activated, _button_was_pressed))

    p1.start()
    p2.start()

    while True:
        keyboard.wait(ACTIVATION_HOTKEY)
        switch_active_state()