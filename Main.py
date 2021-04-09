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
# Randomizer library to create random session ID
import random

# Gspread Initialization
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sh = client.open("Inventory System")


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
    # Get Sheets
    mahasiswa_sheet = sh.worksheet("Mahasiswa")
    mahasiswa_ids = mahasiswa_sheet.col_values(1) #Get Student IDs

    item_sheet = sh.worksheet("Items")
    item_list = item_sheet.col_values(1) #Get Item IDs
    item_status = item_sheet.col_values(3) #Get Item Statuses

    log_sheet = sh.worksheet("Logs")

    session_sheet = sh.worksheet("Session")
    session_mahasiswa_id = session_sheet.col_values(1) #get mahasiswa IDs list
    session_item_id = session_sheet.col_values(4) #get borrowed items, in concatenated string, separator ","
    session_item_name = session_sheet.col_values(5) #get borrowed items, in concatenated string, separator ","
    session_id_list = session_sheet.col_values(6) #get session id list

    os.system('clear')
    print("Welcome to Lab FTI! Please scan your KTM...")
    
    #Placeholder input
    # x = input("ID;Name")
    # id_m, name_m = x.strip().split(';')
    
    #RFID input
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
            item_indexes = set() #clear item indexes 
            sessions = []
            while True:
                id_i, name_i = '', ''
                print("Scan the item, Scan your KTM to finish scanning items.")
                
                #placeholder input
                # x = input("ItemID;ItemName")
                # id_i, name_i = x.strip().split(';')
                
                #RFID input
                id_i, name_i = reader.read()

                id_i = str(id_i).strip() #remove leading and trailing  
                name_i = str(name_i).strip()
                
                if id_i in item_list and item_status[item_list.index(id_i)] == "Available": #check if item exists in DB and available            
                    # Get item indexes
                    item_indexes.add(item_list.index(id_i))

                    if id_i in item_ids: #if item is duplicate 
                        #print(f"Item: {name_i} has already been added") # comment this line to not clutter console?
                        continue
                    
                    else: #new item in borrow session
                        item_ids.add(id_i) #add to set
                        curr_time = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M")
                        newRow = [id_i, name_i, id_m, name_m, curr_time]
                        items.append(newRow)
                        print(f"Item: {name_i} added")            
                        flash_led()

                elif id_i == str(id_m): #if item scanned is borrower's KTM 
                    print("Ending scanning process...")
                    log_sheet.append_rows(items)
                    #curr_time = str(datetime.datetime.now())
                    
                    print("Please Wait...\n")

                    # Update Item Status
                    for i in item_indexes:
                        item_sheet.update_cell(i+1, 3, 'Unavailable')
                        item_sheet.update_cell(i+1, 4, str(name_m))
                    
                    # Get Item IDs
                    borrowed_ids = set(map(lambda x:x[0], items)) #Get all item_id that is borrowed in this session. Format [id_i, name_i, id_m, name_m, time]
                    borrowed_ids_string = ','.join(borrowed_ids)

                    # Get Item Names
                    borrowed_names = set(map(lambda x:x[1], items))
                    borrowed_names_string = ','.join(borrowed_names)

                    # Randomize Session ID?
                    random_id = random.randint(1000,9999)
                    while (random_id in session_id_list) :
                        random_id = random.randint(1000,9999)

                    newRow = [id_m, name_m, curr_time, borrowed_ids_string, borrowed_names_string, random_id]
                    sessions.append(newRow)

                    session_sheet.append_rows(sessions)

                    print("Success!!!\n")

                    sleep(5)
                    break

                else: 
                    print("RFID Tag not recognized!")

            

        # RETURN ITEMS
        elif choice == 2:
            #get index of user's session
            index = []
            for i, x in enumerate(session_mahasiswa_id):
                if x == str(id_m):
                    index.append(i)
            if len(index) != 0 :
                while True:
                    for i in range(len(index)):
                        print(f"[{i+1}]. Session #{session_id_list[index[i]]} \nItems\n{session_item_name[index[i]]}")
                        print("==========================================================")
                    print("Which session do you want to conclude?")
                    choice = int(input("Choice:"))
                    if choice-1 in range(len(index)):
                        # Update Item Status
                        items = session_item_id[index[choice-1]].split(',')
                        item_indexes = set()
                        for i in items: 
                            item_indexes.add(item_list.index(i))

                        for i in item_indexes:
                            item_sheet.update_cell(i+1, 3, "Available")
                            item_sheet.update_cell(i+1, 4, "")

                        # Delete Session 
                        session_sheet.delete_rows(index[choice-1]+1) # +1 for adjusting row header
                        
                        print("Session concluded successfully!")
                        break
                    elif choice == 0:
                        print("Exiting session")
                        break
                    else: 
                        print("Invalid session number")
                        
            else:
                print("Session not available, returning")
            

    else:
        print("Not a College Student ID!\n")
        sleep(1)

