import tkMessageBox
import arcpy
import time
import shared_data

def compactDb(self):
    startTime = time.time ()
    path = shared_data.directory
    exception_list= open(path+"\\exception_list_compact.csv","a")
    count = 0
    total= len(shared_data.filtered_mdb_files)
    for i in shared_data.filtered_mdb_files:
        count +=1
        try:
            arcpy.Compact_management(i)
        except:
            exception_list.write("Compact Error for ," + i + "\n")
            print("Compact error for "+i)
        print (i + " (" + str(count) + "/" + str(total) + ")")
    print(" Compact process complete")
    exception_list.close()
    print ('The script took {0} second !'.format(time.time() - startTime))

    tkMessageBox.showinfo(title="Compact database", message="Done")
