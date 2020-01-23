import os
import RPi.GPIO as GPIO
import MFRC522
import signal
import MySQLdb
from time import strftime,gmtime
import time
import smtplib
from datetime import datetime


GPIO.setwarnings(False)

SysDate = datetime(1,1,1).now()
print("#---------------------------------------------------------------------#")
print("WELCOME TO RFID ATTENDANCE SYSTEM")
print("System " + 'Time: {}:{:02d} - Date: {}/{}/{}'.format(SysDate.hour,SysDate.minute,SysDate.day,SysDate.month,SysDate.year))
print('\n')
print('[1] Plesea choose A = <Tag In>, or B =<Tag Out>')
print('[2] Select the Subject Code For Attendance')
print('\n')

#----------------------------------------------------------------#
#Creating Variables from The Email Settings
smtpUser ='cs928799210@gmail.com'
smtpPass='Cms_Ucc928'
toAdd =""
fromAdd=smtpUser


continue_reading = True

#creating variables for storing the names
firstname = ""
lastname  = ""
stdNum    = ""

#-----------------Function for Sigh In : Take Attendance Option A--------------#
def SignInFunction(subjectCode):
    print('Your attendance will be taken in few seconds.')
    print('Please swipe your card')
    print('---------------------------------------------')
    db = DataBaseConnect()
    
    count=0
    # Capture SIGINT for cleanup when the script is aborted
    def end_read(signal,frame):
        global continue_reading
        print ("Ctrl+C captured, ending read.")
        continue_reading = False
        GPIO.cleanup()

    # Hook the SIGINT
    signal.signal(signal.SIGINT, end_read)
    # Create an object of the class MFRC522
    MIFAREReader = MFRC522.MFRC522()

    # This loop keeps checking for chips. If one is near it will get the UID and authenticate
    while continue_reading:
        
        # Scan for cards    
        (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        # If a card is found
        if status == MIFAREReader.MI_OK:
            print ("Card detected")
        # Get the UID of the card
        (status,uid) = MIFAREReader.MFRC522_Anticoll()
        # If we have the UID, continue
        if status == MIFAREReader.MI_OK:

            # Print UID
            myUDI = str(uid[0]) + str(uid[1]) + str(uid[2]) + str(uid[3])
            print ("Card Number: " + " " + myUDI)
            #print ("Card read UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3]))
            
            #Creating a Database cursor for connection
            myCursor = db.cursor()
            myCursor.execute("SELECT * FROM tb_rfid_register WHERE rfid_tag = %s",(myUDI,))

            for row in myCursor.fetchall():
                    firstname = str(row[2])
                    lastname  = str(row[3])
                    toAdd     = str(row[4])
            #get the current time
            cTime = strftime("%H:%M:%S",gmtime())
                
            print("Hello " + firstname +" " +lastname + " " + "Email : " + toAdd)
            
            subject ='School Notification'
            header = 'To: ' + toAdd + '\n' + 'From:' + fromAdd + '\n' + 'Subject:' + subject
            body = 'Your son ' + firstname + '\n' + lastname + '\n' + 'has attended at school at:' +'\n' +cTime 
            s=smtplib.SMTP('smtp.gmail.com',587)
            s.ehlo()
            s.starttls()
            s.ehlo()

            s.login(smtpUser,smtpPass)
            s.sendmail(fromAdd,toAdd,header+'\n\n'+body)
            s.quit()
            print('Email Sent to your parents:' + toAdd)
            try:
                try:
                    myCursor.execute("SELECT * FROM tb_rfid_register WHERE rfid_tag =%s", (myUDI,))
                    for row in myCursor.fetchall():
                        comTag= str(row[1])
                        stdNum    = str(row[0])
                    if (comTag!=myUDI):
                        print("Sorry, Card Not Register")
                        print('\n')
                        break
                    else:
                        myCursor.execute("INSERT INTO logs_rfid(rfid_tag,std_id,att_hour,att_check,sub_code) VALUES (%s,%s,%s,%s,%s)", (myUDI,stdNum,cTime,"Present",subjectCode))
                        db.commit()
                        print("Attendance Recorded")
                        print("--------------------------------------------")
                except (db.Error, db.Warning) as e:
                    print(e)
            finally:
                
                firstname = " "
                lastname  = " "
                toAdd     = " "
                stdNum    = " "
                myCursor.close()
        time.sleep(1)
#------------------------------------------------------------------------------#
#Creating Function for Option B to Sign Out after class#
def SignOutFunction(subCode):
    continue_reading = True
    def end_read(signal,frame):
        global continue_reading
        print ("Ctrl+C captured, ending read.")
        continue_reading = False
        GPIO.cleanup()

    # Hook the SIGINT
    signal.signal(signal.SIGINT, end_read)

    # Create an object of the class MFRC522
    MIFAREReader = MFRC522.MFRC522()

    # This loop keeps checking for chips. If one is near it will get the UID and authenticate
    while continue_reading:
        
        # Scan for cards    
        (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        # If a card is found
        if status == MIFAREReader.MI_OK:
            print ("Card detected")
        
        # Get the UID of the card
        (status,uid) = MIFAREReader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == MIFAREReader.MI_OK:
            # Print UID
            myUDI = str(uid[0]) + str(uid[1]) + str(uid[2]) + str(uid[3])
            print ("Card Number: " + " " + myUDI)
            
            cTime = strftime("%H:%M:%S",gmtime())
            cDate = strftime("%x",gmdate())
            db = DataBaseConnect()
            myCursor = db.cursor()
            try:
                myCursor.execute("SELECT * FROM tb_rfid_register WHERE rfid_tag =%s", (myUDI,))
                for row in myCursor.fetchall():
                    comTag= str(row[1])
                if (comTag!=myUDI):
                    print("Sorry, Card Not Register")
                    print('\n')
                    exit(1)
                else:
                    try:
                        myCursor.execute("INSERT INTO rfid_check_out(rfid_tag,time_in,date_in,status,sub_code) VALUES (%s,%s,%s,%s,%s)", (myUDI,cTime,cDate,"Out",subCode))
                        db.commit()
                    except (db.Error, db.Warning) as e:
                        print(e)
            finally:
                print("Data logged, Bey")
                myCursor.close()
            
        time.sleep(1)

def DataBaseConnect():
    myDB = MySQLdb.connect('localhost','root','Cms_Ucc928','prototype')
    return myDB

while True:
    print('##########################################')
    try:
        select = input('Select A or B >>')
    except SyntaxError:
        print("[SYSTEM INFO: ] sorry there was an input error")
        exit(1)
    except NameError:
        print("[SYSTEM INFO: ] sorry there was an input error")
        exit(1)
    if (select=="A"):
        subjectCode = input('Please enter the subject code:')
        try:
            db = DataBaseConnect()
            myCursor = db.cursor()
            myCursor.execute("SELECT * FROM tb_subjects WHERE sub_code =%s", (subjectCode,))
            for row in myCursor.fetchall():
                subCode = str(row[0])
                subName = str(row[1])
                sTeacher = str(row[2])
            print("Welcome : " + sTeacher)
            print("Subject : " + subName)
            print("#--------------------------------------------#")
            SignInFunction(subCode)
            subjectCode = ""
            subCode = ""
            subName = ""
            sTeacher = ""
            
        except:
            print("[SYSTEM INFO : ] sorry no such subject registered")
            exit(1)
    elif(select=="B"):
        try:
            SignOutFunction(subCode)
        except NameError:
            print("[SYSTEM INFO : ] sorry this operation can not be perfomed before attendance")
            exit(1)
    else:
        print('Sorry no such option is availabe')
     
        


