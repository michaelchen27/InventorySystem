import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import font as tkFont
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
# import RPi.GPIO as GPIO
# from mfrc522 import SimpleMFRC522

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
session_item_id = session_sheet.col_values(4) #get borrowed items
session_item_name = session_sheet.col_values(5) #get borrowed items
# session_id_list = session_sheet.col_values(6) #get session id list


# RFID Setup
# reader = SimpleMFRC522()

# LED GPIO Setup
# GPIO.setup(12, GPIO.OUT)

# def flash_led():
#     GPIO.output(12, GPIO.HIGH)
#     time.sleep(0.5)
#     GPIO.output(12, GPIO.LOW)



#TKINTER MAIN CLASS, MANAGES EVERYTHING
class GUI:
    def __init__(self, master):
        self.master = master
        self.logout_frame = Frame(self.master)
        self.logout_frame.pack(side=TOP, fill=tkinter.BOTH)

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
        self.tempMessage = "" #Store Temporary Message that will be displayed periodically
        self.tempitem_Message = "" #Store Temporary Item Message that will be displayed periodically
        
        

        #MESSAGE CONFIGURATION
        self.message = Label(self.top_frame, text="Welcome to FTI Lab, please scan your KTM", font=("Arial Bold", 24))
        self.message.pack(side=TOP, padx=10)
        self.sub_message = Label(self.top_frame, text="", font=("Arial", 16))
        self.sub_message.pack(side=TOP)
        self.list_message = Label(self.top_frame, text="", font=("Arial", 14))
        self.list_message.pack(side=TOP)
        self.info_message = Label(self.top_frame, text="", font=("Arial", 12))
        self.info_message.pack(side=TOP)
        
        self.label_def_color = self.info_message.cget("bg")


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
        
        #LOGOUT BUTTON CONFIGURATION
        self.logout_button = Button(self.logout_frame, command=logout)
        self.logout_button.configure(
            text="Logout", background="Grey", 
            font= tkFont.Font(size=12)
        )
        self.logout_button.pack(side=RIGHT, padx=10, pady=10)
        self.logout_button['state'] = tkinter.DISABLED


        #AUTHORIZE USER USING KTM
        self.queue = Queue.Queue()
        ThreadedTask(self.queue, self.ktm_scan).start()
        self.master.after(100, self.ktm_verify)

#Modify Info message
    def clear_info_message(self):
        self.info_message.configure(text="", relief=FLAT, bg=self.label_def_color)
    def set_info_message(self, message):
        self.info_message.configure(text=f"{message}", relief=RIDGE, bg="gold")

#INITIALIZATION ROUTINE, VERIFY USER USING KTM
    def ktm_verify(self):
        try:
            id = self.queue.get(0)
            msg = self.queue.get(0)
            self.USER_ID = id
            self.USER_NAME = msg
            self.message.configure(text="Welcome, "+msg+" !")
            self.sub_message.configure(text="What would you like to do?")
            self.clear_info_message()
            self.logout_button['state'] = tkinter.NORMAL
            self.enable_buttons()
        except Queue.Empty:
            self.master.after(100, self.ktm_verify)

    def ktm_scan(self):
        #scanning then returning KTM name
        # id = ""
        # while True: #keep scanning until id is recognized
        #     self.tempMessage = "Welcome to FTI Lab, please scan your KTM"
        #     id, name = reader.read()
        #     id = str(id).strip()
        #     if (str(id) in db_mahasiswa_ids):
        #        name = str(db_mahasiswa_name[db_mahasiswa_ids.index(id)]).strip()
        #        break
        #     self.set_info_message("KTM not recognized! Please scan a valid KTM !")
        
        # placeholder code =========================================
        self.set_info_message("KTM not recognized! Please scan a valid KTM !")
        id, name =  "45025007063", "Michael"
        time.sleep(2)
        # end placeholder code =====================================
        return id, name

    def update_data(self):
        self.logout_button['state']=tkinter.DISABLED
        self.set_info_message("Updating data, please wait!")
        ThreadedTaskUpdateData(self.update_data_functions).start()

    def update_data_functions(self):
        mahasiswa_sheet = sh.worksheet("Mahasiswa")
        global mahasiswa_ids
        mahasiswa_ids = mahasiswa_sheet.col_values(1) #Get Student IDs

        item_sheet = sh.worksheet("Items")
        global db_item_list, db_item_status
        db_item_list = item_sheet.col_values(1) #Get Item IDs
        db_item_status = item_sheet.col_values(3) #Get Item Statuses

        #log_sheet = sh.worksheet("Logs") #not updated because no reading needed

        session_sheet = sh.worksheet("Session")
        global session_mahasiswa_id, session_item_id, session_item_name
        session_mahasiswa_id = session_sheet.col_values(1) #get mahasiswa IDs list
        session_item_id = session_sheet.col_values(4) #get borrowed items, in concatenated string, separator ","
        session_item_name = session_sheet.col_values(5) #get borrowed items, in concatenated string, separator ","
        
        self.logout_button['state'] = tkinter.NORMAL
        self.enable_buttons()
        # for i, x in enumerate(session_mahasiswa_id):
        #     print(f"{i}")
        #session_id_list = session_sheet.col_values(6) #get session id list

    def enable_buttons(self):
        self.borrow_button['state']=tkinter.NORMAL #enable buttons
        self.return_button['state']=tkinter.NORMAL #enable buttons
        if(self.info_message['text'] == "Updating data, please wait!"):
            self.clear_info_message()

    

#PLACEHOLDER FUNCTIONS
    def borrow_solder(self):
        time.sleep(2)
        return "794796054884", "Solder"
    def borrow_mul1(self):
        time.sleep(4)
        return "320695199595", "Multimeter #1"
    def borrow_invalid(self):
        time.sleep(6)
        return "123123123323", "blyat"
    def borrow_mul2(self):
        time.sleep(8)
        return "236830417729", "Multimeter #2"
    def borrow_solder2(self):
        time.sleep(10)
        return "794796054884", "Solder"
    def ktm_michael(self):
        time.sleep(13)
        return "45025007063", "Michael"
    


#BORROW FUNCTION, INCLUDES RFID READ AND MANAGING GUI WHILE BORROWING
    def borrow_function(self):
        # DO RFID READS HERE
        # id_item, name_item = "", ""
        # while True:
        #     id_item, name_item = reader.read()
        #     id_item = str(id_item).strip()
        #     name_item = str(name_item).strip()
        #     if (id_item in db_item_list or id_item == self.USER_ID):
        #         break
        #     self.set_info_message("RFID Tag not recognized! Please scan KTM or Valid Tags only!")


        #placeholder code ====================================================
        id_item, name_item =  "794796054884", "Solder"
        time.sleep(2)
        #end placeholder code ================================================

        return id_item, name_item

    def start_borrow(self):
        #initiate variables
        self.items = [] #clear item list
        self.item_ids = set() #clear item sets to check for uniques
        self.item_indexes = set() #clear item indexes 
        self.sessions = []
        self.tempitem_Message = "" #List of all item currently on "cart"
        
        self.borrow_button['state']=tkinter.DISABLED #disable buttons
        self.return_button['state']=tkinter.DISABLED #disable buttons
        self.queue = Queue.Queue() #queue to store RFID read result, is used to let the GUI know that read is done or not
       
        self.message.configure(text="Borrowing Item(s)")
        self.sub_message.configure(text="Scan the item, Scan your KTM to finish scanning items!\nScan your KTM to cancel borrow process")
        self.list_message.configure(text="")

        # ThreadedTask(self.queue, self.borrow_function).start() #start borrow_function at other thread        
        # #placeholder routine===============================
        ThreadedTask(self.queue, self.borrow_solder).start()       
        ThreadedTask(self.queue, self.borrow_mul1).start()       
        ThreadedTask(self.queue, self.borrow_invalid).start()       
        ThreadedTask(self.queue, self.borrow_mul2).start()       
        ThreadedTask(self.queue, self.borrow_solder2).start()       
        ThreadedTask(self.queue, self.ktm_michael).start()       
        # #=====================================================
        
        self.master.after(100, self.process_borrow) #schedule after 100ms, run process_queue function  

    def process_borrow(self):
        try:
            id_item = self.queue.get(0) #get id result
            name_item = self.queue.get(0) #get name result
            
            if id_item in db_item_list: #check if it an item and if it is available
                if db_item_status[db_item_list.index(id_item)] == "Available":
                    # Get item indexes
                    self.item_indexes.add(db_item_list.index(id_item))

                    if id_item in self.item_ids: #if item is a duplicate
                        print(f"Item: {name_item} has already been added") # comment this line to not clutter console?
                        self.set_info_message("Item "+ name_item + " has already been added!")
                        #continue
                    else: #not a duplicate
                        self.item_ids.add(id_item) #add to set
                        curr_time = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M")
                        newRow = [id_item, name_item, self.USER_ID, self.USER_NAME, curr_time]
                        self.items.append(newRow)
                        print(f"Item: {name_item} added")  
                        #Print Message (List style)
                        self.list_message['text'] += "- " + name_item + " has been added\n" 
                        self.clear_info_message()
                        # flash_led()

                else: # not available
                    self.set_info_message("Item "+name_item+ " is not available!")
                
                ThreadedTask(self.queue, self.borrow_function).start() #start borrow_function at other thread again        
                self.master.after(100, self.process_borrow) #wait for result again


            elif id_item == self.USER_ID: #if ktm, append to gsheet  and end process 
                if len(self.item_ids) == 0: #empty "cart"
                    self.message.configure(text=f"Welcome, {self.USER_NAME}!")
                    self.sub_message.configure(text="Item Borrowing Cancelled!")
                    self.list_message.configure(text="")
                    self.clear_info_message()
                    self.enable_buttons() #enable both button

                else: #end scan process and submit to database
                    self.sub_message.configure(text="Ending scan process...")
                    #log_sheet.append_rows(self.items)
                    curr_time = str(datetime.datetime.now())
                    
                    # Update Item Status
                    for i in self.item_indexes:
                        item_sheet.update_cell(i+1, 3, 'Unavailable')
                        item_sheet.update_cell(i+1, 4, str(self.USER_NAME))
                    
                    for item in self.items:
                        newRow = [self.USER_ID, self.USER_NAME, curr_time, item[0], item[1]]
                        self.sessions.append(newRow)
                    session_sheet.append_rows(self.sessions)

                    self.message['text'] ="Welcome, "+self.USER_NAME+" !"
                    self.enable_buttons() #enable buttons
                    self.update_data() #update data
                    self.sub_message.configure(text="Borrow success!")
                    self.list_message.configure(text="")
                    self.clear_info_message()

            else: 
                self.set_info_message("Item "+name_item+ " is not a valid item!")
                ThreadedTask(self.queue, self.borrow_function).start() #start borrow_function at other thread again        
                self.master.after(100, self.process_borrow)

        except Queue.Empty:
            self.master.after(100, self.process_borrow)
    
#RETURNING FUNCTION
    def start_returning(self):
        self.borrow_button['state']=tkinter.DISABLED #disable buttons
        self.return_button['state']=tkinter.DISABLED #disable buttons
        self.frames = []
        self.index = []
        self.item_label_pointer = {}
        self.item_returning = set()
        self.curr_item_id = []
        self.index_returning = []
        for i, x in enumerate(session_mahasiswa_id):
            if x == self.USER_ID:
                self.index.append(i)
                self.curr_item_id.append(session_item_id[i])
        if len(self.index) != 0 :
            self.message.configure(text="Item Borrowed by "+self.USER_NAME)

            self.sub_message.configure(text="Scan item tag to return it, scan KTM to finish")

            for idx, value in enumerate(self.index):
                session_frame = Frame(self.master, borderwidth=2, relief="solid")
                session_frame.pack(side=TOP, pady=10, padx=10)
                self.frames.append(session_frame)
                item_label = Label(session_frame, text=str(idx+1)+". " + session_item_name[value], font=("Arial", 12))
                item_label.pack(side=LEFT)
                
                self.item_label_pointer[session_item_id[value]] = item_label, value #reference pointer 

            ThreadedTask(self.queue, self.return_function).start()
            # #placeholder routine===============================
            ThreadedTask(self.queue, self.borrow_solder).start()       
            ThreadedTask(self.queue, self.borrow_mul1).start()       
            ThreadedTask(self.queue, self.borrow_invalid).start()       
            ThreadedTask(self.queue, self.borrow_mul2).start()       
            ThreadedTask(self.queue, self.borrow_solder2).start()       
            ThreadedTask(self.queue, self.ktm_michael).start()       
            # #=====================================================
            
            self.master.after(100, self.process_return)
            print("Which item do you want to return?")
                
        else:
            self.enable_buttons() #enable buttons
            self.sub_message.configure(text="No session available!")
            print("Session not available, returning")

    def return_function(self):
        # DO RFID READS HERE
        # id_item, name_item = "", ""
        # while True:
        #     id_item, name_item = reader.read()
        #     id_item = str(id_item).strip()
        #     name_item = str(name_item).strip()
        #     if (id_item in db_item_list or id_item == self.USER_ID):
        #         break
        #     self.set_info_message("RFID Tag not recognized! Please scan KTM or Valid Tags only!")


        #placeholder code ====================================================
        id_item, name_item =  "794796054884", "Solder"
        time.sleep(2)
        #end placeholder code ================================================

        return id_item, name_item

    def process_return(self):
        try:
            id_item = self.queue.get(0) #get id result
            name_item = self.queue.get(0) #get name result

            if id_item in self.curr_item_id: #valid scan (in current session)
                if id_item not in self.item_returning: #not scanned yet 
                    self.item_returning.add(id_item)
                    label, idx = self.item_label_pointer[id_item]
                    label.configure(bg="pale green")
                    self.index_returning.append(idx)
                    self.set_info_message("Marked " + name_item + " for returning")
                else: #already scanned
                    self.set_info_message("Item " + name_item+ " has already been marked for returning" )
                ThreadedTask(self.queue, self.return_function).start()
                self.master.after(100, self.process_return)
            elif id_item in self.item_ids: #valid but not borrowed
                self.set_info_message("Item " + name_item + " is not borrowed by this user!")
                ThreadedTask(self.queue, self.return_function).start()
                self.master.after(100, self.process_return)
           
            elif id_item == self.USER_ID: #user id, end this returning
                # Delete frames
                for frame in self.frames:
                    for widget in frame.winfo_children():    
                        widget.destroy()
                    frame.pack_forget()
                if len(self.item_returning) == 0: #nothing is selected
                    self.sub_message.configure(text="Nothing selected!")
                    self.clear_info_message()
                    self.enable_buttons() #enable buttons
                else: #some is selected
                    item_indexes = set()
                    self.sub_message.configure(text="Returning selected items, please wait...")
                    for i in self.item_returning:
                        item_indexes.add(db_item_list.index(i))
                    for i in item_indexes:
                        item_sheet.update_cell(i+1, 3, "Available")
                        item_sheet.update_cell(i+1, 4, "")
                    # Delete Session 
                    self.index_returning.sort(reverse=True) #descending order since gspread deletes a row THEN readjust all index
                    for i in self.index_returning:
                        print(f"i = {i}, item name = {session_item_name[i]}")
                        session_sheet.delete_rows(i+1) # +1 for adjusting row header
                    #Re initialize
                    self.sub_message.configure(text="Item(s) successfully returned!")
                    self.message.configure(text="Welcome, "+self.USER_NAME+" !")
                    self.clear_info_message()
                    self.enable_buttons() #enable buttons
                    self.update_data()
                    print("Session concluded successfully!")

            else: #invalid scan
                self.set_info_message("Please scan a valid RFID tag!")
                ThreadedTask(self.queue, self.return_function).start()
                self.master.after(100, self.process_return)

            
        except Queue.Empty:
            self.master.after(100, self.process_return)



   


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

class ThreadedTaskUpdateData(threading.Thread):
    def __init__(self, task):
        threading.Thread.__init__(self)
        self.task = task
    def run(self):
        self.task()

#MAIN DRIVER? TO INITIATE TKINTER SINCE TKINTER IS BLOCKING GUI
if __name__ == '__main__':

    def logout():
        root.destroy()
        main_init()

    def main_init():
        global root
        root = Tk()
        root.title("Inventory System GUI")
        main_ui = GUI(root)
        root.mainloop()

    main_init()