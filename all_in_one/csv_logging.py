import os
import csv


def create_csv_log_file(file_path):
    # Determine the directory name
    dir_name = os.path.dirname(file_path)

    # If directory is empty, use D: drive
    if not dir_name:
        dir_name = 'D:'

    # Ensure the directory exists
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    # Create or open the CSV file
    file_handler = open(file_path, 'wb')  # Use 'wb' for Python 2
    csv_writer = csv.writer(file_handler)
    return file_handler, csv_writer


def write_error_to_csv(csv_writer, filename, error_message):
    """Write an error message to the CSV file."""
    csv_writer.writerow([filename, error_message])
