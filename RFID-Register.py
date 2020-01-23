import RPi.GPIO as GPIO
import MFRC522
import signal
import MySQLdb
import time
from datetime import datetime 

#creating variables for storing student information
stdNum    = ""
firstname = ""
lastname  = ""
stdEmail  = ""
masterCard = str("N")

GPIO.setwarnings(False)

#create a Database object
myDB = MySQLdb.connect("localhost","root","Cms_Ucc928","prototype")

def CardRegister():
    continue_reading = True
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
    
    print ("Press Ctrl-C to stop.")
    print('[SYSTEM INFO :] Register Student RFID Card | One at a time')
    try:
        firstname = input("Enter Student Name: ")
        lastname  = input("Enter Student Surname: ")
        stdEmail  = input("Enter Student Email: ")
    
    except SyntaxError:
        print('Sorry, there was an unexpected input error')
        exit(1)
    
    
    print('\n')
    print("[INFOR: ] Swipe the Card Please")
    
    # This loop keeps checking for chips. If one is near it will get the UID and authenticate
    while continue_reading:
      
        # Scan for cards    
        (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        # If a card is found
        if status == MIFAREReader.MI_OK:
            print('Reading...')
            print("Card detected")
        
        # Get the UID of the card
        (status,uid) = MIFAREReader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == MIFAREReader.MI_OK:

            # Print UID
            myUDI = str(uid[0]) + str(uid[1]) + str(uid[2]) + str(uid[3])
            print ("RFID Tag Number" + " " + myUDI)
            #print ("Card read UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3]))
            
            #Creating a Database cursor for connection
            myCursor = myDB.cursor();
            
            try:
                myCursor.execute("INSERT INTO tb_rfid_register(rfid_tag,std_fname,std_lname,p_email,Master_Check) VALUES (%s,%s,%s,%s,%s)", (myUDI,firstname,lastname,stdEmail,masterCard))
                myDB.commit()
            except (myDB.Error, myDB.Warning) as e:
                print(e)
            finally:
                print("Card Registered")
                print('Thank you')
                firstname = " "
                lastname  = " "
                stdEmail = " "
                myCursor.close()
            time.sleep(1)
            exit(1)

###########################################################################################################
def Register():
    continue_reading = True
   
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
    
    print ("Press Ctrl-C to stop.")
    print('\n')
    print("[INFOR: ] Swipe the Master Card Please")
    
    # This loop keeps checking for chips. If one is near it will get the UID and authenticate
    while continue_reading:
      
        # Scan for cards    
        (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        # If a card is found
        if status == MIFAREReader.MI_OK:
            print('Reading...')
            print("Card detected")
        
        # Get the UID of the card
        (status,uid) = MIFAREReader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == MIFAREReader.MI_OK:

            # Print UID
            myUDI = str(uid[0]) + str(uid[1]) + str(uid[2]) + str(uid[3])
            print ("RFID Tag Number" + " " + myUDI)
            #print ("Card read UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3]))
            
            #Creating a Database cursor for connection
            myCursor = myDB.cursor();
            myCursor.execute("SELECT * FROM tb_rfid_register WHERE rfid_tag = %s",(myUDI,))
            for row in myCursor.fetchall():
               tag = str(row[1])
               tagname = str(row[2])
               tagsurn = str(row[3])
               check = str(row[5])
            try:
                
                if (myUDI!=tag and check!="Y"):
                    print("Sorry, this card is not a Master Card")
                    break
                else:
                    print ("The " + tagname+" "+tagsurn)
                    print("---------------------------------------------------------")
                    CardRegister()
            except UnboundLocalError:
                print("[SYSTEM INFO : ] Sorry, this card is not a Master Card")
                exit(1)

while 1:
    # Welcome message
    #Getting the Date and Time
    SysDate = datetime(1,1,1).now()
    ## Tries to search the finger and calculate hash
    print("#---------------------------------------------------------------------#")
    print("WELCOME TO RFID CARD REGISTRATION SYSTEM")
    print("System " + 'Time: {}:{:02d} - Date: {}/{}/{}'.format(SysDate.hour,SysDate.minute,SysDate.day,SysDate.month,SysDate.year))
    print('\n')
    Register()
    
    