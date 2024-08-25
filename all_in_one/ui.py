from Tkinter import *
from CompactDb import compactDb
from LoadDb import LoadDb
import tkFileDialog
import shared_data
from attribute_check import attributeChecker
from file_filter import FileFilter  # Import the filter class
from filter_dialog import FilterDialog, show_filter_list  # Import the filter dialog
from attributeFill_ward_grid import Fill_Ward_Grid
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
        db_section = LabelFrame(self.master, text="Apply Cleanup", padx=5, pady=5)
        db_section.grid(row=1, column=0, padx=10, pady=10, sticky=E + W + N + S, columnspan=3)

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

        self.attr_check = Button(db_section, text="Fill Ward and Grid (Free)", command=lambda: Fill_Ward_Grid(self), width=30)
        self.attr_check.grid(row=2, column=2, padx=5, pady=5, sticky=E + W + N + S, columnspan=3)

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
