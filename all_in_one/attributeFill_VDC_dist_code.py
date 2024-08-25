from Tkinter import *
import shared_data
global dic_case_sen

def Fill_VDC_Dist_Code(self,vdc_code='',district_code=''):
    import tkMessageBox
    import arcpy
    import os

    district_code=district_code
    vdc_code=vdc_code
    path = shared_data.directory
    mdb_list = shared_data.filtered_mdb_files
    exception_list= open(path+"\\exception_list_att_fill_vdc_dis_code.csv","a")
    exception_list.truncate(0)
    allerror = open (path + "\\regex.csv", "a")
    allerror.truncate (0)
    for mdb_file in mdb_list:
        parcelfile = os.path.join(mdb_file, "Parcel")
        print(parcelfile)

        filename = os.path.basename(mdb_file)
        try:
            arcpy.Compact_management(mdb_file)
        except:
            exception_list.write("Compact Error for ,"+filename+"\n")
            print("Compact error for "+filename)

        try:
            if(district_code != '' and int(district_code)):
                #print district_code
                arcpy.CalculateField_management(parcelfile,"DISTRICT",int(district_code),"PYTHON")#FOR DISTRICT_CODE
            if (vdc_code != '' and int(vdc_code)):
                arcpy.CalculateField_management(parcelfile,"VDC",int(vdc_code),"PYTHON")#FOR VDC_CODE

        except:
            exception_list.write("Attribute fill Error for ," + filename + "\n")
            allerror.write(filename + "," + ",error" +"\n")
        #
        # else:
        #     print(filename + "," + " ")
        #     allerror.write (filename + "," + " " + "\n")
    tkMessageBox.showinfo(title="Fix Attribute Errors", message="Done")
    allerror.close()
    exception_list.close()


