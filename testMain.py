# Gspread Libraries
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint

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

# For test run, finite number of loop
i = 5

# Main program Loop
while (i > 0):
    try:
        print("Bring tag to reader")
        id, text = reader.read()
        print(f"ID: {id}\nItem Name: {text}")
        newRow = [id, text, "Reserved"]
        sheet.append_row(newRow)
        print("!"*5, "Data Inserted", "!"*5,"\n")
    finally:
        GPIO.cleanup()
        sleep(0.5) #sleep for 0.5 second, prevent fast consecutive readings
        i =- 1

