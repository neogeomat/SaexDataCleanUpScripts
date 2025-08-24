# -*- coding: utf-8 -*-
from Tkinter import *
import tkMessageBox
import arcpy
import os
import re
import shared_data
import time
from send_notif_telegram import send_telegram_message  # Import the function to send Telegram notifications

dic_case_sen = {
    "ddha": "19",
    "dhha": "19",
    "sha": "30",
    "Sha": "30",
    "SHA": "31",
    "saa": "31",
    "Shha": "31",
    "sa": "32",
    "Sa": "32"
}

dic_case_insen = {
    "": "00",
    "ka": "01",
    "k": "01",
    "kha": "02",
    "kh": "02",
    "ga": "03",
    "gha": "04",
    "nga": "05",
    "ng": "05",
    "ch": "06",
    "cha": "06",
    "chaa": "06",
    "chha": "07",
    "Chha": "07",
    "ja": "08",
    "jha": "09",
    "yna": "10",
    "yan": "10",
    "Ta": "11",
    "ta": "11",
    "Tha": "12",
    "tha": "12",
    "Da": "13",
    "da": "13",
    "Dha": "14",
    "dha": "14",
    "ana": "15",
    "tta": "16",
    "taa": "16",
    "ttha": "17",
    "thaa":'17',
    "dda": "18",
    "daa": "18",
    "dhaa": "19",
    "na": "20",
    "pa": "21",
    "pha": "22",
    "fa": "22",
    "ba": "23",
    "bha": "24",
    "ma": "25",
    "ya": "26",
    "ra": "27",
    "la": "28",
    "wa": "29",
    "wo": "29",
    "ha": "33",
    "ksha":"34",
    "chey":"34",
    "chhe":"34",
    "kshya": "34",
    "tra": "35",
    "gya": "36"
}

dict_scale = {
    "625": "5552",
    "600": "5553",
    "500": "5554",
    "1200": "5555",
    "1250": "5556",
    "2400": "5557",
    "2500": "5558",
    "4800": "5559"
}
#555501021 = 1200 scale map of 1 ward kha -1
def Fill_Ward_Grid(self, scale, status_update=None, show_messagebox=True, update_progress=None):
    """Fill Ward and Grid codes into the Parcel layers and handle errors."""
    startTime = time.time()
    path = shared_data.directory
    mdb_list = shared_data.filtered_mdb_files
    allerror = open(os.path.join(path, "regex.csv"), "a")
    exception_list = open(os.path.join(path, "exception_list_att_fill_ward_grid.csv"), "a")
    allerror.truncate(0)
    exception_list.truncate(0)

    # Determine the scaled value based on the scale provided
    scaled_value = dict_scale.get(scale, "5555")

    if status_update:
        status_update("Starting the ward and grid fill process...")

    for count, mdb_file in enumerate(mdb_list, start=1):

        if any(x in mdb_file.lower() for x in ["file", "trig"]):
            continue

        parcelfile = os.path.join(mdb_file, "Parcel")
        base_file_name = os.path.basename(mdb_file)
        print parcelfile

        if status_update:
            status_update("Processing {} \n({}/{})".format(base_file_name, count, len(mdb_list)))
        print("Processing {} \n({}/{})".format(base_file_name, count, len(mdb_list)))


        try:
            arcpy.Compact_management(mdb_file)
        except Exception as e:
            exception_list.write("Compact Error for ," + base_file_name + "\n")
            print "Compact error for " + base_file_name + ": " + str(e)

        new_filename = base_file_name.replace(" ", "")
        x = re.findall(r"^.[A-Za-z][A-Za-z\s_-]+(\d+)([\s_(-]*[A-Za-z]*[\(\s_-]*)(\d*)", new_filename)
        print ("x=",x)

        if x:
            bad_chars = ['_', '-', '(', ")", " "]
            new_string_name = ''.join(i for i in x[0][1] if i not in bad_chars)


            dic_code = dic_case_sen.get(new_string_name) or dic_case_insen.get(new_string_name.lower(), "")




            new_string_no = x[0][2] if x[0][2] else "0"


            ward_code = int(x[0][0])

            if ward_code > 99:
                continue

            if int(new_string_no) >= 10:
                new_string_no = 0

            print new_string_no

            try:
                sheet_code = scaled_value + x[0][0].zfill(2) + dic_code + str(new_string_no)
                print "code=" + sheet_code
                if len(sheet_code)!=9:
                    exception_list.write("Attribute fill Error for ," + base_file_name + "\n")
                    print "Attribute fill Error for " + base_file_name + ": " + str(e)

                else:
                    TheRows = arcpy.UpdateCursor(parcelfile)
                    for TheRow in TheRows:
                        TheRow.setValue("GRIDS1", sheet_code)
                        TheRows.updateRow(TheRow)
                        Ward = TheRow.getValue("WARDNO")
                        if not Ward or len(Ward) == 0 or Ward == " " or int(Ward) > 40:
                            TheRow.setValue("WARDNO", ward_code)
                            TheRows.updateRow(TheRow)
                if status_update:
                    status_update("Processed {} ({}/{})".format(base_file_name, count, len(mdb_list)))
            except Exception as e:
                exception_list.write("Attribute fill Error for ," + base_file_name + "\n")
                print "Attribute fill Error for " + base_file_name + ": " + str(e)
                # Send Telegram notification for error
                error_message = "⚠️ Attribute Fill Ward and Grid Error!\n\n" \
                                "🗂 Path: {}\n" \
                                "📜 Script: AttributeFill_ward_grid\n" \
                                "🗂 File: {}\n" \
                                "❌ Error: {}".format(path, mdb_file, str(e))
                send_telegram_message(error_message)

        else:
            print base_file_name + "," + " "
            allerror.write(base_file_name + "," + " " + "\n")


        if update_progress:
            x= count/float(len(mdb_list))
            progress_value = (x) * 100
            update_progress(progress_value, len(mdb_list))
        self.master.update_idletasks()  # Ensure GUI updates


    allerror.close()
    exception_list.close()
    print("Attribute Fill of ward and Grid Process complete")

    if status_update:
        status_update("Fill Ward No and Grid process complete.")

    if show_messagebox:
        tkMessageBox.showinfo(title="Fill Ward No and Grid in freesheet", message="Done")

    # Send Telegram notification for successful processing
    success_message = "✅ Attribute Fill Ward and Grid Success!\n\n" \
                      "🗂 Path: {}\n" \
                      "📜 Script: AttributeFill_ward_grid\n" \
                      "⏱ Duration: {:.2f} seconds".format(path, time.time() - startTime)
    send_telegram_message(success_message)

    print 'The script took {0} seconds!'.format(time.time() - startTime)
