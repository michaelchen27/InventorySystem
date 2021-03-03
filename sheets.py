# Gspread Libraries
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint

# RFID Libraries
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

# Gspread Setup
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)

client = gspread.authorize(creds)

sheet = client.open("Inventory System").sheet1

# RFID Setup
reader = SimpleMFRC522()

try:
    print("Bring tag to reader")
    id, text = reader.read()
finally:
    GPIO.cleanup()

print(f"ID: {id}\nItem Name: {text}")

insertRow = [id, text, "Reserved"]
sheet.insert_row(insertRow, 4)

print("!"*5, "Data Inserted", "!"*5,"\n")

