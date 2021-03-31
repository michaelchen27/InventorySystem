import tkinter
from tkinter import *
from tkinter import ttk
import queue as Queue
import threading
import time


#TKINTER MAIN CLASS, MANAGES EVERYTHING
class GUI:
    def __init__(self, master):
        self.master = master
        
        #VARIABLES HERE

        #MESSAGE CONFIGURATION
        self.message = Label(self.master, text="Welcome to FTI Lab, please scan your KTM", font=("Arial Bold", 24))
        self.message.pack(side=TOP)
        self.item_message = Label(self.master, text="", font=("Arial", 16))
        self.item_message.pack(side=TOP)

        self.ktmName = "" #store ktm name for ending transactions

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
            msg = self.queue.get(0)
            self.ktmName = msg
            self.message.configure(text="Welcome, "+msg+" !")
            self.borrow_button['state'] = tkinter.NORMAL
            self.return_button['state'] = tkinter.NORMAL
        except Queue.Empty:
            self.master.after(100, self.ktm_verify)

    def ktm_scan(self):
        #simulate scanning then returning KTM name, need to be replaced with actual RFID Read
        time.sleep(1)
        return "blyat"

#BORROW FUNCTION, INCLUDES RFID READ AND MANAGING GUI WHILE BORROWING
    def borrow_function(self):
        # DO RFID READS HERE
        time.sleep(2)
        # Return item name
        name_read = "a"
        return name_read

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
            msg = self.queue.get(0) #get reading result
            if msg != "blyat": #if not ktm
                #check for duplicate here, 
                #
                #
                #
                
                self.item_message['text'] += msg + ', ' 
                ThreadedTask(self.queue, self.borrow_function).start() #start borrow_function at other thread again        
                self.master.after(100, self.process_borrow) #wait for result again
            else: #if ktm
                self.end_borrow()
        except Queue.Empty:
            self.master.after(100, self.process_borrow)
    
    def end_borrow(self):
        #append stuff into gsheet here
        # ***
        # ***
        #append stuff into gsheet here
        self.borrow_button['state']=tkinter.NORMAL #enable buttons
        self.return_button['state']=tkinter.NORMAL #enable buttons
        self.message.configure(text="Borrow success!")

        


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
        res = self.task() # run the function that is passed in the args
        self.queue.put(res)


#MAIN DRIVER? TO INITIATE TKINTER SINCE TKINTER IS BLOCKING GUI
if __name__ == '__main__':
    root = Tk()
    root.title("Test non-blocking GUI")
    main_ui = GUI(root)
    root.mainloop()