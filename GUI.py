import tkinter as tk
from tkinter import filedialog
import os
import time

class App:
    def __init__(self):
        pass
    def choose_directory(self):
        directory_root = tk.Tk()
        directory_root.withdraw()
        path_work = filedialog.askdirectory()
        return path_work.replace('/', "\\")
    def choose_file(self, file_type=None, count=None):
        count=1 if count==None else count
        filetype = file_type if file_type is not None else [('All files', '*.*'), ("Gmail JSON Credentials", '*.json'), ('Pickle Token', '*.pickle'), ("CSV files", "*.csv")]
        directory_root = tk.Tk()
        directory_root.withdraw()
        path_work = filedialog.askopenfilename(filetypes=filetype)
        if path_work == '':
            if count<3:
                print('Error, no file selected. Please try again.')
                time.sleep(1)
                return self.choose_file(file_type=filetype, count=count+1)
            else:
                print("No file selected. Giving up.")
        else:
            print(f"File found! {path_work}")
            return path_work.replace('/', "\\")
        

    def Enter_Credentials(self):
        def __submit_login():
            results = (user_entry.get(), password_entry.get())
            print(results)
            return results
        login_page = tk.Tk()
        login_page.title("Log in to LinkedIn")
        user_field = tk.Label(login_page, text="Username").grid(row=0, column=0)
        user_entry = tk.Entry(login_page, width=50)
        user_entry.grid(row=0, column=1)
        # user_entry.insert(0, "Username")
        password_field = tk.Label(login_page, text="Password").grid(row=1, column=0)
        password_entry = tk.Entry(login_page, show="*", width=50)
        password_entry.grid(row=1,column=1)
        # password_entry.insert(0, "Password")
        
        
        
        submitButton = tk.Button(login_page, text="Submit", command=__submit_login).grid(row=0, column=2)
        cancelButton = tk.Button(login_page, text="Cancel", command=login_page.destroy).grid(row=1, column=2)
        # user_entry.pack()
        # password_entry.pack()
        # submitButton.pack()
        self.center_window(login_page, 420, 69)
        login_page.mainloop()
        
        
        
    @staticmethod
    def center_window(host, width=300, height=200):
        # get screen width and height
        screen_width = host.winfo_screenwidth()
        screen_height = host.winfo_screenheight()

        # calculate position x and y coordinates
        x = (screen_width/2) - (width/2)
        y = (screen_height/2) - (height/2)
        host.geometry('%dx%d+%d+%d' % (width, height, x, y))
        
        
        
    def Startup_Page(self):
        root = tk.Tk()
        root.title("Welcome to Zombocom")
        
        
        
        
        
        # root.geometry('300x80')
        firstLabel = tk.Label(root, text="Welcome to my zombocombo")
        secondLabel = tk.Label(root, text="\tPlease enjoy your stay.")
        spacer = tk.Label(root, text="\t")
        dirButton = tk.Button(root, text="Data Directory", command = self.choose_directory, width=20)
        
        credButton = tk.Button(root, text="Gmail Credentials", command = self.choose_file, width=20)
        
        linkedinButton = tk.Button(root, text="LinkedIn", command=self.Enter_Credentials, width=20)
        
        firstLabel.grid(row=0,column=0)
        secondLabel.grid(row=1,column=0)
        spacer.grid(row=2,column=1)
        dirButton.grid(row=0,column=2)
        credButton.grid(row=1,column=2)
        linkedinButton.grid(row=2,column=2)
        # dirButton.pack()
        # credButton.pack()
        # linkedinButton.pack()
        self.center_window(root, 400, 80)
        
        root.mainloop()
        
    def To_Parsing():
        
if __name__=="__main__":
    # print(choose_directory())
    app = App()
    filetypes = {
        "JSON": [("Gmail JSON Credentials", '*.json')],
        "Errything": [('All files', '*.*'), ("Gmail JSON Credentials", '*.json'), ('Pickle Token', '*.pickle'), ("CSV files", "*.csv")],
    }
    # choose_file(filetypes['JSON'])
    # choose_file()
    app.Startup_Page()