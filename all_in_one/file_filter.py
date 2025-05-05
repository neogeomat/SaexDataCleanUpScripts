import os
from tkinter import Tk, filedialog, Listbox, MULTIPLE, Button, Frame, messagebox

class FileFilter:
    def __init__(self, files):
        self.files = files

    def filter_by_folder(self, folders):
        """Filter files to include only those within the specified folders."""
        """Filter files to include only those within the specified folders."""
        if not folders:
            return self.files

        # Normalize folder paths
        folders_normalized  = [os.path.normpath(folder) for folder in folders]

        return [f for f in self.files
                if any(commonpath([os.path.normpath(f), folder]) == folder for folder in folders_normalized)]

    def select_folders(self):
        """Open a dialog to select multiple folders."""
        # Hide the main window temporarily
        self.root.withdraw()

        # Ask for directory selection
        folders = filedialog.askdirectory(
            title="Select folders to filter by",
            mustexist=True
        )

        # Show the main window again
        self.root.deiconify()

        # Return as list (askdirectory returns a single path)
        return [folders] if folders else []

    def filter_by_name(self, name_filters, filtered_files, use_path=False, logic_type="Or"):
        filtered_files_list = []

        # Convert all filters to lowercase
        name_filters_lower = [filter.lower() for filter in name_filters]

        for f in filtered_files:
            # Get basename and full path, convert to lowercase
            basename = os.path.basename(f).lower()
            full_path = f.lower()

            # Check if using full path or just the filename
            search_target = full_path if use_path else basename

            # Apply the selected logic type
            if logic_type == "Or":
                # "Or" logic: if any substring matches
                if any(name_filter in search_target for name_filter in name_filters_lower):
                    filtered_files_list.append(f)
            else:  # "And" logic: all substrings must match
                if all(name_filter in search_target for name_filter in name_filters_lower):
                    filtered_files_list.append(f)

        return filtered_files_list

    def display_results(self, filtered_files):
        """Print the filtered files and their count."""
        print("Filtered Files:")
        for file in filtered_files:
            print(file)
        print("Number of files: {len(filtered_files)}")

    def show_folder_selection_dialog(self):
        """Display a GUI for folder selection and filtering."""
        frame = Frame(self.root)
        frame.pack(padx=10, pady=10)

        # Button to select folders
        select_btn = Button(frame, text="Select Folders", command=self.run_filter_process)
        select_btn.pack(pady=5)

        self.root.mainloop()

    def run_filter_process(self):
        """Handle the complete filtering process."""
        # Get selected folders
        folders = self.select_folders()
        if not folders:
            messagebox.showinfo("Info", "No folders selected. Showing all files.")
            filtered_files = self.files
        else:
            # Filter by folders
            filtered_files = self.filter_by_folder(folders)

        # Display results (you could modify this to show in GUI)
        self.display_results(filtered_files)

        # Ask if user wants to filter by name
        if messagebox.askyesno("Continue", "Do you want to filter by name?"):
            self.show_name_filter_dialog(filtered_files)

    def show_name_filter_dialog(self, files_to_filter):
        """Show dialog for name filtering (to be implemented)"""
        # You would implement similar GUI elements for name filtering
        pass


import os

def commonpath(paths):
    """Return the common path prefix for a list of paths."""
    if not paths:
        return ''
    # Normalize paths
    paths = [os.path.abspath(p) for p in paths]
    # Split each path into components
    split_paths = [p.split(os.sep) for p in paths]
    # Find common components
    common_components = []
    for components in zip(*split_paths):
        if len(set(components)) == 1:
            common_components.append(components[0])
        else:
            break
    return os.sep.join(common_components)
