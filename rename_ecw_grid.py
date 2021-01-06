from Tkinter import *

version = "v1.1.3"

class App(Frame):
    global version
    global dic_case_sen

    def __init__(self, master):
        Frame.__init__(self, master)
        self.pack()
        self.grid()
        self.create_widgets()


    def create_widgets(self):
        """Create buttons that do nothing"""

        # create label for sheet
        self.Sheet = Label(self, text="Enter path to the main folder", width=30)
        self.Sheet.grid(row=0, column=0, padx=5, pady=5, sticky=E + W + N + S)

        # create entry.
        self.sheetentry1 = Entry(self, width=30)
        self.sheetentry1.grid(row=0, column=1, padx=5, pady=5, sticky=E + W + N + S)

        # create calculate button
        self.button4 = Button(self, text="Process", command=self.RenameImage, width=30)
        self.button4.grid(row=3, column=1, padx=5, pady=5, sticky=E + W + N + S)

        self.Sheet = Label(self, text="Instruction", width=30, font=("Helvetica", 10, "bold italic"), fg="blue")
        self.Sheet.grid(row=4, column=0, padx=5, pady=5, sticky=E + W + N + S)

        instruction = """\n
Input: Folder path

Process: 

Output: 

For recent file check https://github.com/neogeomat/SaexDataCleanUpScripts"""
        self.Sheet = Label(self, text=instruction, width=50, justify=LEFT, wraplength=400)
        self.Sheet.grid(row=5, columnspan=2, padx=5, pady=5, sticky=E + W + N + S)

    def RenameImage(self):  # sourcery skip
        import tkMessageBox
        import arcpy
        import os
        from arcpy import env
        import re
        path = self.sheetentry1.get()
        mdb_list = []
        exception_list= open(path+"\\exception_list_rename.csv","a")
        allerror = open (path + "\\regex.csv", "a")
        allerror.truncate (0)
        for root, dirnames, filenames in os.walk(path):
            [dirnames.remove(d) for d in list(dirnames) if os.path.join(root,d).lower().find('file')!=-1]
            for filename in filenames:
                if (filename.endswith('.ecw') or filename.endswith('.prj')):
                    name, file_ext = os.path.splitext(os.path.join(root,filename))
                    imagefile=os.path.join(root, filename)
                    print (imagefile)
                    x = re.findall ("(\d+)", filename)
                    print(x)
                    if x:
                        grid=x[0]
                        column=int(x[1])
                        row=int(x[2])
                        new_name=str(grid)+"_"+str(column+(row-1)*40).zfill(4)+file_ext
                        new_imagefile = os.path.join(root, new_name)
                        print new_name
                        try:
                            os.rename(imagefile,new_imagefile)
                        except:
                            exception_list.write("Rename Error for ," + imagefile + "\n")
                    else:
                        print(filename + "," + " ")
                        allerror.write (filename + "," + " " + "\n")
        tkMessageBox.showinfo(title="Rename Image" + version, message="Done")
        allerror.close()
        exception_list.close()


root = Tk()
root.title("Rename Image " + version)
myapp = App(root)
myapp.mainloop()
