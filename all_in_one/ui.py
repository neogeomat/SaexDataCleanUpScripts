import tkMessageBox
from Tkinter import *
import tkinter as tk
from ttk import Progressbar

from CompactDb import compactDb
from LoadDb import LoadDb
import tkFileDialog
import shared_data
from Replace_mdb import replaceMDb
from Generalize import Generalize
from Recalculate_Extent import recalculate_extent
from Remove_Identical_Feature import Remove_Identical_Feature
from Repair_Layers_Geometry import Repair_Geometry
from merge_dummy_planning import merge_dummy_planning
from mege_saex_mdb import mergeSaexMdbs
from attribute_check import attributeChecker
from file_filter import FileFilter  # Import the filter class
from filter_dialog import FilterDialog, show_filter_list  # Import the filter dialog
from attributeFill_ward_grid import Fill_Ward_Grid
from attributeFill_VDC_dist_code import Fill_VDC_Dist_Code
from Fill_FID import Correct_FID
from tkinter import *
from identical_parcels import Find_Identical_Feature

class DataCleanup:
    def __init__(self, master):
        self.master = master
        self.master.title("Data Clean Up Tools")
        self.create_widgets()

    def create_widgets(self):
        """Create buttons with light, colorful background colors"""

        # Define colors
        colors = {
            "light_blue": "#add8e6",
            "check_button": "#add8e6",
            "light_green": "#90ee90",
            "light_yellow": "#ffffe0",
            "light_coral": "#f08080",
            "light_pink": "#ffb6c1",
            "light_gray": "#d3d3d3",
            "white": "#ffffff"
        }

        # Section for loading and filtering files
        file_section = LabelFrame(self.master, text="Choose Path and Filter", padx=5, pady=5, bg=colors["light_blue"])
        file_section.grid(row=0, column=0, padx=5, pady=5, sticky=E + W + N + S, columnspan=2)

        # Create label for sheet
        self.Sheet = Label(file_section, text="Choose Folder", width=30, bg=colors["light_gray"])
        self.Sheet.grid(row=0, column=0, padx=5, pady=5, sticky=E + W + N + S)

        # Create entry
        self.directory = Entry(file_section, width=30, bg=colors["white"])
        self.directory.grid(row=0, column=1, padx=5, pady=5, sticky=E + W + N + S)

        self.browseDb = Button(file_section, text="Browse", command=self.browse_folder, width=30, bg=colors["light_coral"])
        self.browseDb.grid(row=0, column=2, padx=5, pady=5, sticky=E + W + N + S)

        self.loaddb = Button(file_section, text="Load DB", command=self.load_db, width=45, bg=colors["light_coral"])
        self.loaddb.grid(row=1, column=0, padx=5, pady=5, sticky=E + W + N + S, columnspan=3)

        self.filter_button = Button(file_section, text="Filter Files", command=self.open_filter_dialog, width=30, bg=colors["light_coral"])
        self.filter_button.grid(row=2, column=0, padx=5, pady=5, sticky=E + W + N + S, columnspan=2)

        self.show_filter = Button(file_section, text="Show Filtered Files", command=lambda: show_filter_list(self), width=30, bg=colors["light_coral"])
        self.show_filter.grid(row=2, column=2, padx=5, pady=5, sticky=E + W + N + S, columnspan=1)

        # Section for database operations
        cm_section = LabelFrame(self.master, text="Replace Whole MDb", padx=5, pady=5, bg=colors["light_blue"])
        cm_section.grid(row=1, column=0, padx=5, pady=5, sticky=E + W + N + S, columnspan=2)

        self.Sheet_cm = Label(cm_section, text="Choose Central Meridian", width=30, bg=colors["light_gray"])
        self.Sheet_cm.grid(row=1, column=0, padx=5, pady=5, sticky=E + W + N + S,columnspan=1)

        options_cm = [
            "BLANK.mdb",
            "BLANK81.mdb",
            "BLANK84.mdb",
            "BLANK87.mdb"
        ]

        self.variable_cm = StringVar(cm_section)
        self.variable_cm.set(options_cm[1]) # Default value
        self.optionmenu_cm = OptionMenu(cm_section, self.variable_cm, *options_cm)
        self.optionmenu_cm.config(bg=colors["white"])
        self.optionmenu_cm.grid(row=1, column=1, padx=5, pady=5, sticky=E + W + N + S,columnspan=1)

        self.compactdb = Button(cm_section, text="Replace", command=lambda: replaceMDb(self, self.variable_cm.get()), width=30, bg=colors["light_coral"])
        self.compactdb.grid(row=1, column=2, padx=5, pady=5, sticky=E + W + N + S, columnspan=1)

        # Section for database operations
        db_section = LabelFrame(self.master, text="Apply Cleanup", padx=5, pady=5, bg=colors["light_blue"])
        db_section.grid(row=2, column=0, padx=5, pady=5, sticky=E + W + N + S, columnspan=2)

        # Store the checkbutton states
        self.check_vars = {
            "compactdb": BooleanVar(),
            "attr_check": BooleanVar(),
            "attr_fill1": BooleanVar(),
            "attr_fill2": BooleanVar(),
            "corr_fid": BooleanVar(),
            "generalize": BooleanVar(),
            "recalculate_extent": BooleanVar(),
            "remove_identical": BooleanVar(),
            "repair_geometry": BooleanVar()
        }


        self.compactdb = Button(db_section, text="Compact DB", command=lambda: compactDb(self,status_update=None,show_messagebox=True), width=30, bg=colors["light_coral"])
        self.compactdb.grid(row=0, column=3, padx=5, pady=5, sticky=E + W + N + S, columnspan=2)
        Checkbutton(db_section, bg=colors["check_button"],   variable=self.check_vars["compactdb"]).grid(row=0, column=5)

        self.attr_check = Button(db_section, text="Check Attributes", command=lambda: attributeChecker(self), width=30, bg=colors["light_coral"])
        self.attr_check.grid(row=1, column=3, padx=5, pady=5, sticky=E + W + N + S, columnspan=2)
        Checkbutton(db_section,bg=colors["check_button"],   variable=self.check_vars["attr_check"]).grid(row=1, column=5)

        self.Sheet_sc = Label(db_section, text="Choose Mapped Scale", width=30, bg=colors["light_gray"])
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
        self.variable_sc.set(options_sc[5]) # Default value

        self.optionmenu_sc = OptionMenu(db_section, self.variable_sc, *options_sc)
        self.optionmenu_sc.config(bg=colors["white"])
        self.optionmenu_sc.grid(row=2, column=1, padx=5, pady=5, sticky=E + W + N + S,columnspan=1)

        self.attr_fill1 = Button(db_section, text="Fill Ward and Grid (Free)", command=lambda: Fill_Ward_Grid(self, self.variable_sc.get()), width=30, bg=colors["light_coral"])
        self.attr_fill1.grid(row=2, column=3, padx=5, pady=5, sticky=E + W + N + S, columnspan=2)
        Checkbutton(db_section,bg=colors["check_button"],   variable=self.check_vars["attr_fill1"]).grid(row=2, column=5)

        # Create label for District
        self.Dist_code_label = Label(db_section, text="District Code", width=30, bg=colors["light_gray"])
        self.Dist_code_label.grid(row=3, column=0, padx=5, pady=5, sticky=E + W + N + S)

        # Create entry
        self.DistrictCode = Entry(db_section, width=30, bg=colors["white"])
        self.DistrictCode.grid(row=3, column=1, padx=5, pady=5, sticky=E + W + N + S)

        # Create label for VDC
        self.Vdc_code_label = Label(db_section, text="Enter VDC Code", width=30, bg=colors["light_gray"])
        self.Vdc_code_label.grid(row=4, column=0, padx=5, pady=5, sticky=E + W + N + S)

        # Create entry
        self.VDCCode = Entry(db_section, width=30, bg=colors["white"])
        self.VDCCode.grid(row=4, column=1, padx=5, pady=5, sticky=E + W + N + S, columnspan=2)

        self.attr_fill2 = Button(db_section, text="Fill District VDC Code", command=lambda: Fill_VDC_Dist_Code(self, self.DistrictCode.get(), self.VDCCode.get()), width=30, bg=colors["light_coral"])
        self.attr_fill2.grid(row=4, column=3, padx=5, pady=5, sticky=E + W + N + S, columnspan=2)
        Checkbutton(db_section,bg=colors["check_button"],   variable=self.check_vars["attr_fill2"]).grid(row=4, column=5)

        self.corr_fid = Button(db_section, text="Correct FID", command=lambda: Correct_FID(self), width=30, bg=colors["light_coral"])
        self.corr_fid.grid(row=5, column=3, padx=5, pady=5, sticky=E + W + N + S, columnspan=2)
        Checkbutton(db_section,bg=colors["check_button"],   variable=self.check_vars["corr_fid"]).grid(row=5, column=5)

        self.tolerance_label_text = Label(db_section, text="Tolerance(m)", bg=colors["light_gray"])
        self.tolerance_label_text.grid(row=6, column=0, sticky="e", padx=5, pady=2)

        self.tolerance_entry = Entry(db_section, bg=colors["white"])
        self.tolerance_entry.insert(0, "0.2")  # Insert default value
        self.tolerance_entry.grid(row=6, column=1, sticky="w", padx=5, pady=2)

        self.generalize = Button(db_section, text="Generalize", command=lambda: Generalize(self, self.tolerance_entry.get()), width=30, bg=colors["light_coral"])
        self.generalize.grid(row=6, column=3, padx=5, pady=5, sticky=E + W + N + S, columnspan=2)
        Checkbutton(db_section,bg=colors["check_button"],   variable=self.check_vars["generalize"]).grid(row=6, column=5)

        self.recalculate_extent = Button(db_section, text="ReCalculate Extent", command=lambda: recalculate_extent(self), width=30, bg=colors["light_coral"])
        self.recalculate_extent.grid(row=7, column=3, padx=5, pady=5, sticky=E + W + N + S, columnspan=2)
        Checkbutton(db_section,bg=colors["check_button"],   variable=self.check_vars["recalculate_extent"]).grid(row=7, column=5)

        self.remove_identical = Button(db_section, text="Remove Identical Constructions", command=lambda: Remove_Identical_Feature(self), width=30, bg=colors["light_coral"])
        self.remove_identical.grid(row=8, column=3, padx=5, pady=5, sticky=E + W + N + S, columnspan=2)
        Checkbutton(db_section,bg=colors["check_button"],   variable=self.check_vars["remove_identical"]).grid(row=8, column=5)

        self.repair_geometry = Button(db_section, text="Repair Geometry", command=lambda: Repair_Geometry(self), width=30, bg=colors["light_coral"])
        self.repair_geometry.grid(row=9, column=3, padx=5, pady=5, sticky=E + W + N + S, columnspan=2)
        Checkbutton(db_section,bg=colors["check_button"],   variable=self.check_vars["repair_geometry"]).grid(row=9, column=5)

        # Run all checked actions button
        self.run_all_button = Button(db_section, text="Run Checked Actions", command=self.run_checked_actions, width=30, bg=colors["light_green"])
        self.run_all_button.grid(row=10, column=0, padx=5, pady=5, sticky=E + W + N + S, columnspan=6)

        # Add the progress bar
        self.progress = Progressbar(self.master, orient=HORIZONTAL, length=200, mode='determinate')
        self.progress.grid(row=3, column=0, padx=5, pady=5, sticky=E + W + N + S, columnspan=2)

        # Section for extras
        extra_section = LabelFrame(self.master, text="Extras", padx=5, pady=5, bg=colors["light_green"])
        extra_section.grid(row=4, column=0, padx=5, pady=5, sticky=E + W + N + S,columnspan=3)

        self.merge_all = Button(extra_section, text="Merge All", command=lambda: mergeSaexMdbs(self, self.variable_cm.get()), width=30, bg=colors["light_coral"])
        self.merge_all.grid(row=0, column=0, padx=5, pady=5, sticky=E + W + N + S, columnspan=1)

        self.merge_dummy = Button(extra_section, text="Merge Dummy Planning", command=lambda: merge_dummy_planning(self, self.variable_cm.get()), width=30, bg=colors["light_coral"])
        self.merge_dummy.grid(row=0, column=2, padx=5, pady=5, sticky=E + W + N + S, columnspan=1)

        self.identical_parcel = Button(extra_section, text="Identical Parcels", command=self.find_identical_parcels, width=30, bg=colors["light_coral"])
        self.identical_parcel.grid(row=0, column=3, padx=5, pady=5, sticky=E + W + N + S, columnspan=1)

        # Add this to the end of the create_widgets method
        self.status_label = Label(self.master, text="Ready", bg=colors["light_gray"], width=50)
        self.status_label.grid(row=0, column=4, padx=5, pady=5, sticky=E + W + N + S, columnspan=2)

    def run_checked_actions(self):
        """Run all checked actions serially in the order they appear in the UI"""
        action_order = [
            "compactdb",
            "attr_check",
            "attr_fill1",
            "attr_fill2",
            "corr_fid",
            "generalize",
            "recalculate_extent",
            "remove_identical",
            "repair_geometry"
        ]

        checked_actions = [action for action in action_order if self.check_vars[action].get()]

        if not checked_actions:
            tkMessageBox.showinfo("Info", "Please select at least one action to run.")
            return

        total_actions = len(checked_actions)
        progress_step = 100 / total_actions
        current_progress = 0

        for action in checked_actions:
            try:
                # Update status label
                self.update_status("Processing: {}".format(action.replace('_', ' ').title()))

                if action == "compactdb":
                    compactDb(self,self.update_status, show_messagebox=False)
                elif action == "attr_check":
                    attributeChecker(self, self.update_status,show_messagebox=False)
                elif action == "attr_fill1":
                    Fill_Ward_Grid(self, self.variable_sc.get(), self.update_status,show_messagebox=False)
                elif action == "attr_fill2":
                    Fill_VDC_Dist_Code(self, self.DistrictCode.get(), self.VDCCode.get(), self.update_status,show_messagebox=False)
                elif action == "corr_fid":
                    Correct_FID(self.update_status,show_messagebox=False)
                elif action == "generalize":
                    Generalize(self, self.tolerance_entry.get(), self.update_status,show_messagebox=False)
                elif action == "recalculate_extent":
                    recalculate_extent(self, self.update_status,show_messagebox=False)
                elif action == "remove_identical":
                    Remove_Identical_Feature(self, self.update_status,show_messagebox=False)
                elif action == "repair_geometry":
                    Repair_Geometry(self, self.update_status,show_messagebox=False)

                # Update progress bar
                current_progress += progress_step
                self.progress['value'] = current_progress
                self.master.update_idletasks()

            except Exception as e:
                # Show error message if any action fails
                tkMessageBox.showerror("Error", "An error occurred while performing {}: {}".format(action, str(e)))
                break  # Optionally stop the execution if an error occurs

        # Show completion message
        tkMessageBox.showinfo("Info", "All selected actions have been completed.")
        self.update_status("Completed")

    def find_identical_parcels(self):
        result = Find_Identical_Feature(self)
        #display_results(result)

    def browse_folder(self):
        folder_selected = tkFileDialog.askdirectory()
        if folder_selected:  # Check if a folder was selected
            self.directory.delete(0, tk.END)  # Clear the Entry widget
            self.directory.insert(0, folder_selected)  # Insert the selected folder path
            shared_data.directory = folder_selected  # Update shared_data with the selected path

    def load_db(self):
        directory = self.directory.get()
        LoadDb(directory)  # Pass the directory to LoadDb function

        # Update the OptionMenu based on the new central meridian
        if hasattr(shared_data, 'initial_central_meridian'):
            self.set_default_option(shared_data.initial_central_meridian)

    def update_status(self, message):
        """Update the status label with a message."""
        self.status_label.config(text=message)
        self.master.update_idletasks()

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

