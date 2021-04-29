import arcpy

input_db = "C:\\Users\\HP\\Documents\\ArcGIS\\Default.gdb\\Grid.shp"

# Add Fields
arcpy.AddField_management(input_db, "east", "TEXT",field_length=15)
arcpy.AddField_management(input_db, "west", "TEXT",field_length=15)
arcpy.AddField_management(input_db, "north", "TEXT",field_length=15)
arcpy.AddField_management(input_db, "south", "TEXT",field_length=15)
arcpy.AddField_management(input_db, "northeast", "TEXT",field_length=15)
arcpy.AddField_management(input_db, "northwest", "TEXT",field_length=15)
arcpy.AddField_management(input_db, "southeast", "TEXT",field_length=15)
arcpy.AddField_management(input_db, "southwest", "TEXT",field_length=15)


west_code="""def west1(name):
                if (int(name.split("-")[2]) - 1) % 5 == 0:
                    if (int(name.split("-")[1]) - 1) % 40 == 0:
                        if (int(name.split("-")[0]) - 1) < 54 and (int(name.split("-")[0]) - 1) % 6 == 0:
                            return ""
                        else:
                            if (int(name.split("-")[0]) - 1) % 6 == 0:
                                return str(int(name.split("-")[0]) - 55).zfill(3) + "-" + str(int(name.split("-")[1]) + 39).zfill(
                                        4) + "-" + str(int(name.split("-")[2]) + 4).zfill(2)
                            else:
                                return str(int(name.split("-")[0]) - 1).zfill(3) + "-" + str(int(name.split("-")[1]) + 39).zfill(
                                        4) + "-" + str(int(name.split("-")[2]) + 4).zfill(2)
                    else:
                        return name.split("-")[0] + "-" + str(int(name.split("-")[1]) - 1).zfill(4) + "-" + str(int(name.split("-")[2]) + 4).zfill(2)
                else:
                    return name.split("-")[0] + "-" + name.split("-")[1] + "-" + str(int(name.split("-")[2]) - 1).zfill(2)
    """

east_code="""
def east1(name):
    if int(name.split("-")[2]) % 5 == 0:
        if int(name.split("-")[1]) % 40 == 0:
            if int (name.split("-")[0]) > 126 and int (name.split("-")[0]) % 6 == 0:
                return ""
            else:
                if int(name.split("-")[0]) % 6 == 0:
                    return str(int(name.split("-")[0]) + 55).zfill(3) + "-" + str(int(name.split("-")[1]) - 39).zfill(
                            4) + "-" + str(int(name.split("-")[2]) - 4).zfill(2)
                else:
                    return str(int(name.split("-")[0]) + 1).zfill(3) + "-" + str(int(name.split("-")[1]) - 39).zfill(
                            4) + "-" + str(int(name.split("-")[2]) - 4).zfill(2)
        else:
            return name.split("-")[0] + "-" + str(int(name.split("-")[1]) + 1).zfill(4) + "-" + str(int(name.split("-")[2]) - 4).zfill(2)
    else:
        return name.split("-")[0] + "-" + name.split("-")[1] + "-" + str(int(name.split("-")[2]) + 1).zfill(2)
"""

north_code="""
def north1(name):
    if int(name.split("-")[2]) < 6 :
        if int(name.split("-")[1]) < 41:
            if (int(name.split("-")[0]) >= 1 and int(name.split("-")[0]) <= 6) or (int(name.split("-")[0]) >= 61 and int(name.split("-")[0]) <= 66) or (int(name.split("-")[0]) >= 121 and int(name.split("-")[0]) <= 126):
                return ""
            else:
                return str(int(name.split("-")[0]) - 6).zfill(3) + "-" + str(int(name.split("-")[1]) + 1560).zfill(
                        4) + "-" + str(int(name.split("-")[2]) +20 ).zfill(2)
        else:
            return name.split("-")[0] + "-" + str(int(name.split("-")[1]) + 1560).zfill(4) + "-" + str(int(name.split("-")[2]) + 20).zfill(2)
    else:
        return name.split("-")[0] + "-" + name.split("-")[1] + "-" + str(int(name.split("-")[2]) - 5).zfill(2)
"""

south_code="""
def south1(name):
    if int(name.split("-")[2]) > 20 :
        if int(name.split("-")[1]) > 1559:
            if (int(name.split("-")[0]) >= 54 and int(name.split("-")[0]) <= 60) or (int(name.split("-")[0]) >= 114 and int(name.split("-")[0]) <= 120) or (int(name.split("-")[0]) >= 174 and int(name.split("-")[0]) <= 180):
                return ""
            else:
                return str(int(name.split("-")[0]) + 6).zfill(3) + "-" + str(int(name.split("-")[1]) - 1560).zfill(
                        4) + "-" + str(int(name.split("-")[2]) - 20 ).zfill(2)
        else:
            return name.split("-")[0] + "-" + str(int(name.split("-")[1]) - 1560).zfill(4) + "-" + str(int(name.split("-")[2]) - 20).zfill(2)
    else:
        return name.split("-")[0] + "-" + name.split("-")[1] + "-" + str(int(name.split("-")[2]) + 5).zfill(2)
"""




arcpy.CalculateField_management(input_db, "east", "east1(!name!)", "PYTHON",east_code)
arcpy.CalculateField_management(input_db, "west", "west1(!name!)", "PYTHON",west_code)
arcpy.CalculateField_management(input_db, "north", "north1(!name!)", "PYTHON",north_code)
arcpy.CalculateField_management(input_db, "south", "south1(!name!)", "PYTHON",south_code)
arcpy.CalculateField_management(input_db, "northeast", "north1(!east!)", "PYTHON",north_code)
arcpy.CalculateField_management(input_db, "northwest", "north1(!west!)", "PYTHON",north_code)
arcpy.CalculateField_management(input_db, "southeast", "south1(!east!)", "PYTHON",south_code)
arcpy.CalculateField_management(input_db, "southwest", "south1(!west!)", "PYTHON",south_code)
print "Done"

