from Tkinter import *
import shared_data

dic_case_sen={
    "Ta": "11",
    "Tha": "12",
    "Da": "13",
    "Dha": "14",
    "tta": "16",
    "ttha": "17",
    "dda": "18",
    "ddha": "19",
    "dhha": "19",
    "sha": "30",
    "SHA": "31",
    "sa": "32"
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
    "chha": "07",
    "ja": "08",
    "jha": "09",
    "yna": "10",
    "yan": "10",
    "ana": "15",
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
    "ha": "33",
    "ksha":"34",
    "kshya": "34",
    "tra": "35",
    "gya": "36"
}

dict_scale={
    "625"   :   "5552",
    "600"   :   "5553",
    "500"   :   "5554",
    "1200"  :   "5555",
    "1250"  :   "5556",
    "2400"  :   "5557",
    "2500"  :   "5558",
    "4800"  :   "5559"
}

def Fill_Ward_Grid(self):  # sourcery skip
    import tkMessageBox
    import arcpy
    import os
    import re
    path = shared_data.directory
    mdb_list = shared_data.filtered_mdb_files
    allerror = open (path + "\\regex.csv", "a")
    exception_list= open(path+"\\exception_list_att_fill_ward_grid.csv","a")
    allerror.truncate (0)
    exception_list.truncate(0)
    matches=["file","trig"]

    mapped_scale = self.variable.get()
    if mapped_scale in dict_scale:
        scaled_value=dict_scale[mapped_scale]
    else:
        scaled_value="5555"

    for mdb_file in mdb_list:
        if any(x in mdb_file.lower() for x in matches):  # To detect and skip file/trig folder
            continue  # Skip this iteration if the condition is met

        parcelfile = os.path.join(mdb_file, "Parcel")
        print(parcelfile)

        base_file_name = os.path.basename(mdb_file)
        try:
            arcpy.Compact_management(mdb_file)
        except:
            exception_list.write("Compact Error for ,"+base_file_name+"\n")
            print("Compact error for "+base_file_name)
        new_filename = base_file_name.replace(" ", "")
        x = re.findall ("^...[A-Za-z][A-Za-z\s_-]+(\d+)([\s_(-]*[A-Za-z]*[\(\s_-]*)(\d*)", new_filename)
        print(x)
        if x:
            bad_chars = ['_', '-', '(', ")"," "]
            new_string_name = ''.join(i for i in x[0][1] if not i in bad_chars)
            if(new_string_name) in dic_case_sen:
                dic_code=dic_case_sen[new_string_name]
            elif(new_string_name.lower()) in dic_case_insen:
                dic_code=dic_case_insen[new_string_name.lower()]
            new_string_no = x[0][2]
            ward_code=int(x[0][0])
            if(ward_code>99):
                continue
            if new_string_no=="":
                new_string_no="0"
            try:
                print("code="+scaled_value + x[0][0].zfill(2) + dic_code + new_string_no)
                sheet_code=scaled_value + x[0][0].zfill(2) + dic_code + new_string_no
                del dic_code
                del new_string_no
                TheRows = arcpy.UpdateCursor(parcelfile)
                for TheRow in TheRows:
                    TheRow.setValue("GRIDS1",sheet_code)
                    TheRows.updateRow(TheRow)
                    Ward = TheRow.getValue("WARDNO")
                    if (Ward is None or len(Ward) == 0 or Ward == " " or Ward == "" or int(Ward) > 40):
                        TheRow.setValue("WARDNO", int(x[0][0]))
                        TheRows.updateRow(TheRow)
                allerror.write(base_file_name + "," + x[0][0] + "," + x[0][1] + "," + x[0][2] + "\n")
            except:
                exception_list.write("Attribute fill Error for ," + base_file_name + "\n")
                allerror.write(base_file_name + "," + x[0][0] + "," + x[0][1] + "," + x[0][2] + ",error" +"\n")

        else:
            print(base_file_name + "," + " ")
            allerror.write (base_file_name + "," + " " + "\n")
    tkMessageBox.showinfo(title="Fill Ward No and Grid in freesheet", message="Done")
    allerror.close()
    exception_list.close()