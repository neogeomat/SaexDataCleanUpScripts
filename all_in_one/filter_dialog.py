import os
import Tkinter as tk
import tkMessageBox
import traceback
from Tkinter import Toplevel, StringVar, OptionMenu

import shared_data
from file_filter import FileFilter

import tkinter as tk
from tkinter import Toplevel, Scrollbar, Listbox, messagebox
import shared_data
from LoadDb import getCentralMeridian

class FilterDialog(Toplevel):
    previous_options = None  # Class variable to store previous options
    previous_mdb_list = None  # Class variable to store the previous mdb list


    def __init__(self, master, file_filter, directory, current_mdb_list):
        Toplevel.__init__(self, master)
        self.file_filter = file_filter or FileFilter(current_mdb_list)  # Ensure we always have a filter
        self.directory = directory  # Directory path passed from the main application
        self.current_mdb_list = current_mdb_list  # Store the current list
        self.title("Filter Options")
        self.create_widgets()
        self.populate_folder_list()

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

        # Add this after the other filter options
        self.ignore_frame = tk.LabelFrame(self, text="Ignore Files Containing")
        self.ignore_frame.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

        # Predefined patterns
        self.predefined_patterns = ["file", "merge"]
        self.ignore_vars = {}

        for i, pattern in enumerate(self.predefined_patterns):
            self.ignore_vars[pattern] = tk.BooleanVar()
            cb = tk.Checkbutton(
                self.ignore_frame,
                text=pattern,
                variable=self.ignore_vars[pattern]
            )
            cb.grid(row=0, column=i, padx=5, sticky='w')

        # Custom pattern entry
        self.custom_ignore_label = tk.Label(self.ignore_frame, text="Custom:")
        self.custom_ignore_label.grid(row=1, column=0, padx=5, sticky='e')

        self.custom_ignore_entry = tk.Entry(self.ignore_frame, width=30)
        self.custom_ignore_entry.grid(row=1, column=1, columnspan=3, padx=5, sticky='ew')

    def restore_previous_options(self):
        """Restore the previous filter options if available."""
        self.create_widgets()
        self.folder_var.set(FilterDialog.previous_options['folder'])
        self.name_entry.insert(0, FilterDialog.previous_options['name_filter'])
        self.filter_type_var.set(FilterDialog.previous_options['filter_type'])
        self.logic_type_var.set(FilterDialog.previous_options['logic_type'])

        # Restore ignore patterns
        for pattern, var in self.ignore_vars.items():
            var.set(FilterDialog.previous_options['ignore_patterns'].get(pattern, False))
        self.custom_ignore_entry.insert(0, FilterDialog.previous_options['custom_ignore'])


    def save_filter_options(self):
        """Save the current filter options."""
        FilterDialog.previous_options = {
            'folder': self.folder_var.get(),
            'name_filter': self.name_entry.get().strip(),
            'filter_type': self.filter_type_var.get(),
            'logic_type': self.logic_type_var.get(),
            'ignore_patterns': {k: v.get() for k, v in self.ignore_vars.items()},
            'custom_ignore': self.custom_ignore_entry.get().strip()
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
        """Fixed folder dropdown population"""
        # Get sorted folders and add default option
        folders = self.get_sorted_folders()
        folder_options = ["Select a folder"] + folders

        # Clear existing menu
        menu = self.folder_menu['menu']
        menu.delete(0, 'end')

        # Add all options
        for folder in folder_options:
            menu.add_command(
                label=folder,
                command=lambda f=folder: self.folder_var.set(f)
            )

        # Set default selection
        self.folder_var.set("Select a folder")


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
        try:
            # Get filter values with proper defaults
            selected_folder = self.folder_var.get()
            name_filter_input = self.name_entry.get().strip()

            # Skip folder filtering if none selected
            filtered_files = self.current_mdb_list if selected_folder == "Select a folder" \
                else self.file_filter.filter_by_folder([selected_folder])

            # Debug print
            print("After folder filtering: {} files".format(len(filtered_files)))

            # Name filtering
            if name_filter_input:
                name_filters = [f.strip() for f in name_filter_input.split(',') if f.strip()]
                filtered_files = self.file_filter.filter_by_name(
                    name_filters,
                    filtered_files,
                    use_path=(self.filter_type_var.get() == "Full Path"),
                    logic_type=self.logic_type_var.get()
                )
                print("After name filtering: {} files".format(len(filtered_files)))

            # Ignore patterns
            ignore_patterns = []
            for pattern, var in self.ignore_vars.items():
                if var.get():
                    ignore_patterns.append(pattern)
            custom_pattern = self.custom_ignore_entry.get().strip()
            if custom_pattern:
                ignore_patterns.append(custom_pattern)

            if ignore_patterns:
                filtered_files = self.file_filter.ignore_files_with_patterns(filtered_files, ignore_patterns)
                print("After ignore patterns: {} files".format(len(filtered_files)))


            shared_data.filtered_mdb_files = filtered_files
            print("Final filtered files: {}".format(len(filtered_files)))

            if filtered_files:
                shared_data.initial_central_meridian = getCentralMeridian(filtered_files[0])
            else:
                messagebox.showinfo("No Results", "No files matched your filter criteria.")

        except Exception as e:
            messagebox.showerror("Filter Error", str(e))
            print("Filter error: {}".format(traceback.format_exc()))
        finally:
            self.destroy()

    def is_subpath(self, path, parent_path):
        """Check if path is within parent_path (Python 2.7 compatible)"""
        path = os.path.normpath(path)
        parent_path = os.path.normpath(parent_path)
        return os.path.commonprefix([path, parent_path]) == parent_path

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
