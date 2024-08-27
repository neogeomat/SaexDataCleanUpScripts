import tkMessageBox
from Tkinter import *
from CompactDb import compactDb
from LoadDb import LoadDb
import tkFileDialog
import shared_data
from Replace_mdb import replaceMDb
from Generalize import Generalize
from Recalculate_Extent import recalculate_extent
from Remove_Identical_Feature import Remove_Identical_Feature
from Repair_Layers_Geometry import Repair_Geometry
from mege_saex_mdb import mergeSaexMdbs
from attribute_check import attributeChecker
from file_filter import FileFilter  # Import the filter class
from filter_dialog import FilterDialog, show_filter_list  # Import the filter dialog
from attributeFill_ward_grid import Fill_Ward_Grid
from attributeFill_VDC_dist_code import Fill_VDC_Dist_Code
from Fill_FID import Fill_Par_FID

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
        cm_section = LabelFrame(self.master, text="Replace Whole MDb", padx=5, pady=5)
        cm_section.grid(row=1, column=0, padx=10, pady=10, sticky=E + W + N + S, columnspan=3)

        self.Sheet_cm = Label(cm_section, text="Choose Central Meridian", width=30)
        self.Sheet_cm.grid(row=1, column=0, padx=5, pady=5, sticky=E + W + N + S)

        options_cm = [
            "BLANK.mdb",
            "BLANK87.mdb",
            "BLANK84.mdb",
            "BLANK81.mdb"
        ]

        self.variable_cm = StringVar(cm_section)
        self.variable_cm.set(options_cm[1]) #default value
        self.optionmenu_cm = OptionMenu(cm_section, self.variable_cm, *options_cm)
        self.optionmenu_cm.grid(row=1, column=1, padx=5, pady=5, sticky=E + W + N + S)

        self.compactdb = Button(cm_section, text="Replace", command=lambda: replaceMDb(self,self.variable_cm.get()), width=30)
        self.compactdb.grid(row=1, column=2, padx=5, pady=5, sticky=E + W + N + S, columnspan=3)

        # Section for database operations
        db_section = LabelFrame(self.master, text="Apply Cleanup", padx=5, pady=5)
        db_section.grid(row=2, column=0, padx=10, pady=10, sticky=E + W + N + S, columnspan=2)

        self.compactdb = Button(db_section, text="Compact DB", command=lambda: compactDb(self), width=30)
        self.compactdb.grid(row=0, column=3, padx=5, pady=5, sticky=E + W + N + S, columnspan=2)

        self.attr_check = Button(db_section, text="Check Attributes", command=lambda: attributeChecker(self), width=30)
        self.attr_check.grid(row=1, column=3, padx=5, pady=5, sticky=E + W + N + S, columnspan=2)

        self.Sheet_sc = Label(db_section, text="Choose Mapped Scale", width=30)
        self.Sheet_sc.grid(row=2, column=0, padx=5, pady=5, sticky=E + W + N + S)

        options_sc = [
            "500",
            "600",
            "1200",
            "1250",
            "2400",
            "2500",
            "4800"
        ]

        self.variable_sc = StringVar(db_section)
        self.variable_sc.set(options_sc[5]) #default value

        self.optionmenu_sc = OptionMenu(db_section, self.variable_sc, *options_sc)
        self.optionmenu_sc.grid(row=2, column=1, padx=5, pady=5, sticky=E + W + N + S)

        self.attr_fill1 = Button(db_section, text="Fill Ward and Grid (Free)", command=lambda: Fill_Ward_Grid(self,self.variable_sc.get()), width=30)
        self.attr_fill1.grid(row=2, column=3, padx=5, pady=5, sticky=E + W + N + S, columnspan=2)

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
        self.VDCCode.grid(row=4, column=1, padx=5, pady=5, sticky=E + W + N + S, columnspan=2)

        self.attr_fill2 = Button(db_section, text="Fill District VDC Code", command=lambda: Fill_VDC_Dist_Code(self,self.DistrictCode.get(),self.VDCCode.get()), width=30)
        self.attr_fill2.grid(row=4, column=3, padx=5, pady=5, sticky=E + W + N + S, columnspan=2)

        self.corr_fid = Button(db_section, text="Correct FID", command=self.Correct_FID, width=30)
        self.corr_fid.grid(row=5, column=3, padx=5, pady=5, sticky=E + W + N + S, columnspan=2)

        self.tolerance_label_text = Label(db_section, text="Tolerance(m)")
        self.tolerance_label_text.grid(row=6, column=0, sticky="e", padx=5, pady=2)

        self.tolerance_entry = Entry(db_section)
        self.tolerance_entry.insert(0, "0.2")  # Insert default value
        self.tolerance_entry.grid(row=6, column=1, sticky="w", padx=5, pady=2)

        self.generalize = Button(db_section, text="Generalize", command=lambda: Generalize(self,self.tolerance_entry.get()), width=30)
        self.generalize.grid(row=6, column=3, padx=5, pady=5, sticky=E + W + N + S, columnspan=2)

        self.recalculate_extent = Button(db_section, text="ReCalculate Extent", command=lambda: recalculate_extent(self), width=30)
        self.recalculate_extent.grid(row=7, column=3, padx=5, pady=5, sticky=E + W + N + S, columnspan=2)

        self.remove_identical = Button(db_section, text="Remove Identical Constructions", command=lambda: Remove_Identical_Feature(self), width=30)
        self.remove_identical.grid(row=8, column=3, padx=5, pady=5, sticky=E + W + N + S, columnspan=2)

        self.repair_geometry = Button(db_section, text="Repair Geometry", command=lambda: Repair_Geometry(self), width=30)
        self.repair_geometry.grid(row=9, column=3, padx=5, pady=5, sticky=E + W + N + S, columnspan=2)


        # Section for database operations
        extra_section = LabelFrame(self.master, text="Extras", padx=5, pady=5)
        extra_section.grid(row=3, column=0, padx=10, pady=10, sticky=E + W + N + S)

        self.merge_all = Button(extra_section, text="Merge All", command=lambda: mergeSaexMdbs(self,self.variable_cm.get()), width=30)
        self.merge_all.grid(row=0, column=3, padx=5, pady=5, sticky=E + W + N + S, columnspan=2)

    def browse_folder(self):
        folder_selected = tkFileDialog.askdirectory()
        self.directory.delete(0, END)  # Clear the Entry widget
        self.directory.insert(0, folder_selected)  # Insert the selected folder path

    def load_db(self):
        directory = self.directory.get()
        LoadDb(directory)  # Pass the directory to LoadDb function

        # Update the OptionMenu based on the new central meridian
        if hasattr(shared_data, 'initial_central_meridian'):
            self.set_default_option(shared_data.initial_central_meridian)


    def get_default_option(self, cm_value):
        # Determine the default option based on cm_value
        if cm_value in [81.0, 84.0, 87.0]:
            return "BLANK{:.0f}.mdb".format(cm_value)
        return "BLANK.mdb"

    def set_default_option(self, cm_value):
        # Set the default value for the OptionMenu
        default_option = self.get_default_option(cm_value)
        self.variable_cm.set(default_option)

    def open_filter_dialog(self):
        if not shared_data.mdb_files:
            print("No files to filter.")
            return

        directory = self.directory.get()  # Get the directory path
        filter_obj = FileFilter(shared_data.mdb_files)
        FilterDialog(self.master, filter_obj, directory,shared_data.mdb_files)  # Pass directory to the filter dialog
        # Update the OptionMenu based on the new central meridian
        if hasattr(shared_data, 'initial_central_meridian'):
            self.set_default_option(shared_data.initial_central_meridian)


    def Correct_FID(self):
        for mdb in shared_data.filtered_mdb_files:
            Fill_Par_FID(self,mdb)
        tkMessageBox.showinfo(title="FID Corrected", message="Done")


