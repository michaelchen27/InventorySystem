# SDA   connects to Pin 24.
# SCK   connects to Pin 23.
# MOSI  connects to Pin 19.
# MISO  connects to Pin 21.
# GND   connects to Pin 6.
# RST   connects to Pin 22.
# 3.3v  connects to Pin 1.

# LED_VCC       connects to Pin 12.
# LED_Ground    connects to Pin 14.

# Gspread Libraries
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
import datetime
import os

# RFID Libraries
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

# Time library to create delay (Insert time delay between RFID Read)
from time import sleep


# Gspread Initialization
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)

mahasiswa_sheet = client.open("Inventory System").worksheet("Mahasiswa")
mahasiswa_ids = mahasiswa_sheet.col_values(1)

item_sheet = client.open("Inventory System").worksheet("Items")
item_list = item_sheet.col_values(1) #Get Item IDs

log_sheet = client.open("Inventory System").worksheet("Logs")

# RFID Setup
reader = SimpleMFRC522()


# LED GPIO Setup
GPIO.setup(12, GPIO.OUT)


def flash_led():
    GPIO.output(12, GPIO.HIGH)
    sleep(0.5)
    GPIO.output(12, GPIO.LOW)



# Main program Loop
while True:
    #try:
        os.system('clear')
        print("Welcome to Lab FTI! Please scan your KTM...")
        id_m, name_m = reader.read()

        if str(id_m) in mahasiswa_ids:
            print(f"\nWelcome, {name_m}!")
            print("What would you like to do? \n1. BORROW Lab Equipment \n2. RETURN Lab Equipment\n")
            flash_led()
            choice = int(input("Choice:"))
            
            # BORROW ITEMS
            if choice == 1:
                items = [] #clear item list
                item_ids = set() #clear item sets to check for uniques
                item_indexes = set()
                while True:
                    id_i, name_i = '', ''
                    print("Scan the item, Scan your KTM to finish scanning items.")
                    id_i, name_i = reader.read()

                    id_i = str(id_i)
                    
                    if id_i in item_list: #check if item exists in DB                    
                        
                        # Get item indexes
                        print(item_list.index(id_i))
                        item_indexes.add(item_list.index(id_i))

                        if id_i in item_ids: #if item is duplicate 
                            #print(f"Item: {name_i} has already been added") # comment this line to not clutter console?
                            continue
                        
                        else: #new item in borrow session
                            item_ids.add(id_i) #add to set
                            curr_time = str(datetime.datetime.now())
                            newRow = [id_i, name_i, id_m, name_m, curr_time]
                            items.append(newRow)
                            print(f"Item: {name_i} added")            
                            flash_led()

                    elif id_i == str(id_m):
                        print("Ending scanning process...")
                        log_sheet.append_rows(items)
                        #curr_time = datetime.now()
                        print("Success!!!\n")
                        print(f"Item indexes:\n {item_indexes}\nPlease Wait...")

                        # Update Item Status

                        for i in item_indexes:
                            item_sheet.update_cell(i, 3, 'Unavailable')

                        sleep(2)


                        break

                    else: 
                        print("RFID Tag not recognized!")

                

            # RETURN ITEMS
            elif choice == 2:
                print('haii')


        else:
            print("Not a College Student ID!\n")

    #finally:
     #   GPIO.cleanup()
      #  sleep(0.5) #sleep for 0.5 second, prevent fast consecutive readings

