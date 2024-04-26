import tkinter as tk
import matplotlib.pyplot as plt
from tkinter import messagebox, IntVar
import pyperclip
from shapely import wkt
from shapely.geometry import Polygon
from all import correct_geometry, shift_polygons, modify_polygons, import_wkt, commit, reorder_based_on_common_vertex
from all import revert_to_original_start_vertex
from matplotlib.widgets import CheckButtons

import psycopg2





class PolygonShifter:
    def __init__(self, master):
        self.master = master
        self.master.title("Polygon Shifter")

        # Database connection variables
        self.db_username = tk.StringVar()
        self.db_password = tk.StringVar()

        # Create a menu for database connection
        self.create_menu()
        self.db_connection = None

        self.frame1 = tk.Frame(master, borderwidth=2, relief="groove")
        self.frame1.grid(row=0, column=0, padx=10, pady=10)

        # Create the second frame
        self.frame2 = tk.Frame(master, borderwidth=2, relief="groove")
        self.frame2.grid(row=1, column=0, padx=10, pady=10)

        # Create the third frame
        self.frame3 = tk.Frame(master, borderwidth=2, relief="groove")
        self.frame3.grid(row=2, column=0, padx=10, pady=10)
        
        # Create the third frame 1
        self.frame3_1 = tk.Frame(self.frame3, borderwidth=2, relief="groove")
        self.frame3_1.grid(row=2, column=0, padx=10, pady=10)

        # Create the third frame 2
        self.frame3_2 = tk.Frame(self.frame3, borderwidth=2, relief="groove")
        self.frame3_2.grid(row=2, column=1, padx=10, pady=10)

        # Label and Text Entry for Polygon 2
        self.limitation_head = tk.Label(self.frame3_2, text="Limitations:", fg='blue')
        self.limitation_head.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.limitation_head.config(font=("TkDefaultFont", 12, "underline"))

        self.limitation_text = tk.Label(self.frame3_2, text="1. Do not work for hollow polygons\n", fg='red')
        self.limitation_text.grid(row=1, column=0, sticky="w", padx=5, pady=2)


        # Database connection status label
        self.connection_status_label = tk.Label(self.frame1, text="Not connected", fg="red", anchor="w")
        self.connection_status_label.grid(row=0, column=2, padx=5, pady=2)

        self.connection_name = tk.Label(self.frame1, text="DB::", fg="blue", anchor="e")
        self.connection_name.grid(row=0, column=0, padx=2, pady=2)

        # Label for Tolerance Input Field
        self.tolerance_label_text = tk.Label(self.frame1, text="|  Shift Polygon Tolerance:")
        self.tolerance_label_text.grid(row=0, column=3, sticky="e", padx=5, pady=2)

        # Tolerance Input Field
        self.tolerance_entry = tk.Entry(self.frame1)
        self.tolerance_entry.insert(0, "0.0001")  # Insert default value
        self.tolerance_entry.grid(row=0, column=4, sticky="w", padx=5, pady=2)

        # Label and Text Entry for Polygon 1
        self.poly1_label = tk.Label(self.frame2, text="Polygon 1      PID=", fg='blue')
        self.poly1_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)

        self.pid_1 = tk.Entry(self.frame2)
        self.pid_1.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        self.poly1_text = tk.Text(self.frame2, height=10, width=50)
        self.poly1_text.grid(row=2, column=0, columnspan=3, padx=5, pady=2)
        self.poly1_text.insert(tk.END, "")

        # Label and Text Entry for Polygon 2
        self.poly2_label = tk.Label(self.frame2, text="Polygon 2      PID=", fg='blue')
        self.poly2_label.grid(row=4, column=0, sticky="w", padx=5, pady=2)

        self.pid_2 = tk.Entry(self.frame2)
        self.pid_2.grid(row=4, column=1, sticky="w", padx=5, pady=2)

        self.poly2_text = tk.Text(self.frame2, height=10, width=50)
        self.poly2_text.grid(row=5, column=0, columnspan=3, padx=5, pady=2)
        self.poly2_text.insert(tk.END, "")

        # Output Texts, Copy Buttons, and Vertex Count Labels
        self.poly1_output_label = tk.Label(self.frame2, text="Output for Polygon 1", fg='blue')
        self.poly1_output_label.grid(row=1, column=5, sticky="w", padx=5, pady=2)

        self.poly1_output_text = tk.Text(self.frame2, height=10, width=50)
        self.poly1_output_text.grid(row=2, column=5, columnspan=2, padx=5, pady=2)
        self.poly1_output_text.insert(tk.END, "")

        self.poly1_copy_button = tk.Button(self.frame2, text="Copy",
                                           command=lambda: self.copy_text(self.poly1_output_text))
        self.poly1_copy_button.grid(row=2, column=8, padx=5, pady=2)
        self.poly1_vertex_label = tk.Label(self.frame2, text="Vertices: Before - 0, After - 0")
        self.poly1_vertex_label.grid(row=3, column=5, sticky="w", padx=5, pady=2)

        # Labels for displaying area before and after shift or clean
        self.area_poly1_value = tk.Label(self.frame2, text="Area: Before - 0, After - 0", fg='red')
        self.area_poly1_value.grid(row=3, column=0, sticky="w", padx=5, pady=2)

        self.poly2_output_label = tk.Label(self.frame2, text="Output for Polygon 2", fg='blue')
        self.poly2_output_label.grid(row=4, column=5, sticky="w", padx=5, pady=2)
        self.poly2_output_text = tk.Text(self.frame2, height=10, width=50)
        self.poly2_output_text.grid(row=5, column=5, columnspan=2, padx=5, pady=2)
        self.poly2_output_text.insert(tk.END, "")
        self.poly2_copy_button = tk.Button(self.frame2, text="Copy",
                                           command=lambda: self.copy_text(self.poly2_output_text))
        self.poly2_copy_button.grid(row=5, column=8, padx=5, pady=2)
        self.poly2_vertex_label = tk.Label(self.frame2, text="Vertices: Before - 0, After - 0")
        self.poly2_vertex_label.grid(row=6, column=5, sticky="w", padx=5, pady=2)

        self.area_poly2_value = tk.Label(self.frame2, text="Area: Before - 0, After - 0", fg='red')
        self.area_poly2_value.grid(row=6, column=0, sticky="w", padx=5, pady=2)

        # Radio Buttons to Choose Polygon
        self.choose_polygon_label = tk.Label(self.frame3_1, text="Choose polygon to shift:", fg='blue')
        self.choose_polygon_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)

        self.selected_polygon = tk.IntVar()
        self.selected_polygon.set(1)

        self.poly1_radio = tk.Radiobutton(self.frame3_1, text="Polygon 1", variable=self.selected_polygon, value=1)
        self.poly1_radio.grid(row=1, column=0, sticky="w", padx=5, pady=2)

        self.poly2_radio = tk.Radiobutton(self.frame3_1, text="Polygon 2", variable=self.selected_polygon, value=2)
        self.poly2_radio.grid(row=2, column=0, sticky="w", padx=5, pady=2)

        # Buttons for Shifting and Plotting
        self.shift_button = tk.Button(self.frame3_1, text="Shift Polygon", command=self.shift_polygon)
        self.shift_button.grid(row=1, column=2, columnspan=2, padx=5, pady=2)

        # Button for Cleaning Polygon 1
        self.clean_poly1_button = tk.Button(self.frame3_1, text="Clean Polygon 1", command=self.clean_polygon1)
        self.clean_poly1_button.grid(row=2, column=2, columnspan=2, padx=5, pady=2)

        self.plot_button = tk.Button(self.frame3_1, text="Plot Polygons", command=self.plot_polygons, fg='green')
        self.plot_button.grid(row=3, column=3, sticky="w", padx=5, pady=2)

        # Initialize Checkbuttons for plot layers
        self.plot_poly1_var = IntVar(value=1)
        self.plot_poly2_var = IntVar(value=1)
        self.plot_sh_poly1_var = IntVar(value=1)
        self.plot_sh_poly2_var = IntVar(value=1)

        self.import_p1 = tk.Button(self.frame2, text="Import",
                                   command=lambda: import_wkt(self.pid_1, self.poly1_text, self.db_connection))
        self.import_p1.grid(row=1, column=2, padx=5, pady=2)

        self.import_p2 = tk.Button(self.frame2, text="Import",
                                   command=lambda: import_wkt(self.pid_2, self.poly2_text, self.db_connection))
        self.import_p2.grid(row=4, column=2, padx=5, pady=2)

        self.poly1_commit = tk.Button(self.frame2, text="Commit", fg='blue',
                                      command=lambda: commit(self.pid_1, self.poly1_text, self.poly1_output_text,
                                                             self.db_connection))
        self.poly1_commit.grid(row=1, column=6, sticky="w", padx=5, pady=2)

        self.poly2_commit = tk.Button(self.frame2, text="Commit", fg='blue',
                                      command=lambda: commit(self.pid_2, self.poly2_text, self.poly2_output_text,
                                                             self.db_connection))
        self.poly2_commit.grid(row=4, column=6, sticky="w", padx=5, pady=2)

    def create_menu(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        # Database menu
        db_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Database", menu=db_menu)

        # Database connection submenu
        db_menu.add_command(label="Connect", command=self.connect_to_database)
        db_menu.add_separator()
        db_menu.add_command(label="Disconnect", command=self.disconnect_from_database)

    def connect_to_database(self):
        # Open a Toplevel window for database connection
        db_window = tk.Toplevel(self.master)
        db_window.title("Database Connection")

        # Username entry
        username_label = tk.Label(db_window, text="Username:")
        username_label.grid(row=0, column=0, padx=5, pady=2)
        # self.db_username.set("dosit_suresh")  # Set the default value for the StringVar
        username_entry = tk.Entry(db_window, textvariable=self.db_username)
        username_entry.grid(row=0, column=1, padx=5, pady=2)

        # Password entry
        password_label = tk.Label(db_window, text="Password:")
        password_label.grid(row=1, column=0, padx=5, pady=2)
        password_entry = tk.Entry(db_window, textvariable=self.db_password, show="*")
        password_entry.grid(row=1, column=1, padx=5, pady=2)

        # Connect button
        connect_button = tk.Button(db_window, text="Connect",
                                   command=lambda: self.perform_database_connection(db_window))
        connect_button.grid(row=2, column=0, columnspan=2, padx=5, pady=2)

        # # Bind the focus-in event to clear the default value
        username_entry.bind("<FocusOut>", self.clear_username_default)

        # Add an event binding to the username and password Entry widgets
        username_entry.bind("<Return>", lambda event: self.perform_database_connection(db_window))
        password_entry.bind("<Return>", lambda event: self.perform_database_connection(db_window))

    def perform_database_connection(self, db_window):
        # Retrieve username and password
        username = self.db_username.get()
        password = self.db_password.get()

        try:
            test_param = {
                "dbname": "nelis_stage_db",
                "user": username,
                "password": password,
                "host": "pg-node10.dos.stage.dc",
                "port": "5432"
            }
            live_param = {
                "dbname": "nelis_live_db",
                "user": username,
                "password": password,
                "host": "dbproxy.dos.live.dc",
                "port": "5000"
            }
            # test = psycopg2.connect(**test_param)
            live = psycopg2.connect(**live_param)
            self.db_connection = live
            connected_status = True
        except Exception as e:
            connected_status = False

        if connected_status:
            self.connection_status_label.config(text="Connected", fg="green")
            db_window.destroy()

        else:
            self.connection_status_label.config(text="Connection failed", fg="red")

    def disconnect_from_database(self):
        # Disconnect from the database
        # Example: Close SQLite connection
        try:
            self.db_connection.close()
            messagebox.showinfo("Success", "Disconnected from database successfully!")
        except AttributeError:
            messagebox.showinfo("Info", "Not connected to a database yet!")
        except Exception as e:
            messagebox.showerror("Error", f"Error occurred while disconnecting from database: {e}")

    def clear_username_default(self, event):
        self.db_username.set(event.widget.get())

    def shift_polygon(self):
        poly1_wkt = self.poly1_text.get("1.0", tk.END)
        poly2_wkt = self.poly2_text.get("1.0", tk.END)

        poly1_output_wkt = self.poly1_output_text.get("1.0", tk.END)
        poly2_output_wkt = self.poly2_output_text.get("1.0", tk.END)



        poly1_wkt,poly2_wkt = reorder_based_on_common_vertex(poly1_wkt,poly2_wkt)

        poly1 = wkt.loads(poly1_wkt)
        poly2 = wkt.loads(poly2_wkt)



        # Fetch tolerance value from entry widget
        tolerance_str = self.tolerance_entry.get()
        try:
            tolerance = float(tolerance_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid tolerance value. Please enter a valid number.")
            return

        poly1, before_count_poly1, after_count_poly1, before_area1, after_area1 = correct_geometry(poly1_wkt)
        poly2, before_count_poly2, after_count_poly2, before_area2, after_area2 = correct_geometry(poly2_wkt)

        if self.selected_polygon.get() == 1:
            shifted_poly1 = shift_polygons(Polygon(poly1), Polygon(poly2), tolerance)
            self.poly1_output_text.delete("1.0", tk.END)
            self.poly1_output_text.insert(tk.END, shifted_poly1.wkt)
            self.poly2_output_text.delete("1.0", tk.END)
            self.poly2_output_text.insert(tk.END, poly2.wkt)


        elif self.selected_polygon.get() == 2:
            shifted_poly2 = shift_polygons(Polygon(poly2), Polygon(poly1), tolerance)
            self.poly2_output_text.delete("1.0", tk.END)
            self.poly2_output_text.insert(tk.END, shifted_poly2.wkt)
            self.poly1_output_text.delete("1.0", tk.END)
            self.poly1_output_text.insert(tk.END, poly1.wkt)

        # Find common vertices
        shifted_poly2_wkt = self.poly2_output_text.get("1.0", tk.END)
        shifted_poly1_wkt = self.poly1_output_text.get("1.0", tk.END)
        shifted_poly1 = wkt.loads(shifted_poly1_wkt)
        shifted_poly2 = wkt.loads(shifted_poly2_wkt)

        shifted_poly2, shifted_poly1 = modify_polygons(shifted_poly2, shifted_poly1, tolerance)
        shifted_poly1, shifted_poly2 = modify_polygons(shifted_poly1, shifted_poly2, tolerance)

        poly1_old_wkt = self.poly1_text.get("1.0", tk.END)
        poly2_old_wkt = self.poly2_text.get("1.0", tk.END)


        shifted_poly1 = revert_to_original_start_vertex(shifted_poly1.wkt,poly1_old_wkt,tolerance)
        shifted_poly2 = revert_to_original_start_vertex(shifted_poly2.wkt,poly2_old_wkt,tolerance)

        self.poly1_output_text.delete("1.0", tk.END)
        self.poly1_output_text.insert(tk.END, shifted_poly1.wkt)

        self.poly2_output_text.delete("1.0", tk.END)
        self.poly2_output_text.insert(tk.END, shifted_poly2.wkt)

        shifted_poly2_wkt = self.poly2_output_text.get("1.0", tk.END)
        shifted_poly1_wkt = self.poly1_output_text.get("1.0", tk.END)


        # Compare the contents of poly1_text and poly1_output_text
        if poly1_wkt.strip() != shifted_poly1_wkt.strip():
            self.poly1_output_text.config(fg='red')
        else:
            self.poly1_output_text.config(fg='black')

        # Compare the contents of poly2_text and poly2_output_text
        if poly2_wkt.strip() != shifted_poly2_wkt.strip():
            self.poly2_output_text.config(fg='red')
        else:
            self.poly2_output_text.config(fg='black')

        # Update vertex count labels
        self.poly1_vertex_label.config(text=f"Vertices: Before - {before_count_poly1}, After - {after_count_poly1}")
        self.poly2_vertex_label.config(text=f"Vertices: Before - {before_count_poly2}, After - {after_count_poly2}")
        self.area_poly1_value.config(text=f"Area: Before - {before_area1}, After - {after_area1}", fg='red')
        self.area_poly2_value.config(text=f"Area: Before - {before_area2}, After - {after_area2}", fg='red')

    def plot_polygons(self):
        fig, ax = plt.subplots()

        poly1_wkt = self.poly1_text.get("1.0", tk.END).strip()
        poly2_wkt = self.poly2_text.get("1.0", tk.END).strip()
        shift_poly1_wkt = self.poly1_output_text.get("1.0", tk.END).strip()
        shift_poly2_wkt = self.poly2_output_text.get("1.0", tk.END).strip()

        # Initialize poly2_line to None
        self.poly1_line = None
        self.poly2_line = None
        self.shift_poly1_line = None
        self.shift_poly2_line = None

        if poly1_wkt:
            try:
                poly1 = wkt.loads(poly1_wkt)
                poly1_color = 'blue'  # Default color for Polygon 1
                self.poly1_line, = ax.plot(*poly1.exterior.xy, label='Polygon 1', color=poly1_color)
            except Exception as e:
                messagebox.showerror("Error", f"Error loading Polygon 1: {e}")

        if poly2_wkt:
            try:
                poly2 = wkt.loads(poly2_wkt)
                poly2_color = 'red'  # Default color for Polygon 2
                self.poly2_line, = ax.plot(*poly2.exterior.xy, label='Polygon 2', color=poly2_color)
            except Exception as e:
                messagebox.showerror("Error", f"Error loading Polygon 2: {e}")

        if shift_poly1_wkt:
            try:
                shift_poly1 = wkt.loads(shift_poly1_wkt)
                shift_poly1_color = 'green'  # Default color for Shifted Polygon 1
                self.shift_poly1_line, = ax.plot(*shift_poly1.exterior.xy, label='Shifted Polygon 1',
                                                 color=shift_poly1_color)
            except Exception as e:
                messagebox.showerror("Error", f"Error loading Shifted Polygon 1: {e}")

        if shift_poly2_wkt:
            try:
                shift_poly2 = wkt.loads(shift_poly2_wkt)
                shift_poly2_color = 'orange'  # Default color for Shifted Polygon 2
                self.shift_poly2_line, = ax.plot(*shift_poly2.exterior.xy, label='Shifted Polygon 2',
                                                 color=shift_poly2_color)
            except Exception as e:
                messagebox.showerror("Error", f"Error loading Shifted Polygon 2: {e}")

        # Set aspect ratio and legend
        ax.set_aspect('equal', 'box')
        # Create legend with correct labels and colors
        handles = [line for line in [self.poly1_line, self.poly2_line, self.shift_poly1_line, self.shift_poly2_line] if
                   line is not None]
        labels = ['Polygon 1', 'Polygon 2', 'Shifted Polygon 1', 'Shifted Polygon 2']
        ax.legend(handles=handles, labels=labels)

        # Create CheckButtons
        self.create_check_buttons(ax)

        plt.subplots_adjust(right=0.8)

        plt.draw()

        # Show the plot
        plt.show()

    def create_check_buttons(self, ax):
        # Define the position and size of the CheckButtons
        rax = plt.axes([0.85, 0.4, 0.1, 0.15])

        # Create the CheckButtons
        check_buttons = CheckButtons(rax, ('Polygon 1', 'Polygon 2', 'Shifted Polygon 1', 'Shifted Polygon 2'),
                                     (True, True, True, True))

        # Function to handle the checkbox toggling
        def func(label):
            if label == 'Polygon 1':
                self.poly1_line.set_visible(not self.poly1_line.get_visible())
            elif label == 'Polygon 2':
                self.poly2_line.set_visible(not self.poly2_line.get_visible())
            elif label == 'Shifted Polygon 1':
                self.shift_poly1_line.set_visible(not self.shift_poly1_line.get_visible())
            elif label == 'Shifted Polygon 2':
                self.shift_poly2_line.set_visible(not self.shift_poly2_line.get_visible())
            plt.draw()
            plt.show()

        # Connect the checkbox function with the buttons
        check_buttons.on_clicked(func)

        # Set initial visibility state for the lines
        if self.poly1_line is not None:
            self.poly1_line.set_visible(True)
        if self.poly2_line is not None:
            self.poly2_line.set_visible(True)
        if self.shift_poly1_line is not None:
            self.shift_poly1_line.set_visible(True)
        if self.shift_poly2_line is not None:
            self.shift_poly2_line.set_visible(True)

        # Update the plot to reflect the initial visibility state
        plt.draw()

        plt.show()

    def open_plot(self):
        self.plot_polygons()

    def clean_polygon1(self):
        poly1_wkt = self.poly1_text.get("1.0", tk.END)
        poly1 = wkt.loads(poly1_wkt)
        poly1, before_count, after_count, before_area1, after_area1 = correct_geometry(poly1_wkt)
        self.poly1_output_text.delete("1.0", tk.END)
        self.poly1_output_text.insert(tk.END, poly1.wkt)

        # Compare the contents of poly1_text and poly1_output_text
        if poly1_wkt.strip() != poly1.wkt.strip():
            self.poly1_output_text.config(fg='red')
        else:
            self.poly1_output_text.config(fg='black')

        messagebox.showinfo("Cleaned", "Polygon 1 cleaned successfully!")

        self.poly1_vertex_label.config(text=f"Vertices: Before - {before_count}, After - {after_count}")
        self.area_poly1_value.config(text=f"Area: Before - {before_area1}, After - {after_area1}")

    def copy_text(self, text_widget):
        text_to_copy = text_widget.get("1.0", "end-1c")  # Get text from text widget
        pyperclip.copy(text_to_copy)  # Copy text to clipboard


def main():
    root = tk.Tk()
    app = PolygonShifter(root)
    root.mainloop()


if __name__ == "__main__":
    main()

# pyinstaller --onefile all7.py
