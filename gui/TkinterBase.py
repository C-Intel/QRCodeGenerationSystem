from sqlite3 import Row
import tkinter as tk
from tkinter.ttk import *
from main.qrAuthentication import qrAuthentication

class BaseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Guest Submission")
        self.geometry("720x500")
        self.resizable(True, True)
        self.style = tk.ttk.Style(self)

        container = tk.Frame(self, background="white")
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        

        self.frames = {}
        self.MainPage = MainPage
        self.SentPage = SentPage
        self.FailedPage = FailedPage
        self.DataPage = DataPage


        for F in {MainPage, SentPage, FailedPage, DataPage}:
            frame = F(self, container)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(MainPage)

        btn_data = Button(self, text="Check Data", command=lambda: self.DataPage.checkRecords(self))
        btn_data.pack(side="bottom")

        btn_main = Button(self, text="Home", command=lambda: self.show_frame(MainPage))
        btn_main.pack(side="bottom")

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class MainPage(tk.Frame):
    def __init__(self, parent, container):
        super().__init__(container)
        self.container = container

        lbl = tk.Label(self, text="Submit Info")
        lbl.grid(row=0, column=0, pady=0, padx=0)
        
        lbl_fname = tk.Label(self, text="First Name")
        lbl_fname.grid(row=1, column=0, padx=10, pady=10)
        entry_fname = tk.Entry(self)
        entry_fname.grid(row=1, column=1, padx=10, pady=10)

        lbl_lname = tk.Label(self, text="Last Name")
        lbl_lname.grid(row=2, column=0, padx=10, pady=10)
        entry_lname = tk.Entry(self)
        entry_lname.grid(row=2, column=1, padx=10, pady=10)

        lbl_id = tk.Label(self, text="Requester ID")
        lbl_id.grid(row=3, column=0, padx=10, pady=10)
        entry_id = tk.Entry(self)
        entry_id.grid(row=3, column=1, padx=10, pady=10)

        lbl_email = tk.Label(self, text="Email")
        lbl_email.grid(row=4, column=0, padx=10, pady=10)
        entry_email = tk.Entry(self)
        entry_email.grid(row=4, column=1, padx=10, pady=10)

        self.entries = {"first": entry_fname, "last": entry_lname, "id": entry_id, "email": entry_email}
        btn = tk.Button(self, text = "Send", command=lambda: self.updateSentPage(parent))
        #lambda: parent.show_frame(parent.SentPage)
        btn.grid(row=5, column=1, padx=0, pady=0)

    def createQrAuth(self):
        try:
            new_record = qrAuthentication(self.entries["first"].get(), self.entries["last"].get(), self.entries["id"].get(), self.entries["email"].get())
            new_record.start()
        except Exception as e:
            print("Failed to make qr obj")
            print(e)
    def updateSentPage(self, parent):
        parent.frames[SentPage].showEntries(self.entries)
        parent.show_frame(SentPage)
        self.createQrAuth()


#+-------------------------------------------------------------------------------------------------------------------------------------------------+

class SentPage(tk.Frame):
    def __init__(self, parent, container):
        super().__init__(container)
        lbl = tk.Label(self, text="Info Sent")
        lbl.grid(row=0, column=0, pady=0, padx=0)

    def showEntries(self, entries):
        i = 1
        for key, entry in entries.items():
            text_lbl = str(entry.get())
            lbl = tk.Label(self, text=f"{key}: {text_lbl}").grid(row=i, column=1, padx=10, pady=10)
            i += 1

#+-------------------------------------------------------------------------------------------------------------------------------------------------+

class FailedPage(tk.Frame):
    def __init__(self, parent, container):
        super().__init__(container)
        lbl = tk.Label(self, text="Failed Info Submission")
        lbl.grid(row=0, column=0, pady=0, padx=0)

#+-------------------------------------------------------------------------------------------------------------------------------------------------+

class DataPage(tk.Frame):
    def __init__(self, parent, container):
        super().__init__(container)
        lbl = tk.Label(self, text="Datapage")
        lbl.grid(row=0, column=0, pady=0, padx=0)
        records = qrAuthentication.getDatabaseContents()
        i = 1
        for record in records:
            text_lbl = str(record)
            lbl = tk.Label(self, text=text_lbl).grid(row=i, column=1, padx=10, pady=10)
            i += 1
    def checkRecords(parent):
        parent.show_frame(DataPage)
        
        


# if __name__ == "__main__":
#     app = BaseApp()
#     app.mainloop()