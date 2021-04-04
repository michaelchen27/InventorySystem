import tkinter
from tkinter import *
from tkinter import ttk
import queue as Queue
import threading
import time

#RFID IMPORTS, COMMENTED BECAUSE NO ACCESS TO HARDWARE
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

#GSPREAD IMPORTS
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
import datetime
import os

# Gspread initialization 
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)

# Get Sheets
mahasiswa_sheet = client.open("Inventory System").worksheet("Mahasiswa")
db_mahasiswa_ids = mahasiswa_sheet.col_values(1) #Get Student IDs

item_sheet = client.open("Inventory System").worksheet("Items")
db_item_list = item_sheet.col_values(1) #Get Item IDs

log_sheet = client.open("Inventory System").worksheet("Logs")
session_sheet = client.open("Inventory System").worksheet("Session")


# RFID Setup
reader = SimpleMFRC522()

# LED GPIO Setup
GPIO.setup(12, GPIO.OUT)

def flash_led():
    GPIO.output(12, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(12, GPIO.LOW)



#TKINTER MAIN CLASS, MANAGES EVERYTHING
class GUI:
    def __init__(self, master):
        self.master = master
        
        
        #VARIABLES HERE
        self.USER_ID = ""
        self.USER_NAME = "" #store ktm name for ending transactions
        
        #RESET PER SESSION
        self.items = [] #item lists
        self.item_ids = set() #item sets to check for uniques
        self.item_indexes = set() #item indexes 
        self.sessions = [] #session information


        #MESSAGE CONFIGURATION
        self.message = Label(self.master, text="Welcome to FTI Lab, please scan your KTM", font=("Arial Bold", 24))
        self.message.pack(side=TOP)
        self.item_message = Label(self.master, text="", font=("Arial", 16))
        self.item_message.pack(side=TOP)


        #BORROW BUTTON CONFIGURATION
        self.borrow_button = Button(self.master, command=self.start_borrow)
        self.borrow_button.configure(
            text="BORROW Lab Equipments", background="Grey",
            padx=50
            )
        self.borrow_button.pack(side=LEFT, pady=10, padx=10)
        self.borrow_button['state'] = tkinter.DISABLED #disable until KTM Scan is successful

        #RETURN BUTTON CONFIGURATION
        self.return_button = Button(self.master, command=self.rb_function)
        self.return_button.configure(
            text="RETURN Lab Equipments", background="Grey",
            padx=50
            )
        self.return_button.pack(side=RIGHT, pady=10, padx=10)
        self.return_button['state'] = tkinter.DISABLED #disable until KTM Scan is successful
        
        #AUTHORIZE USER USING KTM
        self.queue = Queue.Queue()
        ThreadedTask(self.queue, self.ktm_scan).start()
        self.master.after(100, self.ktm_verify)
        

#INITIALIZATION ROUTINE, VERIFY USER USING KTM
    def ktm_verify(self):
        try:
            id = self.queue.get(0)
            msg = self.queue.get(0)
            self.USER_ID = id
            self.USER_NAME = msg
            self.message.configure(text="Welcome, "+msg+" !")
            self.borrow_button['state'] = tkinter.NORMAL
            self.return_button['state'] = tkinter.NORMAL
        except Queue.Empty:
            self.master.after(100, self.ktm_verify)

    def ktm_scan(self):
        #scanning then returning KTM name
        id, name = reader.read()
        
        while(str(id) not in db_mahasiswa_ids): #keep scanning until id is recognized
            self.message.configure(text="KTM not recognized! Please scan a valid KTM !")
            id, name = reader.read()
        
        # placeholder code =========================================
        # time.sleep(1)
        # id, name = "id_9999999", "name_aaaaa"  
        # end placeholder code =====================================
        return id, name

#BORROW FUNCTION, INCLUDES RFID READ AND MANAGING GUI WHILE BORROWING
    def borrow_function(self):
        # DO RFID READS HERE
        id_item, name_item = reader.read()
        
        id_item = str(id_item).strip()
        name_item = str(name_item).strip()

        while(id_item not in db_item_list or id_item != self.USER_ID):
            self.message.configure(text="RFID Tag not recognized! Please scan KTM or Valid Tags only!")
            id_item, name_item = reader.read()
            id_item = str(id_item).strip()
            name_item = str(name_item).strip()


        #placeholder code ====================================================
        # time.sleep(2)
        # # Return item name
        # id_item, name_item = "a", "b"
        #end placeholder code ================================================

        return id_item, name_item

    def start_borrow(self):
        #initiate variables
        self.items = [] #clear item list
        self.item_ids = set() #clear item sets to check for uniques
        self.item_indexes = set() #clear item indexes 
        self.sessions = []

        self.borrow_button['state']=tkinter.DISABLED #disable buttons
        self.return_button['state']=tkinter.DISABLED #disable buttons
        self.queue = Queue.Queue() #queue to store RFID read result, is used to let the GUI know that read is done or not

        self.message.configure(text="Scan the item, Scan your KTM to finish scanning items")

        ThreadedTask(self.queue, self.borrow_function).start() #start borrow_function at other thread        
        self.master.after(100, self.process_borrow) #schedule after 100ms, run process_queue function  


    def process_borrow(self):
        try:
            id_item = self.queue.get(0) #get id result
            name_item = self.queue.get(0) #get name result
            
            if id_item in db_item_list: #if an item = not ktm
                # Get item indexes
                self.item_indexes.add(db_item_list.index(id_item))

                if id_item in self.item_ids: #if item is a duplicate
                    print(f"Item: {name_item} has already been added") # comment this line to not clutter console?
                    #continue
                else:
                    self.item_ids.add(id_item) #add to set
                    curr_time = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M")
                    newRow = [id_item, name_item, self.USER_ID, self.USER_NAME, curr_time]
                    self.items.append(newRow)
                    print(f"Item: {name_item} added")            
                    flash_led()
               
                self.item_message['text'] += name_item + ', ' 
                ThreadedTask(self.queue, self.borrow_function).start() #start borrow_function at other thread again        
                self.master.after(100, self.process_borrow) #wait for result again
            
            elif id_item == self.USER_ID: #if ktm, append to gsheet  and end process 
                print("Ending scanning process...")
                log_sheet.append_rows(self.items)
                curr_time = str(datetime.datetime.now())
                
                print("Please Wait...\n")

                # Update Item Status
                for i in self.item_indexes:
                    item_sheet.update_cell(i+1, 3, 'Unavailable')
                    item_sheet.update_cell(i+1, 4, str(self.USER_NAME))
                
                # Session Sheets
                borrowed_ids = set(map(lambda x:x[0], self.items)) #Get all item_id that is borrowed in this session. Format [id_i, name_i, id_m, name_m, time]
                borrowed_ids_string = ','.join(borrowed_ids)

                newRow = [self.USER_ID, self.USER_NAME, curr_time, borrowed_ids_string]
                self.sessions.append(newRow)
                session_sheet.append_rows(self.sessions)

                print("Success!!!\n")

                self.borrow_button['state']=tkinter.NORMAL #enable buttons
                self.return_button['state']=tkinter.NORMAL #enable buttons
                self.message.configure(text="Borrow success!")

        except Queue.Empty:
            self.master.after(100, self.process_borrow)
    

        


#RETURNING FUNCTION
    def rb_function(self):
        print("testing...")

#QUEUE LOGIC, TO WAIT FOR THREAD RESULT 
    def process_queue(self):
        try:
            msg = self.queue.get(0)
            # Show result of the task if needed
            print(msg)
            self.queueMessage = msg
            return msg
        except Queue.Empty:
            self.master.after(100, self.process_queue)

#MULTITHREAD CLASS, DO BLOCKING TASK HERE
class ThreadedTask(threading.Thread):
    def __init__(self, queue, task):
        threading.Thread.__init__(self)
        self.queue = queue
        self.task = task

    def run(self):
        # Do other blocking task here
        id, name = self.task() # run the function that is passed in the args
        self.queue.put(id)
        self.queue.put(name)


#MAIN DRIVER? TO INITIATE TKINTER SINCE TKINTER IS BLOCKING GUI
if __name__ == '__main__':
    root = Tk()
    root.title("Test non-blocking GUI")
    main_ui = GUI(root)
    root.mainloop()