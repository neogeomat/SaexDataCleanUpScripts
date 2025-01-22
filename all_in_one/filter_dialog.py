import os
import Tkinter as tk
import tkMessageBox
from Tkinter import Toplevel, StringVar, OptionMenu

import shared_data
from file_filter import FileFilter

import tkinter as tk
from tkinter import Toplevel, Scrollbar, Listbox
import shared_data
from LoadDb import getCentralMeridian

class FilterDialog(Toplevel):
    previous_options = None  # Class variable to store previous options
    previous_mdb_list = None  # Class variable to store the previous mdb list


    def __init__(self, master, file_filter, directory, current_mdb_list):
        Toplevel.__init__(self, master)
        self.file_filter = file_filter
        self.directory = directory  # Directory path passed from the main application
        self.title("Filter Options")

        # Check if the current mdb_list is unchanged from the previous one
        if FilterDialog.previous_mdb_list == current_mdb_list and FilterDialog.previous_options:
            self.restore_previous_options()
        else:
            self.create_widgets()
        self.populate_folder_list()  # Populate the folder list

    def create_widgets(self):
        # Folder filter using dropdown menu
        self.folder_label = tk.Label(self, text="Filter by Folder:")
        self.folder_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')

        self.folder_var = StringVar()
        self.folder_var.set("Select a folder")  # Default value

        self.folder_menu = OptionMenu(self, self.folder_var, *self.get_sorted_folders())
        self.folder_menu.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='w')

        # Name filter
        self.name_label = tk.Label(self, text="Filter by Name (substring):")
        self.name_label.grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.name_entry = tk.Entry(self, width=50)
        self.name_entry.grid(row=2, column=1, padx=5, pady=5)

        # Filter type selection
        self.filter_type_label = tk.Label(self, text="Filter Type:")
        self.filter_type_label.grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.filter_type_var = StringVar()
        self.filter_type_var.set("Filename")  # Default value

        self.filter_type_menu = OptionMenu(self, self.filter_type_var, "Filename", "Full Path")
        self.filter_type_menu.grid(row=3, column=1, padx=5, pady=5, sticky='w')

        # Substring logic selection (And/Or)
        self.logic_type_label = tk.Label(self, text="Substring Logic:")
        self.logic_type_label.grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.logic_type_var = StringVar()
        self.logic_type_var.set("Or")  # Default value

        self.logic_type_menu = OptionMenu(self, self.logic_type_var, "Or", "And")
        self.logic_type_menu.grid(row=4, column=1, padx=5, pady=5, sticky='w')


        # Apply button
        self.apply_button = tk.Button(self, text="Apply Filters", command=self.apply_filters)
        self.apply_button.grid(row=4, column=1, padx=5, pady=5, sticky='e')

        # Match type selection (Correct/Incorrect)
        self.match_type_label = tk.Label(self, text="Match Type:")
        self.match_type_label.grid(row=5, column=0, padx=5, pady=5, sticky='w')

        self.match_type_var = StringVar()
        self.match_type_var.set("Correct Matches")  # Default value

        self.match_type_menu = OptionMenu(self, self.match_type_var, "Correct Matches", "Incorrect Matches")
        self.match_type_menu.grid(row=5, column=1, padx=5, pady=5, sticky='w')

    def restore_previous_options(self):
        """Restore the previous filter options if available."""
        self.create_widgets()
        self.folder_var.set(FilterDialog.previous_options['folder'])
        self.name_entry.insert(0, FilterDialog.previous_options['name_filter'])
        self.filter_type_var.set(FilterDialog.previous_options['filter_type'])
        self.logic_type_var.set(FilterDialog.previous_options['logic_type'])

    def save_filter_options(self):
        """Save the current filter options."""
        FilterDialog.previous_options = {
            'folder': self.folder_var.get(),
            'name_filter': self.name_entry.get().strip(),
            'filter_type': self.filter_type_var.get(),
            'logic_type': self.logic_type_var.get(),
        }


    def get_sorted_folders(self):
        """Retrieve and sort all folders that contain .mdb files"""
        folders = self.get_folders_from_directory()

        # Separate top-level folders from subfolders
        top_level_folders = [folder for folder in folders if os.path.dirname(folder) == self.directory]
        subfolders = [folder for folder in folders if os.path.dirname(folder) != self.directory]

        # Sort subfolders by their depth in the hierarchy (deeper folders will come later)
        subfolders.sort(key=lambda x: x.count(os.sep))

        # Combine top-level folders and sorted subfolders
        sorted_folders = top_level_folders + subfolders
        return sorted_folders

    def populate_folder_list(self):
        """Populate the dropdown menu with folders that contain .mdb files"""
        folders = self.get_sorted_folders()  # Get sorted folders
        self.folder_var.set("Select a folder")  # Reset to default
        self.folder_menu["menu"].delete(0, "end")  # Clear the existing menu items
        for folder in folders:
            self.folder_menu["menu"].add_command(
                label=folder,
                command=lambda f=folder: self.folder_var.set(f)
            )
    def get_folders_from_directory(self):
        """Retrieve folders that contain .mdb files directly or in their subfolders."""
        folders_with_mdb_files = set()

        for root, dirs, files in os.walk(self.directory):
            # Check if the current directory contains any .mdb files
            if any(file.endswith('.mdb') for file in files):
                folders_with_mdb_files.add(root)

            # Check subdirectories
            for subdir in dirs:
                subdir_path = os.path.join(root, subdir)
                # Traverse subdirectory
                for subroot, _, subfiles in os.walk(subdir_path):
                    if any(file.endswith('.mdb') for file in subfiles):
                        folders_with_mdb_files.add(root)  # Add parent directory if subdirectory contains .mdb files
                        break  # No need to continue if we already found .mdb files in subdirectory

        return sorted(folders_with_mdb_files)

    def apply_filters(self):
        selected_folder = self.folder_var.get()
        name_filter_input = self.name_entry.get().strip()
        filter_type = self.filter_type_var.get()
        logic_type = self.logic_type_var.get()
        match_type = self.match_type_var.get()

        # Save the filter options before applying the filter
        self.save_filter_options()

        # Save the current mdb_list for comparison in future instances
        FilterDialog.previous_mdb_list = shared_data.mdb_files

        # Split the name_filter_input by commas and strip extra spaces
        name_filters = [filter.strip() for filter in name_filter_input.split(',')]

        # Retrieve all .mdb files from the directory
        all_mdb_files = shared_data.mdb_files
        file_filter = FileFilter(all_mdb_files)

        # Filter by folder first
        filtered_by_folder = file_filter.filter_by_folder([selected_folder])

        # Apply filter based on filter type and logic type
        if match_type == "Correct Matches":
            shared_data.filtered_mdb_files = file_filter.filter_by_name(
                name_filters, filtered_by_folder, use_path=(filter_type == "Full Path"), logic_type=logic_type
            )
        else:  # Incorrect Matches
            all_filtered = file_filter.filter_by_name(
                name_filters, filtered_by_folder, use_path=(filter_type == "Full Path"), logic_type=logic_type
            )
            shared_data.filtered_mdb_files = [file for file in filtered_by_folder if file not in all_filtered]

        for mdb in shared_data.filtered_mdb_files:
            shared_data.initial_central_meridian = getCentralMeridian(mdb)
            break

        self.destroy()

def show_filter_list(self):
    # Create a new top-level window
    top = Toplevel(self.master)
    top.title("Filtered Files")

    # Create a frame for the listbox and scrollbar
    frame = tk.Frame(top)
    frame.pack(fill=tk.BOTH, expand=True)

    # Create a scrollbar
    scrollbar = Scrollbar(frame, orient=tk.VERTICAL)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Create a listbox with the scrollbar
    listbox = Listbox(frame, yscrollcommand=scrollbar.set, width=80, height=20)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Configure the scrollbar
    scrollbar.config(command=listbox.yview)

    # Insert the filtered file list into the listbox
    for file in shared_data.filtered_mdb_files:
        listbox.insert(tk.END, file)

    # Show the total count
    count_label = tk.Label(top, text="Total Count: "+ str(len(shared_data.filtered_mdb_files)))
    count_label.pack(pady=10)
