# SDA connects to Pin 24.
# SCK connects to Pin 23.
# MOSI connects to Pin 19.
# MISO connects to Pin 21.
# GND connects to Pin 6.
# RST connects to Pin 22.
# 3.3v connects to Pin 1.

# Gspread Libraries
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
import datetime

# RFID Libraries
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

# Time library to create delay (Insert time delay between RFID Reads)
from time import sleep


# Gspread Initialization
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Inventory System").sheet1

# RFID Setup
reader = SimpleMFRC522()

mahasiswa_sheet = client.open("Inventory System").worksheet("Mahasiswa")
mahasiswa_ids = mahasiswa_sheet.col_values(1)

item_sheet = client.open("Inventory System").worksheet("Items")
item_list = item_sheet.col_values(1)
print(item_list)

log_sheet = client.open("Inventory System").worksheet("Logs")

i = 5
items = []
item_ids = []
# Main program Loop
while True:
    #try:
        print("Welcome to Lab FTI! Please scan your KTM...")
        id_m, name_m = reader.read()

        if str(id_m) in mahasiswa_ids:
            print(f"\nWelcome, {name_m}! ")
            print("What would you like to do? \n1. BORROW Lab Equipment \n2. RETURN Lab Equipment\n")
            choice = int(input("Choice:"))

            if choice == 1:
                while True:

                    id_i, name_i = '', ''
                    print("Scan the item, Scan your KTM to end scanning.")
                    id_i, name_i = reader.read()

                    if str(id_i) in item_list: 
                        print(f"Item: {name_i}")
                        curr_time = str(datetime.datetime.now())

                        newRow = [id_i, name_i, id_m, name_m, curr_time]

                        log_sheet.append_row(newRow)
                        #items.append(name_i)
                        #item_ids.append(id_i)

                    else:
                        print("Ending scanning process...")
                        #curr_time = datetime.now()
                        print("Success!!!\n")
                        break


        else:
            print("Not a College Student ID!\n")

        #print(f"ID: {id}\nItem Name: {text}")
        #newRow = [id, text, "Reserved"]
        #sheet.append_row(newRow)
        #print("!"*5, "Data Inserted", "!"*5,"\n")
    #finally:
     #   GPIO.cleanup()
      #  sleep(0.5) #sleep for 0.5 second, prevent fast consecutive readings

