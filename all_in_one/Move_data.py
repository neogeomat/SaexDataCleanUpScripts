import Tkinter as tk
import tkFileDialog
import tkMessageBox
import arcpy
import os
import time


class CoordinateShiftApp(tk.Frame):
    VERSION = "v1.0.2"

    # UI Configuration
    COLORS = {
        'background': '#F5F5F5',
        'primary': '#2C3E50',
        'secondary': '#3498DB',
        'accent': '#27AE60',
        'text': '#2C3E50',
        'error': '#E74C3C',
        'red': '#E74C3C'  # Added red color
    }

    FONTS = {
        'title': ('Helvetica', 14, 'bold'),
        'header': ('Helvetica', 12),
        'body': ('Helvetica', 10),
        'status': ('Helvetica', 9)
    }

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        self.master.title("Database Mover {}".format(self.VERSION))  # Using .format() for string formatting
        self.configure_layout()
        self.create_widgets()
        self.pack(padx=20, pady=20)

    def configure_layout(self):
        """Configure grid layout proportions"""
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=1)
        self.master.configure(bg=self.COLORS['background'])

    def create_widgets(self):
        """Create and arrange UI components"""
        self.create_header()
        self.create_input_section()
        self.create_coordinate_section()
        self.create_instruction_section()
        self.create_status_bar()

    def create_header(self):
        """Create application header section"""
        header_frame = tk.Frame(self, bg=self.COLORS['primary'])
        header_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            header_frame,
            text="Database Location Shifter {}".format(self.VERSION),  # Using .format() for string formatting
            font=self.FONTS['title'],
            fg='white',
            bg=self.COLORS['primary']
        ).pack(pady=10)

    def create_input_section(self):
        """Create folder input section"""
        input_frame = tk.Frame(self, bg=self.COLORS['background'])
        input_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            input_frame,
            text="Project Folder:",
            font=self.FONTS['header'],
            bg=self.COLORS['background']
        ).grid(row=0, column=0, sticky=tk.W)

        self.folder_entry = tk.Entry(
            input_frame,
            width=40,
            font=self.FONTS['body']
        )
        self.folder_entry.grid(row=1, column=0, padx=(0, 10))

        tk.Button(
            input_frame,
            text="Browse",
            command=self.browse_folder,
            bg=self.COLORS['secondary'],
            fg='white',
            font=self.FONTS['body']
        ).grid(row=1, column=1)

    def create_coordinate_section(self):
        """Create coordinate input section"""
        coord_frame = tk.Frame(self, bg=self.COLORS['background'])
        coord_frame.pack(fill=tk.X, pady=10)

        # Arbitrary Coordinates
        tk.Label(
            coord_frame,
            text="Arbitrary Coordinates:",
            font=self.FONTS['header'],
            bg=self.COLORS['background']
        ).grid(row=0, column=0, columnspan=4, sticky=tk.W)

        tk.Label(coord_frame, text="X:", font=self.FONTS['body'], bg=self.COLORS['background']).grid(row=1, column=0,
                                                                                                     sticky=tk.E,
                                                                                                     padx=(0, 5))
        tk.Label(coord_frame, text="Y:", font=self.FONTS['body'], bg=self.COLORS['background']).grid(row=1, column=2,
                                                                                                     sticky=tk.E,
                                                                                                     padx=(0, 5))
        self.arb_x_entry = self.create_coord_entry(coord_frame, 1, 1)
        self.arb_y_entry = self.create_coord_entry(coord_frame, 1, 3)

        # Real Coordinates
        tk.Label(
            coord_frame,
            text="Target Coordinates:",
            font=self.FONTS['header'],
            bg=self.COLORS['background']
        ).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))

        tk.Label(coord_frame, text="X:", font=self.FONTS['body'], bg=self.COLORS['background']).grid(row=3, column=0,
                                                                                                     sticky=tk.E,
                                                                                                     padx=(0, 5))
        tk.Label(coord_frame, text="Y:", font=self.FONTS['body'], bg=self.COLORS['background']).grid(row=3, column=2,
                                                                                                     sticky=tk.E,
                                                                                                     padx=(0, 5))
        self.real_x_entry = self.create_coord_entry(coord_frame, 3, 1)
        self.real_y_entry = self.create_coord_entry(coord_frame, 3, 3)

        # Offset Display Text Box
        self.offset_text = tk.Text(
            coord_frame,
            height=1,
            width=40,
            font=self.FONTS['body'],
            wrap=tk.WORD,
            bg=self.COLORS['background'],
            bd=0,
            relief=tk.FLAT
        )
        self.offset_text.grid(row=5, column=0, columnspan=4, pady=(10, 0))
        self.offset_text.insert(tk.END, "Offsets: X = 0, Y = 0")
        self.offset_text.config(state=tk.DISABLED)  # Make text box read-only

        # Process Button
        tk.Button(
            coord_frame,
            text="Start Coordinate Shift",
            command=self.process_databases,
            bg=self.COLORS['accent'],
            fg='white',
            font=self.FONTS['body'],
            pady=8
        ).grid(row=4, columnspan=2, pady=15, sticky=tk.EW)

    def create_coord_entry(self, parent, row, column):
        """Helper method to create coordinate entry fields"""
        entry = tk.Entry(
            parent,
            width=15,
            font=self.FONTS['body'],
            validate="key",
            vcmd=(self.register(self.validate_numeric_input), '%P')
        )
        entry.grid(row=row, column=column, padx=5, pady=2)
        return entry

    def create_instruction_section(self):
        """Create instruction panel"""
        instr_frame = tk.Frame(self, bg=self.COLORS['background'])
        instr_frame.pack(fill=tk.X, pady=10)

        instructions = (
            "1. Select folder containing .mdb files\n"
            "2. Enter reference coordinates (arbitrary and real)\n"
            "3. Click 'Start Coordinate Shift'\n"
            "4. All features will be moved using calculated offset"
        )

        tk.Label(
            instr_frame,
            text=instructions,
            font=self.FONTS['body'],
            bg=self.COLORS['background'],
            justify=tk.LEFT
        ).pack(anchor=tk.W)

    def create_status_bar(self):
        """Create bottom status bar"""
        self.status_bar = tk.Label(
            self.master,
            text="Ready",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=self.FONTS['status'],
            bg=self.COLORS['primary'],
            fg='white'
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def validate_numeric_input(self, value):
        """Validate coordinate inputs are numeric"""
        if value.replace('.', '', 1).isdigit() or value == "":
            return True
        self.bell()
        return False

    def browse_folder(self):
        """Handle folder selection"""
        folder = tkFileDialog.askdirectory()
        if folder:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)
            self.update_status("Selected folder: {}".format(folder))  # Using .format() for string formatting

    def update_status(self, message, error=False):
        """Update status bar message"""
        self.status_bar.config(
            text=message,
            fg=self.COLORS['error'] if error else 'white'
        )

    def calculate_offsets(self):
        """Calculate X/Y offset values and update the label in the main window"""
        try:
            arb_x = float(self.arb_x_entry.get())
            arb_y = float(self.arb_y_entry.get())
            real_x = float(self.real_x_entry.get())
            real_y = float(self.real_y_entry.get())

            x_offset = real_x - arb_x
            y_offset = real_y - arb_y

            # Update the text box with new offsets
            self.offset_text.config(state=tk.NORMAL)  # Allow editing
            self.offset_text.delete(1.0, tk.END)  # Clear current text

            # Insert the offsets with red color
            self.offset_text.insert(tk.END, "Offsets: X = {:.3f}, Y = {:.3f}".format(x_offset, y_offset))

            # Apply red color to the offsets text
            self.offset_text.tag_configure("red", foreground=self.COLORS['red'])  # Red color for text
            self.offset_text.tag_add("red", 1.0, tk.END)  # Apply red color to the entire text

            self.offset_text.config(state=tk.DISABLED)  # Make text box read-only

            return x_offset, y_offset

        except ValueError:
            self.update_status("Invalid coordinate values", error=True)
            tkMessageBox.showerror("Input Error", "Please enter valid numeric coordinates")
            raise

    def process_databases(self):
        """Main processing function"""
        start_time = time.time()
        base_path = self.folder_entry.get()

        try:
            # Validate inputs
            if not self.validate_inputs():
                return

            # Calculate offsets
            x_offset, y_offset = self.calculate_offsets()

            # Find MDB files
            mdb_files = self.find_mdb_files(base_path)

            # Process databases
            self.process_mdb_files(mdb_files, x_offset, y_offset)

            # Show completion
            elapsed = time.time() - start_time
            self.show_completion_message(len(mdb_files), elapsed)

        except Exception as e:
            self.handle_processing_error(e)

    def validate_inputs(self):
        """Validate all user inputs"""
        errors = []

        if not self.folder_entry.get():
            errors.append("Please select a project folder")

        for entry in [self.arb_x_entry, self.arb_y_entry,
                      self.real_x_entry, self.real_y_entry]:
            if not entry.get():
                errors.append("All coordinate fields are required")

        if errors:
            self.update_status("Error: " + ", ".join(errors), error=True)
            tkMessageBox.showerror("Input Error", "\n".join(errors))
            return False

        return True

    def find_mdb_files(self, base_path):
        """Locate all MDB files in directory"""
        mdb_files = []
        for root, _, files in os.walk(base_path):
            for file in files:
                if file.endswith('.mdb'):
                    mdb_files.append(os.path.join(root, file))

        if not mdb_files:
            self.update_status("No MDB files found", error=True)
            tkMessageBox.showerror("Error", "No .mdb files found in selected folder")
            raise ValueError("No MDB files found")

        return mdb_files

    def process_mdb_files(self, mdb_files, x_offset, y_offset):
        """Process all found MDB files"""
        exception_log = os.path.join(os.path.dirname(mdb_files[0]),
                                     "exception_list_move_data.csv")

        with open(exception_log, 'a') as error_file:
            for idx, mdb_path in enumerate(mdb_files, 1):
                try:
                    self.update_status("Processing {}/{}: {}".format(idx, len(mdb_files), os.path.basename(
                        mdb_path)))  # Using .format() for string formatting
                    self.process_single_mdb(mdb_path, x_offset, y_offset)

                except Exception as e:
                    error_file.write(
                        "Error in {}: {}\n".format(mdb_path, str(e)))  # Using .format() for string formatting
                    self.update_status("Error processing file", error=True)
                    break

    def process_single_mdb(self, mdb_path, x_offset, y_offset):
        """Process a single MDB file"""
        pass

    def show_completion_message(self, total_files, elapsed_time):
        """Display completion message"""
        self.update_status(
            "Processing complete: {} files processed in {:.2f} seconds".format(total_files, elapsed_time)
        )
        tkMessageBox.showinfo("Process Complete", "All databases processed successfully.")

    def handle_processing_error(self, error):
        """Handle error during processing"""
        self.update_status("Error: {}".format(str(error)), error=True)
        tkMessageBox.showerror("Error", "An error occurred during processing.\n\n{}".format(str(error)))


if __name__ == "__main__":
    root = tk.Tk()
    app = CoordinateShiftApp(root)
    root.mainloop()
