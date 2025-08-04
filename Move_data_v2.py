from Tkinter import *
import tkMessageBox
import arcpy
import os
import time

version = "v1.0.1"

class App(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.pack()
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        # Folder path
        Label(self, text="Enter path to the main folder", width=30).grid(row=0, column=0, padx=5, pady=5, sticky=E + W)
        self.sheetentry1 = Entry(self, width=30)
        self.sheetentry1.grid(row=0, column=1, padx=5, pady=5, sticky=E + W)

        # X Shift
        Label(self, text="Enter X_Shift", width=30).grid(row=1, column=0, padx=5, pady=5, sticky=E + W)
        self.XShift = Entry(self, width=30)
        self.XShift.grid(row=1, column=1, padx=5, pady=5, sticky=E + W)

        # Y Shift
        Label(self, text="Enter Y_Shift", width=30).grid(row=2, column=0, padx=5, pady=5, sticky=E + W)
        self.YShift = Entry(self, width=30)
        self.YShift.grid(row=2, column=1, padx=5, pady=5, sticky=E + W)

        # Conditional Move Checkbox
        self.conditional_var = IntVar()
        self.conditional_checkbox = Checkbutton(self, text="Move only if centroid > thresholds", variable=self.conditional_var)
        self.conditional_checkbox.grid(row=3, columnspan=2, padx=5, pady=5, sticky=W)

        # Threshold X
        Label(self, text="Centroid X Threshold", width=30).grid(row=4, column=0, padx=5, pady=5, sticky=E + W)
        self.centroidX = Entry(self, width=30)
        self.centroidX.grid(row=4, column=1, padx=5, pady=5, sticky=E + W)

        # Threshold Y
        Label(self, text="Centroid Y Threshold", width=30).grid(row=5, column=0, padx=5, pady=5, sticky=E + W)
        self.centroidY = Entry(self, width=30)
        self.centroidY.grid(row=5, column=1, padx=5, pady=5, sticky=E + W)

        # Process Button
        Button(self, text="Process", command=self.moveData, width=30).grid(row=6, column=1, padx=5, pady=5, sticky=E + W)

        # Instruction
        Label(self, text="Instruction", width=30, font=("Helvetica", 10, "bold italic"), fg="blue").grid(row=7, column=0, padx=5, pady=5, sticky=W)
        instruction = """
Input: Folder path

Process:Input the folder location 
Output: Move Layer by Input Distance Database.
If 'Move only if centroid > thresholds' is checked, only move if centroid X and Y exceed given values.

For recent file check https://github.com/neogeomat/SaexDataCleanUpScripts"""
        Label(self, text=instruction, width=50, justify=LEFT, wraplength=400).grid(row=8, columnspan=2, padx=5, pady=5, sticky=W)

    def moveData(self):
        startTime = time.time()
        path = self.sheetentry1.get()
        mdb_list = []
        exception_list = open(path + "\\exception_list_move_data.csv", "a")
        count = 0

        try:
            xOffset = float(self.XShift.get())
            yOffset = float(self.YShift.get())
            centroidX = float(self.centroidX.get()) if self.conditional_var.get() else None
            centroidY = float(self.centroidY.get()) if self.conditional_var.get() else None
        except ValueError:
            tkMessageBox.showerror("Input Error", "Please enter valid numerical values.")
            return

        for root, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith('.mdb'):
                    mdb_list.append(os.path.join(root, filename))

        total_mdbs = len(mdb_list)

        for i in mdb_list:
            try:
                print("\nProcessing " + i)
                arcpy.env.workspace = i
                fcl = arcpy.ListFeatureClasses("*", "ALL")

                if self.conditional_var.get():
                    centroid_x_total = 0.0
                    centroid_y_total = 0.0
                    total_points = 0

                    for fc in fcl:
                        with arcpy.da.SearchCursor(fc, ["SHAPE@XY"]) as cursor:
                            for row in cursor:
                                centroid_x_total += row[0][0]
                                centroid_y_total += row[0][1]
                                total_points += 1

                    if total_points == 0:
                        raise ValueError("No features found to calculate centroid.")

                    avg_x = centroid_x_total / total_points
                    avg_y = centroid_y_total / total_points

                    if avg_x <= centroidX or avg_y <= centroidY:
                        print("Skipping " + i + " (centroid too low)")
                        continue  # Skip move

                print("Moving data " + i + "\n")
                # Apply shift
                for fc in fcl:
                    with arcpy.da.UpdateCursor(fc, ["SHAPE@XY"]) as cursor:
                        for row in cursor:
                            cursor.updateRow([[row[0][0] + xOffset, row[0][1] + yOffset]])
                count += 1

            except Exception as e:
                exception_list.write("Move Error for ," + i + "\n")
                print("Move error for " + i)
                print(e)

        print("Processed {} of {} MDBs".format(count, total_mdbs))
        print("Move process complete")
        exception_list.close()
        print('The script took {:.2f} seconds!'.format(time.time() - startTime))

        tkMessageBox.showinfo(title="move database " + version, message="Done")

root = Tk()
root.title("Move database " + version)
myapp = App(root)
myapp.mainloop()
