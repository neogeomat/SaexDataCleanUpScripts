from Tkinter import *
from CompactDb import compactDb
from LoadDb import LoadDb
import tkFileDialog
import shared_data
from attribute_check import attributeChecker
from file_filter import FileFilter  # Import the filter class
from filter_dialog import FilterDialog, show_filter_list  # Import the filter dialog
from attributeFill_ward_grid import Fill_Ward_Grid
from attributeFill_VDC_dist_code import Fill_VDC_Dist_Code


class DataCleanup:
    def __init__(self, master):
        self.master = master
        self.master.title("Data Clean Up Tools")

        self.create_widgets()

    def create_widgets(self):
        """Create buttons that do nothing"""

        # Section for loading and filtering files
        file_section = LabelFrame(self.master, text="Choose Path and Filter", padx=5, pady=5)
        file_section.grid(row=0, column=0, padx=10, pady=10, sticky=E + W + N + S, columnspan=3)

        # create label for sheet
        self.Sheet = Label(file_section, text="Choose Folder", width=30)
        self.Sheet.grid(row=0, column=0, padx=5, pady=5, sticky=E + W + N + S)

        # create entry.
        self.directory = Entry(file_section, width=30)
        self.directory.grid(row=0, column=1, padx=5, pady=5, sticky=E + W + N + S)

        self.browseDb = Button(file_section, text="Browse", command=self.browse_folder, width=30)
        self.browseDb.grid(row=0, column=2, padx=5, pady=5, sticky=E + W + N + S)

        self.loaddb = Button(file_section, text="Load DB", command=self.load_db, width=30)
        self.loaddb.grid(row=1, column=0, padx=5, pady=5, sticky=E + W + N + S, columnspan=3)

        self.filter_button = Button(file_section, text="Filter Files", command=self.open_filter_dialog, width=30)
        self.filter_button.grid(row=2, column=0, padx=5, pady=5, sticky=E + W + N + S, columnspan=1)

        self.show_filter = Button(file_section, text="Show Filtered Files", command=lambda: show_filter_list(self), width=30)
        self.show_filter.grid(row=2, column=1, padx=5, pady=5, sticky=E + W + N + S, columnspan=1)

        # Section for database operations
        cm_section = LabelFrame(self.master, text="Choose CM", padx=5, pady=5)
        cm_section.grid(row=1, column=0, padx=10, pady=10, sticky=E + W + N + S, columnspan=3)

        self.Sheet = Label(cm_section, text="Choose Central Meridian", width=30)
        self.Sheet.grid(row=1, column=0, padx=5, pady=5, sticky=E + W + N + S)

        options = [
            "Blank.mdb",
            "Blank87.mdb",
            "Blank84.mdb",
            "Blank81.mdb"
        ]

        self.variable = StringVar(cm_section)
        self.variable.set(options[1]) #default value
        self.optionmenu = OptionMenu(cm_section, self.variable, *options)
        self.optionmenu.grid(row=1, column=1, padx=5, pady=5, sticky=E + W + N + S)


        # Section for database operations
        db_section = LabelFrame(self.master, text="Apply Cleanup", padx=5, pady=5)
        db_section.grid(row=2, column=0, padx=10, pady=10, sticky=E + W + N + S, columnspan=3)

        self.compactdb = Button(db_section, text="Compact DB", command=lambda: compactDb(self), width=30)
        self.compactdb.grid(row=0, column=2, padx=5, pady=5, sticky=E + W + N + S, columnspan=3)

        self.attr_check = Button(db_section, text="Check Attributes", command=lambda: attributeChecker(self), width=30)
        self.attr_check.grid(row=1, column=2, padx=5, pady=5, sticky=E + W + N + S, columnspan=3)

        self.Sheet = Label(db_section, text="Choose Mapped Scale", width=30)
        self.Sheet.grid(row=2, column=0, padx=5, pady=5, sticky=E + W + N + S)

        options = [
            "500",
            "600",
            "1200",
            "1250",
            "2400",
            "2500",
            "4800"
        ]

        self.variable = StringVar(db_section)
        self.variable.set(options[5]) #default value(2500)
        self.optionmenu = OptionMenu(db_section, self.variable, *options)
        self.optionmenu.grid(row=2, column=1, padx=5, pady=5, sticky=E + W + N + S)

        self.attr_fill1 = Button(db_section, text="Fill Ward and Grid (Free)", command=lambda: Fill_Ward_Grid(self), width=30)
        self.attr_fill1.grid(row=2, column=2, padx=5, pady=5, sticky=E + W + N + S, columnspan=3)

        # create label for District
        self.Dist_code_label = Label(db_section, text="District Code", width=30)
        self.Dist_code_label.grid(row=3, column=0, padx=5, pady=5, sticky=E + W + N + S)

        # create entry.
        self.DistrictCode = Entry(db_section, width=30)
        self.DistrictCode.grid(row=3, column=1, padx=5, pady=5, sticky=E + W + N + S)

        # create label for VDC
        self.Vdc_code_label = Label(db_section, text="Enter VDC Code", width=30)
        self.Vdc_code_label.grid(row=4, column=0, padx=5, pady=5, sticky=E + W + N + S)

        # create entry.
        self.VDCCode = Entry(db_section, width=30)
        self.VDCCode.grid(row=4, column=1, padx=5, pady=5, sticky=E + W + N + S)

        self.attr_fill2 = Button(db_section, text="Fill District VDC Code", command=lambda: Fill_VDC_Dist_Code(self,self.DistrictCode.get(),self.VDCCode.get()), width=30)
        self.attr_fill2.grid(row=4, column=3, padx=5, pady=5, sticky=E + W + N + S, columnspan=3)

    def browse_folder(self):
        folder_selected = tkFileDialog.askdirectory()
        self.directory.delete(0, END)  # Clear the Entry widget
        self.directory.insert(0, folder_selected)  # Insert the selected folder path

    def load_db(self):
        directory = self.directory.get()
        LoadDb(directory)  # Pass the directory to LoadDb function

    def open_filter_dialog(self):
        if not shared_data.mdb_files:
            print("No files to filter.")
            return

        directory = self.directory.get()  # Get the directory path
        filter_obj = FileFilter(shared_data.mdb_files)
        FilterDialog(self.master, filter_obj, directory,shared_data.mdb_files)  # Pass directory to the filter dialog
