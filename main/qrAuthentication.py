from genericpath import isfile
import pyqrcode
import png
from cryptography.fernet import Fernet
import sqlite3
import smtplib
import os
import re
from datetime import datetime
from email.message import EmailMessage
from email.utils import make_msgid
import mimetypes

class qrAuthentication:
    def __init__(self, f_name, l_name, submitter, email):
        self.f_name = f_name
        self.l_name = l_name
        self.submitter = submitter

        self.to_email = email
        self.sender_email = None
        self.app_pass = None

        self.qr = None
        self.qr_path = None

        self.key = None

        self.time_now = datetime.now().strftime("%m/%d/%Y %H:%M")

    def set_sender_email(self, email):
        email_rule = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
        if re.match(email_rule, email):
            self.sender_email = email
            return True
        return False

    def set_user_email(self, email):
        email_rule = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
        if re.match(email_rule, email):
            self.to_email = email
            return True
        return False

    def set_f_name(self, name):
        if len(name) < 50:
            self.f_name = name
        else:
            print("Bad Name, Must be less than 50 characters")

    def set_l_name(self, name):
        if len(name) < 50:
            self.l_name = name
        else:
            print("Bad Name, Must be less than 50 characters")
    
    def set_submitter(self, submitter_id):
        if len(submitter_id) < 10:
            self.submitter = submitter_id
        else:
            print("Bad ID, Must be 9 characters")
    def setAppPass(self, passw):
        if isinstance(passw, str):
            if len(passw) < 20:
                self.app = passw
    """
    Responsible for framing the email and doing smtp authentication. Adds QR code to body of email.
    """
    def emailQR(self):#3
        msg = EmailMessage()
        msg['Subject'] = 'Your Pass for Entry'
        msg['From'] = self.sender_email
        msg['To'] = self.to_email
        msg.set_content('This is a plain text body.')
        image_cid = make_msgid(domain='qrcodeauthentication.com')
        msg.add_alternative("""\
        <html>
            <body>
                <p>Hello, {self.f_name} {self.l_name}</p><br>
                <p>Show this to the guard to gain entry<br>
                </p>
                <img src="cid:{image_cid}"><br>
                <p>Only Good for 24 Hours</p>
            </body>
        </html>
        """.format(image_cid=image_cid[1:-1]), subtype='html')
        with open(self.qr_path, 'rb') as img:
            maintype, subtype = mimetypes.guess_type(img.name)[0].split('/')
            msg.get_payload()[1].add_related(img.read(), 
                                         maintype=maintype, 
                                         subtype=subtype, 
                                         cid=image_cid)
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        try:
            server.login(self.sender_email, self.app_pass)
            server.send_message(msg)
            return True
        except Exception as e:
            print("Email Failed to Send")
            print(e)
            return False

    """
    Responsible for adding a new record to the (passes) table. Creates table if it doesnt exist.
    """
    def addDatabaseEntry(self): #2
        try:
            conn = sqlite3.connect('permDB.db')
            c = conn.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS passes (
            date_entered text,
            id text,
            fname text NOT NULL,
            lname text NOT NULL,
            qr_name text,
            encryption_key text NOT NULL PRIMARY KEY
            );""")

            insert_record = (self.time_now, self.submitter, self.f_name, self.l_name, str(self.qr), self.key)
            c.execute('INSERT INTO passes VALUES (?, ?, ?, ?, ?, ?)', insert_record)
            #c.execute('''SELECT * FROM passes;''')
            return True
        except Exception as e:
            print("Database Entry Failed")
            print(e)
            return False

        finally:
            conn.commit()
            conn.close()
    """
    Responsible for deleting all the records from the database.
    Returns bool determines success of method.
    """
    def clearDatabase(self):
        try:
            conn = sqlite3.connect('permDB.db')
            c = conn.cursor()
            c.execute("DELETE FROM passes;")
            print(f"{c.rowcount} Records Deleted")
            #c.execute('''SELECT * FROM passes;''')
        except Exception as e:
            print("Database Entry Failed")
            print(e)
            return False
        finally:
            conn.commit()
            conn.close()
            return True
    """
    Takes the encrypted data string and creates a QR code. Sets file path to qr code PNG.
    Also sets the qr code obj for future use.
    """
    def createQRCode(self, data):#1
        try:
            self.qr_path = f"./codes/{data[10:15]}.png"
            qr_code = pyqrcode.create(data)
            qr_code.png(self.qr_path, scale=6)
            print(f"QR Code {self.qr}")
            self.qr = qr_code
            return True
        except Exception as e:
            print("QR Failed")
            print(e)
            return False
    """
    Responsible for creating the string of personal data and encrypting it for qr code processing.
    Also saves the encryption key for decryption in the future.
    """
    def encryptQRData(self):
        encrypt_this = bytes(f"fname={self.f_name}lname={self.l_name}submitter={self.submitter}time={self.time_now}", 'utf-8')
        self.key = Fernet.generate_key()
        cipher = Fernet(self.key)
        try:
            encoded = cipher.encrypt(encrypt_this)
            print(f"Encrypted {encoded}")
            return encoded
        except Exception as e:
            print("Encryption Failed")
            print(e)
    """ 
    Responsible for pulling the contents of the database.
    Returns list of records
    """
    def getDatabaseContents():
        conn = sqlite3.connect('permDB.db')
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS passes (
            date_entered text,
            id text,
            fname text NOT NULL,
            lname text NOT NULL,
            qr_name text,
            encryption_key text NOT NULL PRIMARY KEY
            );""")
        c.execute("SELECT * FROM passes;")
        rows = c.fetchall()
        records = []
        for row in rows:
            records.append(row)
        conn.commit()
        conn.close()
        return records
    """
    Method that puts all the pieces together.
    """
    def start(self):
        enc_data = self.encryptQRData()
        if self.createQRCode(enc_data):
            print("QR Success")
        if self.addDatabaseEntry():
            if self.emailQR():
                print("Email/Database Success")

    def show(self):
        print(f"First {self.f_name}")
        print(f"Last {self.l_name}")
        print(f"Submitter ID {self.submitter}")
        print(f"Send pass to {self.user_email}")
        print(f"Crypt Key {self.key}")
        print(f"QR Code {self.qr}")


