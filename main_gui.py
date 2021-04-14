import tkinter
from tkinter import *
from tkinter import ttk
import queue as Queue
import threading
import time
import random
import os

#Set Display to :20.0
if os.environ.get('DISPLAY','') != ':20.0':
    print('No display found. Using display :20.0')
    os.environ.__setitem__('DISPLAY', ':20.0')

#in windows Shell 
#cd C:\Program Files (x86)\Xming
#xming :20.0 -ac -scrollbars

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
sh = client.open("Inventory System")

# Get Sheets
mahasiswa_sheet = sh.worksheet("Mahasiswa")
db_mahasiswa_ids = mahasiswa_sheet.col_values(1) #Get Student IDs
db_mahasiswa_name = mahasiswa_sheet.col_values(2) #Get Student Name

item_sheet = sh.worksheet("Items")
db_item_list = item_sheet.col_values(1) #Get Item IDs
db_item_status = item_sheet.col_values(3) #Get Item Statuses

log_sheet = sh.worksheet("Logs")

session_sheet = sh.worksheet("Session")
session_mahasiswa_id = session_sheet.col_values(1) #get mahasiswa IDs list
session_item_id = session_sheet.col_values(4) #get borrowed items, in concatenated string, separator ","
session_item_name = session_sheet.col_values(5) #get borrowed items, in concatenated string, separator ","
session_id_list = session_sheet.col_values(6) #get session id list


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
        self.top_frame = Frame(self.master)
        self.top_frame.pack(side=TOP)

        self.bot_frame = Frame(self.master)
        self.bot_frame.pack(side=BOTTOM)
        
        #VARIABLES HERE
        self.USER_ID = ""
        self.USER_NAME = "" #store ktm name for ending transactions
        
        #RESET PER SESSION
        self.items = [] #item lists
        self.item_ids = set() #item sets to check for uniques
        self.item_indexes = set() #item indexes 
        self.sessions = [] #session information
        self.borrowMessage = "" #Borrowing Message

        #MESSAGE CONFIGURATION
        self.message = Label(self.top_frame, text="Welcome to FTI Lab, please scan your KTM", font=("Arial Bold", 24))
        self.message.pack(side=TOP)
        self.item_message = Label(self.top_frame, text="", font=("Arial", 16))
        self.item_message.pack(side=TOP)


        #BORROW BUTTON CONFIGURATION
        self.borrow_button = Button(self.bot_frame, command=self.start_borrow)
        self.borrow_button.configure(
            text="BORROW Lab Equipments", background="Grey",
            padx=50
            )
        self.borrow_button.pack(side=LEFT, pady=10, padx=10)
        self.borrow_button['state'] = tkinter.DISABLED #disable until KTM Scan is successful

        #RETURN BUTTON CONFIGURATION
        self.return_button = Button(self.bot_frame, command=self.start_returning)
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
        id = ""
        while True: #keep scanning until id is recognized
            id, name = reader.read()
            id = str(id).strip()
            if (str(id) in db_mahasiswa_ids):
               name = str(db_mahasiswa_name[db_mahasiswa_ids.index(id)]).strip()
               break
            self.message.configure(text="KTM not recognized! Please scan a valid KTM !")
        
        # placeholder code =========================================
        # id, name =  "45025007063", "Michael"
        # time.sleep(2)
        # end placeholder code =====================================
        return id, name

    def update_data(self):
        mahasiswa_sheet = sh.worksheet("Mahasiswa")
        global mahasiswa_ids
        mahasiswa_ids = mahasiswa_sheet.col_values(1) #Get Student IDs

        item_sheet = sh.worksheet("Items")
        global db_item_list, db_item_status
        db_item_list = item_sheet.col_values(1) #Get Item IDs
        db_item_status = item_sheet.col_values(3) #Get Item Statuses

        #log_sheet = sh.worksheet("Logs") #not updated because no reading needed

        session_sheet = sh.worksheet("Session")
        global session_mahasiswa_id, session_item_id, session_item_name, session_id_list
        session_mahasiswa_id = session_sheet.col_values(1) #get mahasiswa IDs list
        session_item_id = session_sheet.col_values(4) #get borrowed items, in concatenated string, separator ","
        session_item_name = session_sheet.col_values(5) #get borrowed items, in concatenated string, separator ","
        session_id_list = session_sheet.col_values(6) #get session id list

#BORROW FUNCTION, INCLUDES RFID READ AND MANAGING GUI WHILE BORROWING
    def borrow_function(self):
        # DO RFID READS HERE
        id_item, name_item = "", ""
        while True:
            id_item, name_item = reader.read()
            id_item = str(id_item).strip()
            name_item = str(name_item).strip()
            if (id_item in db_item_list or id_item == self.USER_ID):
                break
            self.item_message.configure(text="RFID Tag not recognized! Please scan KTM or Valid Tags only!")


        #placeholder code ====================================================
        # id_item, name_item =  "794796054884", "Solder"
        # time.sleep(2)
        #end placeholder code ================================================

        return id_item, name_item

    def start_borrow(self):
        #initiate variables
        self.items = [] #clear item list
        self.item_ids = set() #clear item sets to check for uniques
        self.item_indexes = set() #clear item indexes 
        self.sessions = []
        self.borrowMessage = "" #Reset Borrowing Message

        self.borrow_button['state']=tkinter.DISABLED #disable buttons
        self.return_button['state']=tkinter.DISABLED #disable buttons
        self.queue = Queue.Queue() #queue to store RFID read result, is used to let the GUI know that read is done or not

        self.item_message.configure(text="Scan the item, Scan your KTM to finish scanning items")

        ThreadedTask(self.queue, self.borrow_function).start() #start borrow_function at other thread        
        self.master.after(100, self.process_borrow) #schedule after 100ms, run process_queue function  


    def process_borrow(self):
        try:
            id_item = self.queue.get(0) #get id result
            name_item = self.queue.get(0) #get name result
            
            if id_item in db_item_list and db_item_status[db_item_list.index(id_item)] == "Available": #check if it an item and if it is available
                # Get item indexes
                self.item_indexes.add(db_item_list.index(id_item))

                if id_item in self.item_ids: #if item is a duplicate
                    def printbackMessage():
                        self.item_message.configure(text=f"{self.borrowMessage}")
                    print(f"Item: {name_item} has already been added") # comment this line to not clutter console?
                    self.item_message.configure(text="Item ")
                    Item_Name = [Item_Name for Item_Name in self.items if id_item in Item_Name][0]
                    self.item_message['text'] += Item_Name[1]+" has already been added!"
                    self.master.after(2000,printbackMessage)

                    #continue
                else:
                    self.item_ids.add(id_item) #add to set
                    curr_time = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M")
                    newRow = [id_item, name_item, self.USER_ID, self.USER_NAME, curr_time]
                    self.items.append(newRow)
                    print(f"Item: {name_item} added")  
                    self.borrowMessage = "Item "
                    for name in self.items:
                        self.borrowMessage += str(name[1]) 
                        if (self.items.index(name)+1)!=len(self.items):
                            self.borrowMessage += ", "
                    self.borrowMessage +=" will be borrowed."
                    self.item_message.configure(text=f"{self.borrowMessage}")
                    # flash_led()
                
                ThreadedTask(self.queue, self.borrow_function).start() #start borrow_function at other thread again        
                self.master.after(100, self.process_borrow) #wait for result again
            elif id_item == self.USER_ID and len(self.item_ids)==0:
                self.item_message.configure(text="Borrowing Item Cancelled")
                self.borrow_button['state']=tkinter.NORMAL #enable buttons
                self.return_button['state']=tkinter.NORMAL #enable buttons

            elif id_item == self.USER_ID: #if ktm, append to gsheet  and end process 
                print("Ending scanning process...")
                log_sheet.append_rows(self.items)
                curr_time = str(datetime.datetime.now())
                
                print("Please Wait...\n")

                # Update Item Status
                for i in self.item_indexes:
                    item_sheet.update_cell(i+1, 3, 'Unavailable')
                    item_sheet.update_cell(i+1, 4, str(self.USER_NAME))
                
                # Get Item IDs
                borrowed_ids = set(map(lambda x:x[0], self.items)) #Get all item_id that is borrowed in this session. Format [id_i, name_i, id_m, name_m, time]
                borrowed_ids_string = ','.join(borrowed_ids)

                # Get Item Names
                borrowed_names = set(map(lambda x:x[1], self.items))
                borrowed_names_string = ','.join(borrowed_names)

                # Randomize Session ID?
                random_id = random.randint(1000,9999)
                while (random_id in session_id_list) :
                    random_id = random.randint(1000,9999)

                newRow = [self.USER_ID, self.USER_NAME, curr_time, borrowed_ids_string, borrowed_names_string, random_id]
                self.sessions.append(newRow)

                session_sheet.append_rows(self.sessions)

                
                print("Success!!!\n")
                

                self.borrow_button['state']=tkinter.NORMAL #enable buttons
                self.return_button['state']=tkinter.NORMAL #enable buttons
                self.update_data() #update data
                self.item_message.configure(text="Borrow success!")

        except Queue.Empty:
            self.master.after(100, self.process_borrow)
    

        


#RETURNING FUNCTION
    def start_returning(self):
        self.borrow_button['state']=tkinter.DISABLED #disable buttons
        self.return_button['state']=tkinter.DISABLED #disable buttons
        self.frames = []
        index = []
        for i, x in enumerate(session_mahasiswa_id):
            if x == self.USER_ID:
                index.append(i)
        if len(index) != 0 :
            for idx, value in enumerate(index):
                session_frame = Frame(self.master, borderwidth=2, relief="solid")
                session_frame.pack(side=TOP, pady=10, padx=10)
                self.frames.append(session_frame)
                
                header = Label(session_frame, text="Session #"+session_id_list[value], font=("Arial Bold", 24))
                header.pack(side=TOP)

                item_frame = Frame(session_frame)
                item_frame.pack(side=LEFT)

                items_name = session_item_name[value].split(',')
                for x, name in enumerate(items_name):
                    item = Label(item_frame, text=str(x+1)+". " + name, font=("Arial", 12))
                    item.pack(side=TOP)
                button_session = Button(session_frame, command= lambda value=value: self.end_session(value))
                button_session.configure(
                    text="End session", background="Grey",
                    padx=10
                    )
                button_session.pack(side=RIGHT, padx=10, pady=10)

            print("Which session do you want to conclude?")
                
        else:
            self.borrow_button['state']=tkinter.NORMAL #enable buttons
            self.return_button['state']=tkinter.NORMAL #enable buttons
            self.item_message.configure(text="No session available!")
            print("Session not available, returning")


    def end_session(self, idx):
        #Update Item Status
        items_ids = session_item_id[idx].split(',')
        item_indexes = set()
        for i in items_ids: 
            item_indexes.add(db_item_list.index(i))

        for i in item_indexes:
            item_sheet.update_cell(i+1, 3, "Available")
            item_sheet.update_cell(i+1, 4, "")

        # Delete Session 
        session_sheet.delete_rows(idx+1) # +1 for adjusting row header
        
        # print("IDX = "+str(idx))
        # for i in items_ids:
        #     print(i)

        for frame in self.frames:
            for widget in frame.winfo_children():    
                widget.destroy()
            frame.pack_forget()
        
        self.item_message.configure(text="Session concluded successfully!")
        self.borrow_button['state']=tkinter.NORMAL #enable buttons
        self.return_button['state']=tkinter.NORMAL #enable buttons
        self.update_data()
        print("Session concluded successfully!")



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
    root.title("Inventory System GUI")
    main_ui = GUI(root)
    root.mainloop()