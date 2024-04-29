import time
import os
import tkinter
from PIL import Image, ImageTk
import keyboard
import pydirectinput
import pyautogui
import pytesseract
from PIL import Image
import gtts
import json
import playsound

# Setup
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
mainWindow = tkinter.Tk()

# konstante Farben
HSV_DARK_BLUE = (0, 90, 170)
TICKET_BLUE = (126, 184, 205)
NO_TICKET_RED = (255, 173, 173)
WHITE = (255, 255, 255)

# variable Koordinaten
NEULADEN = (116, 81)
JETZT_PLAETZE_AUSWAEHLEN = (600, 1000)
PLATZVORSCHLAG_ERHALTEN = (1300, 900)
NO_TICKET_FOUND = (1430, 340)
NO_TICKET_FOUND_LOADING = (1887, 401)
WARENKORB = (1750, 950)
A23 = (555, 554)
A24 = (579, 552)
A25 = (603, 551)
A26 = (628, 552)
A27 = (648, 553)
PRICE_SLIDER = [(920, 293), (470, 293)]
NO_TICKET_IN_WINDOW = (995, 472)
CONNECTION_GONE = (995, 455)

downscroll = [(1908, 190), (1908, 426)]
CLICK_AFTER_DOWNSCROLL = (1550, 808)

# Ticketauswahl!
tickets = [A23, A24, A25, A26, A27]

def readVariables():
    with open('/settings.json') as f:
        data = json.load(f)
        NEULADEN = data['NEULADEN']
        JETZT_PLAETZE_AUSWAEHLEN = data['JETZT_PLAETZE_AUSWAEHLEN']
        PLATZVORSCHLAG_ERHALTEN = data['PLATZVORSCHLAG_ERHALTEN']
        NO_TICKET_FOUND = data['NO_TICKET_FOUND']
        NO_TICKET_FOUND_LOADING = data['NO_TICKET_FOUND_LOADING']
        WARENKORB = data['WARENKORB']
        A23 = data['A23']
        A24 = data['A24']
        A25 = data['A25']
        A26 = data['A26']
        A27 = data['A27']
        PRICE_SLIDER = data['PRICE_SLIDER']
        NO_TICKET_IN_WINDOW = data['NO_TICKET_IN_WINDOW']
        CONNECTION_GONE = data['CONNECTION_GONE']
        downscroll = data['downscroll']
        CLICK_AFTER_DOWNSCROLL = data['CLICK_AFTER_DOWNSCROLL']
        tickets = data['tickets']

def readText():
    imageToRead = pyautogui.screenshot()
    # crop image
    imageToRead = imageToRead.crop((559, 570, 1368, 642))
    imageToRead.save('resources/img/screenshot.png')
    return pytesseract.image_to_string(Image.open('resources/img/screenshot.png'))

def inactivityCheck():
    pyautogui.click(PLATZVORSCHLAG_ERHALTEN)
    
    while not (testForColor(NO_TICKET_RED, NO_TICKET_IN_WINDOW) or (testForColor(NO_TICKET_RED, CONNECTION_GONE))):
        time.sleep(0.01)

    message = readText()
    if "Bestplatzsuche" in message:
        pyautogui.click(PLATZVORSCHLAG_ERHALTEN)
    else:
        reload()

def priceSlider():
    pyautogui.moveTo(PRICE_SLIDER[0][0], PRICE_SLIDER[0][1])
    pyautogui.dragTo(PRICE_SLIDER[1][0], PRICE_SLIDER[1][1], 0.35, button='left')
    time.sleep(0.35)

def testForColor(color2, position):
    color1 = pyautogui.pixel(position[0], position[1])
    return abs(color1[0] - color2[0]) < 8 and abs(color1[1] - color2[1]) < 8 and abs(color1[2] < color2[2]) < 8

def handleNoTicket():
    while not testForColor(WHITE, NO_TICKET_FOUND_LOADING) and not cancel:
        if (testForColor(HSV_DARK_BLUE, JETZT_PLAETZE_AUSWAEHLEN)):
            return
        time.sleep(0.01)
    offset = testForColor(NO_TICKET_RED, NO_TICKET_FOUND)

    pyautogui.moveTo(downscroll[0][0], downscroll[0][1])
    pyautogui.dragTo(downscroll[1][0], downscroll[1][1], 0.3, button='left')
    time.sleep(0.31)

    pyautogui.click((CLICK_AFTER_DOWNSCROLL[0], CLICK_AFTER_DOWNSCROLL[1] + offset * 80))

def reload():
    mainWindow.wm_state('iconic')
    pyautogui.click(NEULADEN)
    time.sleep(0.01)

    cancel = False
    while not testForColor(HSV_DARK_BLUE, JETZT_PLAETZE_AUSWAEHLEN):
        if (keyboard.is_pressed('esc')):
            mainWindow.wm_state('normal')
            mainWindow.attributes('-topmost', 1)
            cancel = True
            return
        handleNoTicket()
        time.sleep(1)

    while testForColor(HSV_DARK_BLUE, NEULADEN):
        time.sleep(0.01)
    time.sleep(0.05)

    pyautogui.click(JETZT_PLAETZE_AUSWAEHLEN)
    time.sleep(0.05)

    snipeFor(tickets)

def snipeFor(tickets):
    while not testForColor(HSV_DARK_BLUE, PLATZVORSCHLAG_ERHALTEN):
        time.sleep(0.01)
    priceSlider()

    cancel = False
    count = 0
    while not cancel:
        count += 1
        if count % 500 == 0:
            inactivityCheck()
        for ticket in tickets:
            pyautogui.moveTo(ticket)
            if testForColor(TICKET_BLUE, ticket):
                pyautogui.click(ticket)
                cancel = True
                clickTicket(ticket)
                break
        if keyboard.is_pressed('esc'):
            mainWindow.wm_state('normal')
            mainWindow.attributes('-topmost', 1)
            cancel = True
            break
        
def clickTicket(ticket):
    while not testForColor(HSV_DARK_BLUE, WARENKORB):
        time.sleep(0.005)
    pyautogui.click(WARENKORB)
    playsound.playsound("./resources/sound/confirmation.mp3")

def setup():
    mainWindow.title("HSV-Ticketsniper v.2.0")
    mainWindow.geometry("450x370")
    mainWindow.attributes('-topmost', 1)
    mainWindow.iconbitmap("./resources/img/icon.ico")
    mainWindow.resizable(False, False)
    readVariables()
    pyautogui.PAUSE = 0.001

    # Einrichten der Bilder
    backgroundImg = ImageTk.PhotoImage(Image.open("./resources/img/hsv.jpg"))
    startImg = ImageTk.PhotoImage(Image.open("./resources/img/startButton.png"))

    # Einrichten der Buttons
    hsvLogo = tkinter.Label(image=backgroundImg).place(x=225, y=50, anchor="center")
    startButton = tkinter.Button(mainWindow, image=startImg, command=reload).place(x=225, y=225, anchor="center", width=225, height=63)
    mainWindow.mainloop()
setup()