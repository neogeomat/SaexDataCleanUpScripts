import os
import subprocess
import tkFont
import tkMessageBox
from Tkinter import *
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
from FixGapsAndOverlaps_saex_mdbs import Fix_Gap_Overlap
from merge_dummy_planning import merge_dummy_planning
from mege_saex_mdb import mergeSaexMdbs
from attribute_check import attributeChecker
from file_filter import FileFilter  # Import the filter class
from filter_dialog import FilterDialog, show_filter_list  # Import the filter dialog
from attributeFill_ward_grid import Fill_Ward_Grid
from attributeFill_VDC_dist_code import Fill_VDC_Dist_Code
from Fill_FID import Correct_FID
from identical_parcels import Find_Identical_Feature
from Change_Parcel_No import Change_parcel_no

psutil_available = True
try:
    import psutil
except ImportError:
    print("psutil not found. Trying to install...")
    try:
        subprocess.call(["python", "-m", "pip", "install", "psutil"])
        import psutil  # Try importing again after installation
    except ImportError:
        psutil_available = False  # If installation fails, disable the button

# Version constant
from shared_data import VERSION



# Define colors
colors = {
    "light_blue": "#9FB3DF",
    "check_button": "#add8e6",
    "light_green": "#90ee90",
    "light_yellow": "#ffffe0",
    "light_coral": "#FF8282",
    "light_pink": "#ffb6c1",
    "light_gray": "#9FB3D0",
    "white": "#ffffff",
    "heading":"#ffe896"
}


class DataCleanup:
    def __init__(self, master):
        self.master = master
        self.master.title("Data Clean Up Tools")
        self.create_widgets()

    def create_widgets(self):
        """Create buttons with light, colorful background colors"""

        # Add version label at top
        version_label = Label(self.master,
                              text="DATA CLEANUP TOOLS - VERSION {}".format(VERSION),
                              font=('Helvetica', 16, 'bold'),
                              bg=colors["heading"],
                              pady=10)
        version_label.grid(row=0, column=0, columnspan=2, sticky="ew")

        # Configuration variables for easy adjustments
        LABEL_WIDTH = 8
        ENTRY_WIDTH = 30
        BUTTON_WIDTH = 10
        PADX = 2
        PADY = 3
        STICKY = E + W + N + S
        SECTION_COLSPAN = 6  # Adjust based on number of columns needed
        LABEL_WIDTH = 20
        OPTIONMENU_WIDTH = 15
        ACTION_BUTTON_WIDTH = 12

        # Section for loading and filtering files - Single horizontal row
        file_section = LabelFrame(self.master,
                                  text="Choose Path and Filter",
                                  padx=PADX,
                                  pady=PADY,
                                  bg=colors["light_blue"])
        file_section.grid(row=1, column=0, padx=PADX, pady=PADY, sticky=STICKY, columnspan=SECTION_COLSPAN)

        # Create widgets with consistent styling
        self.Sheet = Label(file_section,
                           text="Folder:",
                           width=LABEL_WIDTH,
                           bg=colors["light_gray"])
        self.directory = Entry(file_section,
                               width=ENTRY_WIDTH,
                               bg=colors["white"])
        self.browseDb = Button(file_section,
                               text="Browse",
                               command=self.browse_folder,
                               width=BUTTON_WIDTH,
                               bg=colors["light_coral"])
        self.loaddb = Button(file_section,
                             text="Load DB",
                             command=self.load_db,
                             width=BUTTON_WIDTH,
                             bg=colors["light_green"])
        self.filter_button = Button(file_section,
                                    text="Filter",
                                    command=self.open_filter_dialog,
                                    width=BUTTON_WIDTH,
                                    bg=colors["light_coral"])
        self.show_filter = Button(file_section,
                                  text="Show",
                                  command=lambda: show_filter_list(self),
                                  width=BUTTON_WIDTH,
                                  bg=colors["light_coral"])

        # Grid layout - all in one row
        widgets = [
            (self.Sheet, 0),
            (self.directory, 1),
            (self.browseDb, 2),
            (self.loaddb, 3),
            (self.filter_button, 4),
            (self.show_filter, 5)
        ]

        for widget, col in widgets:
            widget.grid(row=0,
                        column=col,
                        padx=PADX,
                        pady=PADY,
                        sticky=STICKY)

        # Section for database operations - Compact horizontal layout
        cm_section = LabelFrame(self.master,
                                text="Replace Whole MDb",
                                padx=PADX,
                                pady=PADY,
                                bg=colors["light_blue"])
        cm_section.grid(row=2, column=0, padx=PADX, pady=PADY, sticky=STICKY, columnspan=2)

        # Central Meridian Selection
        self.Sheet_cm = Label(cm_section,
                              text="Central Meridian:",
                              width=LABEL_WIDTH,
                              bg=colors["light_gray"])
        self.Sheet_cm.grid(row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY)

        options_cm = ["BLANK81.mdb", "BLANK84.mdb", "BLANK87.mdb"]

        self.variable_cm = StringVar(cm_section)
        self.variable_cm.set(options_cm[1])  # Default value

        self.optionmenu_cm = OptionMenu(cm_section, self.variable_cm, *options_cm)
        self.optionmenu_cm.config(bg=colors["white"], width=OPTIONMENU_WIDTH)
        self.optionmenu_cm.grid(row=0, column=1, padx=PADX, pady=PADY, sticky=STICKY)

        self.compactdb = Button(cm_section,
                                text="Replace",
                                command=lambda: replaceMDb(self, self.variable_cm.get()),
                                width=ACTION_BUTTON_WIDTH,
                                bg=colors["light_coral"])
        self.compactdb.grid(row=0, column=2, padx=PADX, pady=PADY, sticky=STICKY)

        # Section for database operations
        db_section = LabelFrame(self.master, text="Apply Cleanup", padx=2, pady=3, bg=colors["light_blue"])
        db_section.grid(row=3, column=0, padx=2, pady=3, sticky=E + W + N + S, columnspan=2)

        self.select_all_var = BooleanVar()
        self.select_all_checkbutton = Checkbutton(db_section, text="Select All", variable=self.select_all_var,
                                                  command=self.toggle_all_checkbuttons, bg=colors["light_green"])
        self.select_all_checkbutton.grid(row=0, column=0, padx=2, pady=3, sticky=W)

        self.run_on_error = BooleanVar()
        self.run_on_error_checkbutton = Checkbutton(db_section, text="Run On Error Files Only", variable=self.run_on_error,
                                                  command=self.select_error_mdbs, bg=colors["light_green"])
        self.run_on_error_checkbutton.grid(row=0, column=1, padx=2, pady=3, sticky=W)


        # Store the checkbutton states
        self.check_vars = {
            "compactdb": BooleanVar(),
            "attr_check": BooleanVar(),
            "attr_fill1": BooleanVar(),
            "attr_fill2": BooleanVar(),
            "corr_fid": BooleanVar(),
            "fix_gap_overlap": BooleanVar(),
            "generalize": BooleanVar(),
            "recalculate_extent": BooleanVar(),
            "remove_identical": BooleanVar(),
            "repair_geometry": BooleanVar(),
            "merge_dummy": BooleanVar()
        }


        self.compactdb = Button(db_section, text="Compact DB", command=lambda: compactDb(self,status_update=None,show_messagebox=True), width=30, bg=colors["light_coral"])
        self.compactdb.grid(row=0, column=3, padx=2, pady=3, sticky=E + W + N + S, columnspan=2)
        Checkbutton(db_section, bg=colors["check_button"],   variable=self.check_vars["compactdb"]).grid(row=0, column=5)

        self.run_on_parcel_0 = BooleanVar()
        self.run_on_parcel_0_check = Checkbutton(db_section, text="Exclude Parcel No 0", variable=self.run_on_parcel_0, bg=colors["light_green"])
        self.run_on_parcel_0_check.grid(row=1, column=1, padx=2, pady=3, sticky=W)


        self.attr_check = Button(db_section, text="Check Attributes", command=lambda: attributeChecker(self,self.run_on_parcel_0.get()), width=30, bg=colors["light_coral"])
        self.attr_check.grid(row=1, column=3, padx=2, pady=3, sticky=E + W + N + S, columnspan=2)
        Checkbutton(db_section,bg=colors["check_button"],   variable=self.check_vars["attr_check"]).grid(row=1, column=5)

        self.Sheet_sc = Label(db_section, text="Choose Mapped Scale", width=30, bg=colors["light_gray"])
        self.Sheet_sc.grid(row=3, column=0, padx=2, pady=3, sticky=E + W + N + S)

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
        self.optionmenu_sc.grid(row=3, column=1, padx=2, pady=3, sticky=E + W + N + S,columnspan=1)

        self.attr_fill1 = Button(db_section, text="Fill Ward and Grid (Free)", command=lambda: Fill_Ward_Grid(self, self.variable_sc.get()), width=30, bg=colors["light_coral"])
        self.attr_fill1.grid(row=3, column=3, padx=2, pady=3, sticky=E + W + N + S, columnspan=2)
        Checkbutton(db_section,bg=colors["check_button"],   variable=self.check_vars["attr_fill1"]).grid(row=3, column=5)

        # Create label for District
        self.Dist_code_label = Label(db_section, text="Enter District Code", width=30, bg=colors["light_gray"])
        self.Dist_code_label.grid(row=4, column=0, padx=2, pady=3, sticky=E + W + N + S)

        # Create entry
        self.DistrictCode = Entry(db_section, width=30, bg=colors["white"])
        self.DistrictCode.grid(row=4, column=1, padx=2, pady=3, sticky=E + W + N + S)

        # Create label for VDC
        self.Vdc_code_label = Label(db_section, text="Enter VDC Code", width=30, bg=colors["light_gray"])
        self.Vdc_code_label.grid(row=5, column=0, padx=2, pady=3, sticky=E + W + N + S)

        # Create entry
        self.VDCCode = Entry(db_section, width=30, bg=colors["white"])
        self.VDCCode.grid(row=5, column=1, padx=2, pady=3, sticky=E + W + N + S, columnspan=2)

        self.attr_fill2 = Button(db_section, text="Fill District VDC Code", command=lambda: Fill_VDC_Dist_Code(self, self.DistrictCode.get(), self.VDCCode.get()), width=30, bg=colors["light_coral"])
        self.attr_fill2.grid(row=5, column=3, padx=2, pady=3, sticky=E + W + N + S, columnspan=2)
        Checkbutton(db_section,bg=colors["check_button"],   variable=self.check_vars["attr_fill2"]).grid(row=5, column=5)

        self.corr_fid = Button(db_section, text="Correct FID", command=lambda: Correct_FID(self), width=30, bg=colors["light_coral"])
        self.corr_fid.grid(row=6, column=3, padx=2, pady=3, sticky=E + W + N + S, columnspan=2)
        Checkbutton(db_section,bg=colors["check_button"],   variable=self.check_vars["corr_fid"]).grid(row=6, column=5)

        self.fix_gap_overlap = Button(db_section, text="Fix Gap and Overlap", command=lambda: Fix_Gap_Overlap(self,self.variable_cm.get()), width=30, bg=colors["light_coral"])
        self.fix_gap_overlap.grid(row=7, column=3, padx=2, pady=3, sticky=E + W + N + S, columnspan=2)
        Checkbutton(db_section,bg=colors["check_button"],   variable=self.check_vars["fix_gap_overlap"]).grid(row=7, column=5)

        self.tolerance_label_text = Label(db_section, text="Tolerance(m)", bg=colors["light_gray"])
        self.tolerance_label_text.grid(row=8, column=0, sticky="e", padx=2, pady=3)

        self.tolerance_entry = Entry(db_section, bg=colors["white"])
        self.tolerance_entry.insert(0, "0.2")  # Insert default value
        self.tolerance_entry.grid(row=8, column=1, sticky="w", padx=2, pady=3)

        self.generalize = Button(db_section, text="Generalize", command=lambda: Generalize(self, self.tolerance_entry.get(),self.variable_cm.get()), width=30, bg=colors["light_coral"])
        self.generalize.grid(row=8, column=3, padx=2, pady=3, sticky=E + W + N + S, columnspan=2)
        Checkbutton(db_section,bg=colors["check_button"],   variable=self.check_vars["generalize"]).grid(row=8, column=5)

        self.recalculate_extent = Button(db_section, text="ReCalculate Extent", command=lambda: recalculate_extent(self), width=30, bg=colors["light_coral"])
        self.recalculate_extent.grid(row=9, column=3, padx=2, pady=3, sticky=E + W + N + S, columnspan=2)
        Checkbutton(db_section,bg=colors["check_button"],   variable=self.check_vars["recalculate_extent"]).grid(row=9, column=5)

        self.remove_identical = Button(db_section, text="Remove Identical Constructions & Segments",font = (tkFont.Font(size=8)) , command=lambda: Remove_Identical_Feature(self), width=30, bg=colors["light_coral"])
        self.remove_identical.grid(row=10, column=3, padx=2, pady=3, sticky=E + W + N + S, columnspan=2)
        Checkbutton(db_section,bg=colors["check_button"],   variable=self.check_vars["remove_identical"]).grid(row=10, column=5)

        self.repair_geometry = Button(db_section, text="Repair Geometry", command=lambda: Repair_Geometry(self), width=30, bg=colors["light_coral"])
        self.repair_geometry.grid(row=11, column=3, padx=2, pady=3, sticky=E + W + N + S, columnspan=2)
        Checkbutton(db_section,bg=colors["check_button"],   variable=self.check_vars["repair_geometry"]).grid(row=11, column=5)

        self.merge_dummy = Button(db_section, text="Merge Dummy Planning", command=lambda: merge_dummy_planning(self, self.variable_cm.get()), width=30, bg=colors["light_coral"])
        self.merge_dummy.grid(row=2, column=3, padx=2, pady=3, sticky=E + W + N + S, columnspan=2)
        Checkbutton(db_section,bg=colors["check_button"],   variable=self.check_vars["merge_dummy"]).grid(row=2, column=5)

        # Run all checked actions button
        self.run_all_button = Button(db_section, text="Run Checked Actions", command=self.run_checked_actions, width=30, bg=colors["light_green"])
        self.run_all_button.grid(row=12, column=0, padx=2, pady=3, sticky=E + W + N + S, columnspan=6)

        # Add the progress bar
        self.progress = Progressbar(self.master, orient=HORIZONTAL, length=200, mode='determinate')
        self.progress.grid(row=4, column=0, padx=2, pady=3, sticky=E + W + N + S, columnspan=2)

        # Section for extras
        extra_section = LabelFrame(self.master, text="Extras", padx=2, pady=3, bg=colors["light_green"])
        extra_section.grid(row=5, column=0, padx=2, pady=3, sticky=E + W + N + S,columnspan=2)

        self.merge_all = Button(extra_section, text="Merge All", command=lambda: mergeSaexMdbs(self, self.variable_cm.get()), width=30, bg=colors["light_coral"])
        self.merge_all.grid(row=0, column=0, padx=2, pady=3, sticky=E + W + N + S, columnspan=1)

        self.identical_parcel = Button(extra_section, text="Identical Parcels", command=self.find_identical_parcels, width=30, bg=colors["light_coral"])
        self.identical_parcel.grid(row=0, column=2, padx=2, pady=3, sticky=E + W + N + S, columnspan=1)
        if psutil_available:
            self.move_data = Button(extra_section, text="Move Data", command=self.move_data, width=30, bg=colors["light_coral"])
            self.move_data.grid(row=0, column=3, padx=2, pady=3, sticky=E + W + N + S, columnspan=1)
        else:
            print("psutil installation failed. 'Move Data' button is disabled.")


        self.p_no_label = Label(extra_section, text="Enter Max Parcel No \n to Change to zero", width=30, bg=colors["light_gray"])
        self.p_no_label.grid(row=1, column=0, padx=2, pady=3, sticky=E + W + N + S)

        # Create entry
        self.max_p_no = Entry(extra_section, width=30, bg=colors["white"])
        self.max_p_no.grid(row=1, column=2, padx=2, pady=3, sticky=E + W + N + S, columnspan=2)
        self.max_p_no.insert(0,"9999")

        self.change_p_no = Button(extra_section, text="Change Parcel No to 0", command=lambda: self.change_parcel_no(self.max_p_no.get()), width=30, bg=colors["light_coral"])
        self.change_p_no.grid(row=1, column=3, padx=2, pady=3, sticky=E + W + N + S, columnspan=1)

        # Section for status updates
        self.status_section = LabelFrame(self.master, text="Status", padx=2, pady=3, bg=colors["light_blue"])
        self.status_section.grid(row=6, column=0, padx=2, pady=3, sticky=E + W + N + S, columnspan=2)

        self.status_label = Label(self.status_section, text="", bg=colors["light_yellow"], anchor='w')
        self.status_label.grid(row=0, column=0, padx=2, pady=3, sticky=W, columnspan=6)
        self.hide_status()  # Hide the status_label initially

    def select_error_mdbs(self):
        mdb_files = shared_data.filtered_mdb_files  # Assuming this contains the list of .mdb file paths
        error_mdbs = []

        for mdb_path in mdb_files:
            # Get the directory and base file name (without extension) of the .mdb file
            directory, mdb_filename = os.path.split(mdb_path)
            base_filename = os.path.splitext(mdb_filename)[0]

            # Check if any .csv file in the directory contains the base file name
            for file_name in os.listdir(directory):
                if file_name.endswith('.csv') and base_filename in file_name:
                    error_mdbs.append(mdb_path)
                    break

        shared_data.filtered_mdb_files = error_mdbs

    def toggle_all_checkbuttons(self):
        """Toggle all checkbuttons based on the state of the master checkbutton"""
        for var in self.check_vars.values():
            var.set(self.select_all_var.get())

    def run_checked_actions(self):
        """Run all checked actions serially in the order they appear in the UI"""
        action_order = [
            "compactdb",
            "attr_check",
            "merge_dummy",
            "attr_fill1",
            "attr_fill2",
            "corr_fid",
            "fix_gap_overlap",
            "generalize",
            "recalculate_extent",
            "remove_identical",
            "repair_geometry"
        ]

        action_buttons = {
            "compactdb": self.compactdb,
            "attr_check": self.attr_check,
            "merge_dummy": self.merge_dummy,
            "attr_fill1": self.attr_fill1,
            "attr_fill2": self.attr_fill2,
            "corr_fid": self.corr_fid,
            "fix_gap_overlap": self.fix_gap_overlap,
            "generalize": self.generalize,
            "recalculate_extent": self.recalculate_extent,
            "remove_identical": self.remove_identical,
            "repair_geometry": self.repair_geometry
        }

        # Mapping of action keys to user-friendly display names
        action_display_names = {
            "compactdb": "Compact database",
            "merge_dummy": "Merge Dummy Plannings",
            "attr_check": "Attribute check",
            "attr_fill1": "Fill Ward Grid",
            "attr_fill2": "Fill VDC/District Code",
            "corr_fid": "Correct Parcel ID",
            "fix_gap_overlap": "Fix Gap And Overlap",
            "generalize": "Generalize",
            "recalculate_extent": "Recalculate extent",
            "remove_identical": "Remove identical const features",
            "repair_geometry": "Repair geometry"
        }

        checked_actions = [action for action in action_order if self.check_vars[action].get()]

        if not checked_actions:
            tkMessageBox.showinfo("Info", "Please select at least one action to run.")
            return

        total_actions = len(checked_actions)
        self.progress["maximum"] = total_actions

        for i, action in enumerate(checked_actions, start=1):
            #update_status = "show"
            try:
                display_name = action_display_names.get(action, action.replace('_', ' ').capitalize())
                #self.progress["value"] = i
                # Show the status_label and update its text
                self.status_label.pack(side="right", fill="x")  # Adjust as needed for your layout
                self.status_label.config(text="Running {}... ({}/{})".format(display_name, i, total_actions))
                self.master.update_idletasks()

                button = action_buttons.get(action)
                if button:
                    original_color = self.update_button_color(button, "spring green")  # Change to a color (e.g., tomato)
                    self.master.update_idletasks()

                def progress_callback(current, total):
                    """Function to update progress bar from action functions"""
                    # Ensure float division
                    progress_fraction = current / float(len(shared_data.filtered_mdb_files))
                    self.progress["value"] = (i - 1) + progress_fraction * (1.0 / total_actions)
                    self.master.update_idletasks()


                if action == "compactdb":
                    compactDb(self, self.update_status, show_messagebox=False,update_progress=progress_callback)
                elif action == "attr_check":
                    attributeChecker(self,self.run_on_parcel_0.get(), self.update_status, show_messagebox=False,update_progress=progress_callback)
                elif action == "attr_fill1":
                    Fill_Ward_Grid(self, self.variable_sc.get(), self.update_status, show_messagebox=False,update_progress=progress_callback)
                elif action == "attr_fill2":
                    Fill_VDC_Dist_Code(self, self.DistrictCode.get(), self.VDCCode.get(), self.update_status,
                                       show_messagebox=False,update_progress=progress_callback)
                elif action == "corr_fid":
                    Correct_FID(self,self.update_status, show_messagebox=False,update_progress=progress_callback)
                elif action == "fix_gap_overlap":
                    Fix_Gap_Overlap(self,self.variable_cm.get(),self.update_status, show_messagebox=False,update_progress=progress_callback)
                elif action == "generalize":
                    Generalize(self, self.tolerance_entry.get(),self.variable_cm.get(), self.update_status, show_messagebox=False,update_progress=progress_callback)
                elif action == "recalculate_extent":
                    recalculate_extent(self, self.update_status, show_messagebox=False,update_progress=progress_callback)
                elif action == "remove_identical":
                    Remove_Identical_Feature(self, self.update_status, show_messagebox=False,update_progress=progress_callback)
                elif action == "repair_geometry":
                    Repair_Geometry(self, self.update_status, show_messagebox=False,update_progress=progress_callback)
                elif action == "merge_dummy":
                    merge_dummy_planning(self,self.variable_cm.get(), self.update_status, show_messagebox=False,update_progress=progress_callback)

                if button:
                    self.update_button_color(button, original_color)  # Revert to the original color

            except Exception as e:
                tkMessageBox.showerror("Error", "An error occurred while running {}: {}".format(display_name, str(e)))
                return

        # Final update and completion message
        self.status_label.config(text="All selected actions completed!")
        tkMessageBox.showinfo("Info", "All selected actions have been successfully completed.")

        # Hide the status_section after all actions are complete
        self.status_section.pack_forget()

    def find_identical_parcels(self):
        result = Find_Identical_Feature(self)

    def is_script_running(self,script_name):
        """Check if a script is already running."""
        for proc in psutil.process_iter():
            try:
                cmdline = proc.cmdline()  # Get command line arguments
                if cmdline and script_name in " ".join(cmdline):
                    return True  # Script is already running
            except:
                pass
        return False

    def move_data(self):
        script_name = "Move_data.py"
        if not self.is_script_running(script_name):
            subprocess.Popen(["python", script_name])
        else:
            print("{} is already running.".format(script_name))

    def change_parcel_no(self, parcel_no_str):
        max_parcel_no=int(parcel_no_str)
        if not isinstance(max_parcel_no, int):
            tkMessageBox.showerror("Invalid Input", "max_parcel_no must be an integer.")
            return None  # Exit the function gracefully
        Change_parcel_no(self,max_parcel_no)

    def browse_folder(self):
        folder_selected = tkFileDialog.askdirectory()
        if folder_selected:  # Check if a folder was selected
            self.directory.delete(0, END)  # Clear the Entry widget
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

    def show_status(self, message):
        self.status_label.config(text=message)
        self.status_label.grid(row=0, column=0, padx=2, pady=3, sticky=W)
        self.master.update_idletasks()

    def hide_status(self):
        self.status_label.grid_forget()


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

    def update_button_color(self, button, color):
        """Change the button color."""
        original_color = button.cget('background')
        button.config(bg=color)
        return original_color