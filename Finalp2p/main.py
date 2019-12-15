import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from pathlib import Path
import os

apps = []
rec = []

if os.path.isfile('save.txt'):
    with open('save.txt', 'r') as f:
        tempApps = f.read()
        tempApps = tempApps.split(',')
        apps = [x for x in tempApps if x.strip()]

if os.path.isfile('savenames.txt'):
    with open('savenames.txt', 'r') as a:
        tempname = a.read()
        tempname = tempname.split(',')
        rec = [x for x in tempname if x.strip()]


class Main(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.init_main()

    def init_main(self):

        toolbar = tk.Frame(bg='#d7d8e0', bd=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        self.add_img = tk.PhotoImage(file='addnew.gif')
        btn_open_dialog = tk.Button(toolbar, text='add', command=self.open_dialog, bg='#d7d8e0', bd=0, compound=tk.TOP,
                                    image=self.add_img)
        btn_open_dialog.pack(side=tk.LEFT)

        # sync button
        self.add_img1 = tk.PhotoImage(file='syncbutton.gif')
        btn_open_dialog1 = tk.Button(toolbar, text='sync', bg='#d7d8e0', bd=0, compound=tk.TOP,
                                     image=self.add_img1)
        btn_open_dialog1.pack(side=tk.RIGHT)

        self.tree = ttk.Treeview(self, column=('Location'), height=15, show='headings')
        self.tree.column('Location', width=400)
        self.tree.heading('Location', text='Dest Location')
        self.tree.pack(side=tk.TOP)
        self.addtotree(self)
        scrollBar = Scrollbar(self, orient="vertical", command=self.tree.yview)

        self.tree.configure(yscrollcommand=scrollBar.set)

        self.tree1 = ttk.Treeview(self, column=('Location'), height=15, show='headings')
        self.tree1.column('Location', width=400)
        self.tree1.heading('Location', text='Src Location')
        self.tree1.pack()
        self.addtotree1(self)

    def open_dialog(self):
        Child()
        self.addtotree(self)
        self.addtotree1(self)

    @staticmethod
    def addtotree(self):
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)

        for i in apps:
            self.tree.insert('', 'end', i, )
            self.tree.set(i, 'Location', i)
    @staticmethod
    def addtotree1(self):
        records = self.tree1.get_children()
        for element in records:
            self.tree1.delete(element)

        for ii in rec:
            self.tree1.insert('', 'end', ii)
            self.tree1.set(ii, 'Location', ii)


class Child(tk.Toplevel):

    def __init__(self):
        super().__init__(root)
        self.init_child()


    def fileDialog(self):
        self.filename = filedialog.askopenfilename(initialdir="/", title="Select A File",
                                                   filetypes=(("game files", "*.*"), ("All Files", "*.*")))

        path1 = Path(self.filename).parent.absolute()
        apps.append(str(path1) + '/')

    def fileDialogforRec(self):
        self.filename = filedialog.askopenfilename(initialdir="/", title="Select A File",
                                                   filetypes=(("game files", "*.*"), ("All Files", "*.*")))
        path = Path(self.filename).parent.absolute()
        rec.append(str(path) + '/')

    def init_child(self):
        self.title('')
        self.geometry('400x220+400+300')
        self.resizable(False, False)
        self.usertext = StringVar()
        self.usertext.set('Type here')
        label_description = tk.Label(self, text='rec Location')
        label_description.place(x=50, y=50)

        self.entry_description = ttk.Entry(self, textvariable=self.usertext)
        self.entry_description.place(x=200, y=50)

        btn_cancel = ttk.Button(self, text='close', command=self.destroy)
        btn_cancel.place(x=300, y=170)

        btn_openfile = ttk.Button(self, text='Browse file', command=self.fileDialog)
        btn_openfile.place(x=250, y=110)

        btn_openfile = ttk.Button(self, text='Browse file for Rec', command=self.fileDialogforRec)
        btn_openfile.place(x=250, y=130)

        btn_ok = ttk.Button(self, text='ok', command=self.takeit)
        btn_ok.place(x=220, y=170)

        self.grab_set()
        self.focus_set()

    def takeit(self):
        # rec.append(self.usertext.get())
        # print(self.usertext.get())
        #m = Main()
        #m.addtotree(self)
        #m.addtotree1(self)
        Main.addtotree(self)
        Main.addtotree1(self)

        self.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = Main(root)
    app.pack()
    root.title("S-Play")
    root.geometry("650x700+300+200")
    root.resizable(False, False)

    root.mainloop()

    with open('save.txt', 'w') as f:
        for app in apps:
            f.write(str(app) + ',')

    with open('savenames.txt', 'w')as a:
        for name in rec:
            a.write(str(name) + ',')
