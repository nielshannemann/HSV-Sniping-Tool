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

# Konstante Farben
color_blue = (0, 90, 170)
color_lightblue = (79, 140, 194)
color_blue_alt  = (34, 105, 168)
color_red = (255, 173, 173)

# Einrichten der Hauptroutine
def start():
    global position_platzvorschlag, position_neuladen, position_ticketansicht, position_regler_r, position_regler_l, position_warenkorb, position_serverError, position_keinTicket

    if os.path.exists("./settings.json"):
        # Lesen der Einstellungen aus der settings.json
        with open('./settings.json', 'r') as openfile:
            json_object = json.load(openfile)

        # Einstellungen auslesen
        if 'position_platzvorschlag' in json_object:
            position_platzvorschlag = (json_object['position_platzvorschlag'][0], json_object['position_platzvorschlag'][1])
            position_neuladen = (json_object['position_neuladen'][0], json_object['position_neuladen'][1])
            position_ticketansicht = (json_object['position_ticketansicht'][0], json_object['position_ticketansicht'][1])
            position_regler_r = (json_object['position_regler_r'][0], json_object['position_regler_r'][1])
            position_regler_l = (json_object['position_regler_l'][0], json_object['position_regler_l'][1])
            position_warenkorb = (json_object['position_warenkorb'][0], json_object['position_warenkorb'][1])
            position_keinTicket = (json_object['position_keinTicket'][0], json_object['position_keinTicket'][1])
            # Falls ServerError spezifiziert wurde, wird dieser verwendet
            if 'position_serverError' in json_object:
                position_serverError = json_object['position_serverError']
            else:
                position_serverError = (1080, 628)
    else:
        # Default-Einstellungen
        position_platzvorschlag = (1300, 860)
        position_neuladen = (100, 60)
        position_ticketansicht = (593, 959)
        position_regler_r = (933, 216)
        position_regler_l = (480, 218)
        position_warenkorb = (1750, 950)
        position_keinTicket = (950, 500)
        position_serverError = (1080, 628)

    # Start der Hauptroutine
    mainWindow.wm_state('iconic')
    neuladen()
    click()

# komponentenweiser Vergleich zweier Farben mit einer Toleranz von d
def compareColors(color1, color2, d=5):
    return abs(color1[0] - color2[0]) < d and abs(color1[1] - color2[1]) < d and abs(color1[2] < color2[2]) < d

# Neuladen und zur Ticketansicht wechseln
def neuladen():
    global position_platzvorschlag, position_neuladen, position_ticketansicht

    # Seite neuladen
    pydirectinput.click(position_neuladen[0], position_neuladen[1]) # Neuladen-Symbol (91, 48)

    progress = False
    while not progress:
        # Prüfen, ob der Vorgang abgebrochen werden soll
        if keyboard.is_pressed('escape'):
            windowUpFront()
            return

        image = pyautogui.screenshot()
        # Suche nach dem Ticketansicht-Button
        if (compareColors(image.getpixel(position_ticketansicht), color_blue) or compareColors(image.getpixel(position_ticketansicht), color_blue_alt)): # weiter zur Ticketansicht (574, 793)
            progress = True

        if (compareColors(image.getpixel((1490, 320)), (255, 173, 173))):
            pydirectinput.moveTo(1908, 174)
            pydirectinput.mouseDown(button='left')
            pydirectinput.moveTo(1911, 410, 0.2)
            pydirectinput.mouseUp(button='left')
            time.sleep(0.2)
            pydirectinput.click(1230, 650)
    # weiter zur Ticketansicht
    pydirectinput.click(position_ticketansicht[0], position_ticketansicht[1]) # weiter zur Ticket-Ansicht (574, 793)

    progress = False
    while not progress:
        # Prüfen, ob der Vorgang abgebrochen werden soll
        if keyboard.is_pressed('escape'):
            windowUpFront()
            return

        # Suche nach dem Platzvorschlag-Button
        image = pyautogui.screenshot()
        if (compareColors(image.getpixel(position_platzvorschlag), color_blue)): # Platzvorschlag erhalten (1800, 680)
            progress = True
    # Platzvorschlag auf Nordtribüne beschränken
    dragToNord()

# Regler auf Nordtribüne ziehen
def dragToNord():
    global position_regler_r, position_regler_l

    pydirectinput.moveTo(position_regler_r[0], position_regler_r[1]) # rechte Seite des Reglers (933, 216)
    pydirectinput.mouseDown(button='left')
    pydirectinput.moveTo(position_regler_l[0] - 15, position_regler_l[1], 0.4) # linke Seite des Reglers (610, 218)
    time.sleep(0.4)
    pydirectinput.mouseUp(button='left')

# Klicken und Warten, bis ein Platzvorschlag erhalten wurde
def click():
    global position_platzvorschlag, position_warenkorb, position_serverError, position_keinTicket
    
    # Initialisierung von Variablen
    cancel = False
    success = False

    # Main-Loop
    while not success:
        # Prüfen, ob der Vorgang abgebrochen werden soll
        if keyboard.is_pressed('escape'):
            windowUpFront()
            return
        pydirectinput.click(position_platzvorschlag[0], position_platzvorschlag[1]) # Platzvorschlag erhalten (1800, 680)

        progress = False
        count = 0
        while not progress:
            # Prüfen, ob der Vorgang abgebrochen werden soll
            if keyboard.is_pressed('escape'):
                windowUpFront()
                return
            
            # Analyse des Screenshots
            image = pyautogui.screenshot()
            count += 1
            if (count % 10 == 0):
                count = 0
                text = readText()
                # if text includes "Server Error"
                serverError = "Internetverbindung" in text
            else:
                serverError = False
                
            # Verbindung zum Server fehlgeschlagen, neuladen
            if(serverError): # besonderer Pixel (1052, 609)
                progress = True
                neuladen()
            # Keine Plätze verfügbar, erneut versuchen
            elif (compareColors(image.getpixel((position_keinTicket[0], position_keinTicket[1])), color_red)): # OK-Knopf (950, 500)
                progress = True
            # Ticket gefunden
            elif (compareColors(image.getpixel((position_warenkorb[0], position_warenkorb[1])), color_blue)): # Warenkorb-Knopf (1815, 975)
                progress = True
                success = True
            # Seite lädt, Cursor vom Button bewegen, um den Vorgang zu beschleunigen
            elif (compareColors(image.getpixel((position_platzvorschlag[0], position_platzvorschlag[1])), color_lightblue)): # Platzvorschlag erhalten (1800, 680)
                progess = True
                pydirectinput.moveTo(1100, 695) # etwas zur Seite (1100, 695)

        # Ticket gefunden, Klick auf Warenkorb
        if success and not cancel:
            pydirectinput.click(position_warenkorb[0], position_warenkorb[1]) # Warenkorb-Knopf (1815, 975)
            playsound.playsound('resources/audio/success.wav')
        # Ticket nicht gefunden, erneut versuchen
        elif not success:
            pydirectinput.click(position_platzvorschlag[0], position_platzvorschlag[1])
    windowUpFront()

def setupServerError():
    playsound.playsound("./resources/audio/setup10.wav")
    mainWindow.wm_state('iconic')

    progress = False
    while not progress:
        # Prüfen, ob der Vorgang abgebrochen werden soll
        if keyboard.is_pressed('escape'):
            windowUpFront()
            return
        elif keyboard.is_pressed('H'):
            # Analyse des Screenshots
            image = pyautogui.screenshot()
            position_serverError = (pydirectinput.position()[0], pydirectinput.position()[1])
                
            # Testen, ob der Pixelwert stimmt
            if (image.getpixel((position_serverError[0], position_serverError[1]))) == ((49, 49, 49)): # besonderer Pixel (1052, 609)
                progress = True
                playsound.playsound("./resources/audio/success.wav")

    # Lesen der Einstellungen aus der settings.json
    with open('./settings.json', 'r') as openfile:
        json_object = json.load(openfile)
        json_object.update({"serverError": position_serverError})
        with open('./settings.json', 'w') as openfile:
            json.dump(json_object, openfile)

    playsound.playsound('./resources/audio/setup11.wav')
    windowUpFront()

# Hauptfenster in den Vordergrund bringen
def windowUpFront():
    mainWindow.wm_state('normal')
    mainWindow.attributes('-topmost', 1)

def readText():
    imageToRead = pyautogui.screenshot()
    # crop image
    imageToRead = imageToRead.crop((559, 570, 1368, 642))
    imageToRead.save('resources/img/screenshot.png')
    return pytesseract.image_to_string(Image.open('resources/img/screenshot.png'))

# Setup der Parameter
def setup():
    playsound.playsound("./resources/audio/setup0.wav")

    # Schritt 1: Anfrage bestätigen
    progress = False
    while not progress:
        # Prüfen, ob der Vorgang abgebrochen werden soll
        if keyboard.is_pressed('escape'):
            return
        elif keyboard.is_pressed('H'):
            progress = True

    mainWindow.wm_state('iconic')
    playsound.playsound("./resources/audio/setup1.wav")

    # Zwischenspeichern der Positionen
    position_platzvorschlag = (1300, 860)
    position_neuladen = (100, 60)
    position_ticketansicht = (593, 959)
    position_regler_r = (933, 216)
    position_regler_l = (500, 218)
    position_warenkorb = (1750, 950)
    position_keinTicket = (950, 500)

    # Schritt 2: Browser öffnen
    progress = False
    while not progress:
        # Prüfen, ob der Vorgang abgebrochen werden soll
        if keyboard.is_pressed('escape'):
            return
        elif keyboard.is_pressed('S'):
            progress = True
    
    # Schritt 3: Neuladen-Knopf finden
    playsound.playsound("./resources/audio/setup2.wav")
    progress = False
    while not progress:
        # Prüfen, ob der Vorgang abgebrochen werden soll
        if keyboard.is_pressed('escape'):
            return
        elif keyboard.is_pressed('V'):
            position_neuladen = (pydirectinput.position()[0], pydirectinput.position()[1])
            progress = True
    
    # Schritt 4: Ticketansicht finden
    playsound.playsound("./resources/audio/setup3.wav")
    progress = False
    while not progress:
        # Prüfen, ob der Vorgang abgebrochen werden soll
        if keyboard.is_pressed('escape'):
            return
        elif keyboard.is_pressed('H'):
            position_ticketansicht = (pydirectinput.position()[0], pydirectinput.position()[1])
            progress = True
    pydirectinput.click(position_ticketansicht[0], position_ticketansicht[1])
    
    # Schritt 5: Regler finden
    playsound.playsound("./resources/audio/setup4.wav")
    progress = False
    while not progress:
        # Prüfen, ob der Vorgang abgebrochen werden soll
        if keyboard.is_pressed('escape'):
            return
        elif keyboard.is_pressed('S'):
            position_regler_r = (pydirectinput.position()[0], pydirectinput.position()[1])
            progress = True
    
    # Schritt 6: Regler-Ende finden
    playsound.playsound("./resources/audio/setup5.wav")
    progress = False
    while not progress:
        # Prüfen, ob der Vorgang abgebrochen werden soll
        if keyboard.is_pressed('escape'):
            return
        elif keyboard.is_pressed('V'):
            position_regler_l = (pydirectinput.position()[0], pydirectinput.position()[1])
            progress = True

    # Schritt 7: Platzvorschlag finden
    playsound.playsound("./resources/audio/setup6.wav")
    progress = False
    while not progress:
        # Prüfen, ob der Vorgang abgebrochen werden soll
        if keyboard.is_pressed('escape'):
            return
        elif keyboard.is_pressed('H'):
            position_platzvorschlag = (pydirectinput.position()[0], pydirectinput.position()[1])
            progress = True

    pydirectinput.click(position_platzvorschlag[0], position_platzvorschlag[1])
    
    # Schritt 8: Kein-Ticket deketieren
    playsound.playsound("./resources/audio/setup7.wav")
    progress = False
    while not progress:
        # Prüfen, ob der Vorgang abgebrochen werden soll
        if keyboard.is_pressed('escape'):
            return
        elif keyboard.is_pressed('S'):
            position_keinTicket = (pydirectinput.position()[0], pydirectinput.position()[1])
            progress = True

    # Ticket auswählen
    pydirectinput.click(position_neuladen[0], position_neuladen[1])
    time.sleep(1.5)
    pydirectinput.click(position_ticketansicht[0], position_ticketansicht[1])
    time.sleep(1.5)
    pydirectinput.click(position_platzvorschlag[0], position_platzvorschlag[1])
    
    # Schritt 9: Warenkorb finden
    playsound.playsound("./resources/audio/setup8.wav")
    progress = False
    while not progress:
        # Prüfen, ob der Vorgang abgebrochen werden soll
        if keyboard.is_pressed('escape'):
            return
        elif keyboard.is_pressed('V'):
            position_warenkorb = (pydirectinput.position()[0], pydirectinput.position()[1])
            progress = True

    playsound.playsound("./resources/audio/setup9.wav")
    
    # Speichern der Positionen
    values = {
        "position_neuladen": position_neuladen,
        "position_ticketansicht": position_ticketansicht,
        "position_regler_r": position_regler_r,
        "position_regler_l": position_regler_l,
        "position_platzvorschlag": position_platzvorschlag,
        "position_warenkorb": position_warenkorb,
        "position_keinTicket": position_keinTicket
    }

    if not (os.path.exists("./settings.json")):
        setupServerErrorButton = tkinter.Button(mainWindow, image=setup2Img, command=setupServerError).place(x=225, y=310, anchor="center", width=225, height=63)

    # Speichern der Positionen in die Datei
    with open('./settings.json', 'w') as f:
        json.dump(values, f)

    windowUpFront()

# Fenster zum Starten des Programms
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

mainWindow = tkinter.Tk()
mainWindow.title("HSV-Ticketsniper v.1.0")
mainWindow.geometry("450x370")
mainWindow.attributes('-topmost', 1)
mainWindow.iconbitmap("./resources/img/icon.ico")
mainWindow.resizable(False, False)

# Einrichten der Bilder
backgroundImg = ImageTk.PhotoImage(Image.open("./resources/img/hsv.jpg"))
startImg = ImageTk.PhotoImage(Image.open("./resources/img/startButton.png"))
setupImg = ImageTk.PhotoImage(Image.open("./resources/img/settingsButton.png"))
setup2Img = ImageTk.PhotoImage(Image.open("./resources/img/settings2Button.png"))

# Einrichten der Buttons
hsvLogo = tkinter.Label(image=backgroundImg).place(x=225, y=50, anchor="center")
startButton = tkinter.Button(mainWindow, image=startImg, command=start).place(x=225, y=160, anchor="center", width=225, height=63)
setupButton = tkinter.Button(mainWindow, image=setupImg, command=setup).place(x=225, y=235, anchor="center", width=225, height=63)
if os.path.exists("./settings.json"):
    setupServerErrorButton = tkinter.Button(mainWindow, image=setup2Img, command=setupServerError).place(x=225, y=310, anchor="center", width=225, height=63)
mainWindow.mainloop()