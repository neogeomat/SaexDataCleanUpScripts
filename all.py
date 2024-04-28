import psycopg2
from shapely.geometry import Polygon, MultiPolygon
from tkinter import messagebox
from shapely.geometry import Point
from shapely.wkt import loads
import numpy as np
from shapely.wkb import loads
import tkinter as tk

def commit(parcelid_widget,old_poly,poly_out_wkt,conn):

    if not conn:
        messagebox.showerror("Error", "Database is not connected. Please connect to the database first.")
        return
    parcelid = parcelid_widget.get()
    # Check if PID is empty
    if not parcelid:
        messagebox.showerror("Error", "Parcel ID empty")
        return

    poly_wkt = poly_out_wkt.get("1.0", "end-1c")
    in_poly_wkt = old_poly.get("1.0", "end-1c")

    #print(parcelid)


    if not poly_wkt:
        messagebox.showerror("Error", "No geometry to commit")
        return

    # Create a cursor object
    cur = conn.cursor()

    try:
        # Execute a SELECT query to retrieve the WKB representation of the geometry
        cur.execute("""update cadastral.geometries 
                        set _geometry = %s 
                        from cadastral.parcels p
                        where p.geometryid = cadastral.geometries.geometryid 
                        and p.parcelid = %s""", (poly_wkt,parcelid))

        conn.commit()

        cur.execute("select s.sonameeng from cadastral.parcels p , master.surveyoffices s where p.soid = s.soid and p.parcelid = %s", (parcelid,))

        # Fetch the result
        office_name = cur.fetchone()
        save_to_file(FILE_NAME, parcelid, in_poly_wkt,office_name)
        messagebox.showinfo("Success", f"Commit and Saved:")

    except psycopg2.Error as e:
        messagebox.showerror("Error", f"Database error: {e}")


def import_wkt(parcelid_widget,insert_txt_widget,conn):

    if not conn:
        messagebox.showerror("Error", "Database is not connected. Please connect to the database first.")
        return

    parcelid = parcelid_widget.get()
    # Check if PID is empty
    if not parcelid:
        messagebox.showerror("Error", "Please enter a PID.")
        return

    # Create a cursor object
    cur = conn.cursor()

    try:
        # Execute a SELECT query to retrieve the WKB representation of the geometry
        cur.execute("select g._geometry from cadastral.parcels p ,cadastral.geometries g where p.geometryid = g.geometryid and p.parcelid = %s", (parcelid,))

        # Fetch the result
        result = cur.fetchone()

        if result:
            # The result is a tuple containing the WKB representation
            wkb_representation = result[0]

            # Convert WKB bytes to WKT string
            wkt_geometry = wkb_to_wkt_with_precision(wkb_representation, precision=10)


            insert_txt_widget.delete("1.0", tk.END)
            insert_txt_widget.insert("1.0",wkt_geometry)
            return wkb_representation
        else:
            messagebox.showerror("Error", "No geometry found for the given parcelid.")
            return None
    except Exception as e:
        messagebox.showerror("Error", "Please enter a valid PID.")
        return None

from shapely import wkb, wkt

# Function to convert WKB to WKT with 10-digit precision
from shapely.geometry import shape

# Function to convert WKB to WKT with 10-digit precision
def wkb_to_wkt_with_precision(wkb_representation, precision=10):
    # Convert WKB bytes to Shapely geometry object
    geom = loads(wkb_representation)
    # Convert geometry object to WKT string with specified precision
    wkt_geometry = shape(geom).wkt
    return wkt_geometry


def wkb_to_wkt(wkb_bytes):
    geometry = wkb.loads(wkb_bytes)
    wkt_string = wkt.dumps(geometry)
    return wkt_string


from shapely import wkt
from shapely.geometry import Polygon

def correct_geometry_old(geometry):
    # Load the geometry from the WKT string
    geom = wkt.loads(geometry)

    # Calculate the number of coordinates and the area of the geometry before any corrections
    before_count = count_coordinates(geom)
    before_area = geom.area

    # Apply corrections step by step
    geometry1 = remove_overshoot(geometry)
    geometry2 = remove_duplicate_coordinates(geometry1)
    #polygon = wkt.loads(geometry2)
    geometry3 = remove_duplicate_polygon_coordinates(geometry2)

    # Remove duplicate coordinates from the exterior of the polygon, excluding the endpoints
    coordinates = geometry3.exterior.coords
    coord = remove_duplicate_coords_except_ends(coordinates)
    geometry4 = Polygon(coord)

    # Count the coordinates and calculate the area of the polygon after all corrections
    after_count = count_coordinates(geometry4)
    after_area = geometry4.area

    return geometry4, before_count, after_count, before_area, after_area


def correct_geometry(geometry,tol_area = 0.1):

    threshold_area = 2
    # Load the geometry from the WKT string
    geom = wkt.loads(geometry)

    # Calculate the number of coordinates and the area of the geometry before any corrections
    before_count = count_coordinates(geom)
    before_area = geom.area

    geometry1 = remove_overshoot(geometry)
    geometry2 = remove_duplicate_coordinates(geometry1)
    polygon = geometry2
    geometry3 = remove_duplicate_polygon_coordinates(polygon)

    # Check if there are interior rings and if their area exceeds the threshold
    geometry4 = remove_small_interior_polygons(geometry3, tol_area)

    after_count = count_coordinates(geometry4)
    after_area = geometry4.area

    return geometry4, before_count, after_count, before_area, after_area


def fix_ring_orientation(ring):
    # Ensure the ring is oriented counter-clockwise
    if ring.is_ccw:
        return ring
    else:
        return ring.coords[::-1]

def remove_small_interior_polygons(polygon, tolerance_area):
    filtered_interior_rings = []
    for hole in polygon.interiors:
        fixed_hole = fix_ring_orientation(hole)
        interior_polygon = Polygon(fixed_hole)
        if interior_polygon.area >= tolerance_area:
            filtered_interior_rings.append(hole)
    filtered_polygon = Polygon(polygon.exterior, filtered_interior_rings)
    return filtered_polygon

def shift_polygons(poly1, poly2, tolerance):
    new_poly_points = []
    for point1 in poly1.exterior.coords:
        replaced = False
        for point2 in poly2.exterior.coords:
            if Point(point1).distance(Point(point2)) <= tolerance:
                new_poly_points.append(point2)
                replaced = True
                break
        if not replaced:
            new_poly_points.append(point1)
    return Polygon(new_poly_points)

def add_missing_vertices(polygon1, polygon2, common_vertex_index1, common_vertex_index2,common_vertex1,common_vertex2):
    polygon1_coords = list(polygon1.exterior.coords)
    missing_vertices = []
    if common_vertex_index1 > common_vertex_index2:
        missing_vertices = polygon1_coords[
                           polygon1_coords.index(common_vertex2) + 1:polygon1_coords.index(common_vertex1)]
    else:
        missing_vertices = polygon1_coords[
                           polygon1_coords.index(common_vertex1) + 1:polygon1_coords.index(common_vertex2)]
    if not len(missing_vertices) == 0:
        polygon2_coords = list(polygon2.exterior.coords)
        before_index = polygon2_coords[:common_vertex_index1 + 1]
        after_index = polygon2_coords[common_vertex_index2:]
        new_polygon2_coords = before_index + missing_vertices + after_index
    else:
        polygon2_coords = list(polygon2.exterior.coords)
        new_polygon2_coords = polygon2_coords
    return Polygon(new_polygon2_coords)

def reorder_based_on_common_vertex(poly1_wkt, poly2_wkt):
    poly1 = wkt.loads(poly1_wkt)
    poly2 = wkt.loads(poly2_wkt)

    common_vertices = list(set(poly1.boundary.coords[:-1]).intersection(set(poly2.boundary.coords[:-1])))
    reorder_poly1 = reorder_polygon(poly1_wkt,common_vertices)
    reorder_poly2 = reorder_polygon(poly2_wkt,common_vertices)

    return reorder_poly1,reorder_poly2



from shapely.geometry import Polygon
from shapely.wkt import loads as load_wkt


from shapely.geometry import Point

def get_vertex_index_within_tolerance(polygon_wkt, vertex, tolerance):
    polygon = load_wkt(polygon_wkt)
    point = Point(vertex)
    for i, coord in enumerate(polygon.exterior.coords):
        if point.distance(Point(coord)) <= tolerance:
            return i
    return None

def get_vertex_index(polygon, vertex):
    for i, coord in enumerate(polygon.exterior.coords):
        if coord == vertex:
            return i
    return None
def calculate_vertex_sum(polygon, vertex_list):
    min_vertex_sum = float('inf')
    min_start_index = 0

    for i in range(len(polygon.exterior.coords) - 1):  # Iterate up to the second-to-last vertex
        start_index = i
        vertex_sum = 0
        for vertex in vertex_list:
            ver_index = get_vertex_index(polygon, vertex)
            len_pol = len(polygon.exterior.coords)-1
            vertex_sum += (ver_index - start_index) % len_pol
        if vertex_sum < min_vertex_sum:
            min_vertex_sum = vertex_sum
            min_start_index = start_index

    return min_start_index

def reorder_polygon(wkt_polygon, vertex_list):
    polygon = load_wkt(wkt_polygon)
    start_index = calculate_vertex_sum(polygon, vertex_list)
    new_poly2=change_starting_vertex(polygon,start_index)
    return new_poly2.wkt


def change_starting_vertex(polygon, new_start_index):
    num_points = len(polygon.exterior.coords)

    if new_start_index >= num_points or new_start_index < 0:
        print("Invalid index!")
        return None

    new_coords = list(polygon.exterior.coords[:-1])
    new_coords = new_coords[new_start_index:] + new_coords[:new_start_index]

    new_polygon = Polygon(new_coords)
    return new_polygon

def count_coordinates(geometry):
    count = 0
    if isinstance(geometry, Polygon):
        count += len(geometry.exterior.coords)
        for interior in geometry.interiors:
            count += len(interior.coords)
    elif isinstance(geometry, MultiPolygon):
        for polygon in geometry.geoms:
            count += len(polygon.exterior.coords)
            for interior in polygon.interiors:
                count += len(interior.coords)
    return count


def get_starting_vertex(wkt_polygon):
    polygon = load_wkt(wkt_polygon)
    exterior_ring = polygon.exterior
    starting_vertex = exterior_ring.coords[0]  # First vertex of the exterior ring
    return starting_vertex

def modify_polygons(polygon1, polygon2,tolerance):
    polygon2 = Polygon(polygon2.exterior.coords[::-1])

    common_vertices = list(set(polygon1.boundary.coords[:-1]).intersection(set(polygon2.boundary.coords[:-1])))
    common_vertices.sort(key=lambda vertex: list(polygon2.exterior.coords).index(vertex))

    polygon1,polygon2 = add_vertex_with_one_side_common(polygon1,polygon2,tolerance)
    polygon2,polygon1 = add_vertex_with_one_side_common(polygon2,polygon1,tolerance)


    new_polygon2 = polygon2
    for i in range(len(common_vertices) - 1):
        common_vertex1 = common_vertices[i]
        common_vertex2 = common_vertices[i + 1]
        common_vertex_index1 = list(polygon2.exterior.coords).index(common_vertex1)
        common_vertex_index2 = list(polygon2.exterior.coords).index(common_vertex2)
        new_polygon2 = add_missing_vertices(polygon1, new_polygon2, common_vertex_index1, common_vertex_index2, common_vertex1, common_vertex2)

    new_polygon2 = Polygon(new_polygon2.exterior.coords[::-1])

    return polygon1, new_polygon2


def remove_duplicate_coordinates(geometry):
    if isinstance(geometry, Polygon):
        return remove_duplicate_polygon_coordinates(geometry)
    elif isinstance(geometry, MultiPolygon):
        return MultiPolygon([remove_duplicate_polygon_coordinates(polygon) for polygon in geometry.geoms])
    else:
        return geometry


def fix_ring_orientation(ring):
    # Ensure the ring is oriented counter-clockwise
    if ring.is_ccw:
        return ring
    else:
        return ring.coords[::-1]

def remove_duplicate_polygon_coordinates(polygon):

    exterior_coords = polygon.exterior.coords
    cleaned_exterior_coords = remove_duplicate_coords_except_ends(exterior_coords)

    interior_coords = []
    for interior in polygon.interiors:
        interior_coords.append(remove_duplicate_coords_except_ends(interior.coords))

    return Polygon(cleaned_exterior_coords, interior_coords)


def remove_duplicate_coords_except_ends(coords):
    seen_coords = set()
    cleaned_coords = []
    for coord in coords:
        rounded_coord = (round(coord[0], 4), round(coord[1], 4))
        if len(coords) >= 4 and (rounded_coord not in seen_coords or coord == coords[0] or coord == coords[-1]):
            cleaned_coords.append(coord)
            seen_coords.add(rounded_coord)
    return cleaned_coords


def remove_invalid_interior_rings(geometry):
    if isinstance(geometry, Polygon):
        return remove_invalid_polygon_interior_rings(geometry)
    elif isinstance(geometry, MultiPolygon):
        return MultiPolygon([remove_invalid_polygon_interior_rings(polygon) for polygon in geometry.geoms])
    else:
        return geometry


def remove_invalid_polygon_interior_rings(polygon):
    exterior = polygon.exterior
    valid_interiors = [interior for interior in polygon.interiors if interior.is_valid and interior.area >= 1.0]
    return Polygon(exterior, valid_interiors)


def clean_topological_errors(geometry):
    if isinstance(geometry, Polygon):
        return clean_polygon_topological_errors(geometry)
    elif isinstance(geometry, MultiPolygon):
        return MultiPolygon([clean_polygon_topological_errors(polygon) for polygon in geometry.geoms])
    else:
        return geometry


def clean_polygon_topological_errors(polygon):
    try:
        # Use buffer(0) to clean topological errors
        cleaned_polygon = polygon.buffer(0)
        if isinstance(cleaned_polygon, Polygon):
            return cleaned_polygon
        elif isinstance(cleaned_polygon, MultiPolygon) and len(cleaned_polygon.geoms) == 1:
            return cleaned_polygon.geoms[0]
        else:
            raise ValueError("Unable to clean topological errors.")
    except Exception as e:
        print(f"Error cleaning topological errors: {e}")
        return polygon


from shapely.geometry import Polygon, Point
import numpy as np
from shapely import wkt

from shapely.geometry import Point, Polygon
import numpy as np
import shapely.wkt as wkt


def get_indexes_to_keep(total_indexes, indexes_to_remove):
    indexes_to_keep = []
    for i in range(total_indexes):
        if i not in indexes_to_remove:
            indexes_to_keep.append(i)
    return indexes_to_keep


def remove_overshoot(polygon, vertex_distance_threshold=0.0001, area_tolerance=0.01):
    # Parse WKT polygon
    initial_polygon = wkt.loads(polygon)
    polygon = initial_polygon

    # Calculate initial area
    initial_area = polygon.area

    # List to store indexes of vertices to be removed
    indexes_to_remove = []

    # Iterate over each pair of vertices in the polygon
    for i in range(len(polygon.exterior.coords) - 1):
        for j in range(i + 2, len(polygon.exterior.coords) - 2):
            vertex1 = Point(polygon.exterior.coords[i])
            vertex2 = Point(polygon.exterior.coords[j])
            # If the distance between vertex i and j is within the threshold
            if vertex1.distance(vertex2) < vertex_distance_threshold:
                # Mark the indexes between i and j for removal
                indexes_to_remove.extend(range(i + 1, j))
                break  # No need to check further

    # Remove duplicate indexes
    indexes_to_remove = list(set(indexes_to_remove))

    # Remove vertices marked for removal
    if indexes_to_remove:
        total_indexes = len(polygon.exterior.coords) - 1
        indexes_to_keep = get_indexes_to_keep(total_indexes, indexes_to_remove)

        # Check if there are at least four coordinates
        if len(indexes_to_keep) >= 4:
            # Create a new polygon
            polygon_coords = np.array(polygon.exterior.coords[:-1])
            polygon_coords = polygon_coords[indexes_to_keep]

            # Ensure the new polygon has the same first and last vertex
            polygon_coords = np.vstack([polygon_coords, polygon_coords[0]])

            keep_polygon = Polygon(polygon_coords)

            # Calculate new area
            new_area = keep_polygon.area

            # Check if area change is within tolerance
            if abs(new_area - initial_area) <= area_tolerance:
                return keep_polygon
            else:
                # Delete the indexes of vertices to keep instead of printing a message
                # Create a new polygon
                polygon_coords = np.array(polygon.exterior.coords[:-1])
                polygon_coords = polygon_coords[indexes_to_remove]

                # Ensure the new polygon has the same first and last vertex
                polygon_coords = np.vstack([polygon_coords, polygon_coords[0]])

                rem_polygon = Polygon(polygon_coords)

                # Calculate new area
                new_area = rem_polygon.area

                # Check if area change is within tolerance
                if abs(new_area - initial_area) <= area_tolerance:
                    return rem_polygon

    return polygon


def remove_overshoot_old(polygon, vertex_distance_threshold=0.0001):
    # Parse WKT polygon
    polygon = wkt.loads(polygon)

    # List to store indexes of vertices to be removed
    indexes_to_remove = []

    # Iterate over each pair of vertices in the polygon
    for i in range(len(polygon.exterior.coords) - 1):
        for j in range(i + 2, len(polygon.exterior.coords) - 2):
            vertex1 = Point(polygon.exterior.coords[i])
            vertex2 = Point(polygon.exterior.coords[j])
            # If the distance between vertex i and j is within the threshold
            if vertex1.distance(vertex2) < vertex_distance_threshold:
                # Mark the indexes between i and j for removal
                indexes_to_remove.extend(range(i + 1, j))
                break  # No need to check further

    # Remove duplicate indexes
    indexes_to_remove = list(set(indexes_to_remove))

    # Remove vertices marked for removal
    if indexes_to_remove:
        polygon_coords = np.array(polygon.exterior.coords[:-1])
        polygon_coords = np.delete(polygon_coords, indexes_to_remove, axis=0)

        # Check if there are at least four coordinates
        if len(polygon_coords) >= 4:
            polygon = Polygon(polygon_coords)
        else:
            # Handle the case where there are not enough coordinates
            print("Not enough coordinates to form a valid LinearRing.")

    return polygon

def add_vertex_with_one_side_common(polygon1_wkt,polygon2_wkt,tol):
    # Parse the WKT representations into Shapely Polygon objects
    polygon1 = polygon1_wkt
    polygon2 = polygon2_wkt
    # polygon1 = loads(polygon1_wkt)
    # polygon2 = loads(polygon2_wkt)

    # Define tolerance distance from the side of the second polygon
    tolerance = tol  # Example tolerance distance, adjust as needed

    # Find the common vertices between the polygons
    common_vertices = list(set(polygon1.boundary.coords[:-1]).intersection(set(polygon2.boundary.coords[:-1])))

    # Exclude the common vertices if found
    if common_vertices:
        polygon1_coords = [vertex for vertex in polygon1.exterior.coords if vertex not in common_vertices]
    else:
        polygon1_coords = polygon1.exterior.coords

    # Iterate over the vertices of the first polygon, excluding common vertices if found
    for vertex1 in polygon1_coords:
        # Create a Point object for the vertex
        point1 = Point(vertex1)

        # Iterate over the sides of the second polygon
        for i in range(len(polygon2.exterior.coords) - 1):
            # Create line segments for each side of the second polygon
            side_start = polygon2.exterior.coords[i]
            side_end = polygon2.exterior.coords[i + 1]

            # Calculate the distance from the point to the line segment
            # vector AB
            vec_AB = np.array(side_end) - np.array(side_start)
            # vector AP
            vec_AP = np.array(vertex1) - np.array(side_start)
            # Projection of AP onto AB
            proj_AP_AB = np.dot(vec_AP, vec_AB) / np.dot(vec_AB, vec_AB) * vec_AB
            # perpendicular vector from P to line AB
            perp_vec = vec_AP - proj_AP_AB

            # Check if the projection is within the line segment bounds
            if 0 <= np.dot(vec_AB, proj_AP_AB) <= np.dot(vec_AB, vec_AB):
                # # Calculate the distance only if the perpendicular lies within the side and outside the side
                # if np.linalg.norm(perp_vec) < np.linalg.norm(vec_AB) and np.dot(vec_AB, perp_vec) >= 0:
                    # Calculate the distance
                    distance = np.linalg.norm(perp_vec)

                    # Check if the distance is within the tolerance
                    if distance < tolerance:
                        # Add the point to the second polygon
                        polygon2_points = list(polygon2.exterior.coords)
                        polygon2_points.insert(i + 1, vertex1)
                        polygon2 = Polygon(polygon2_points)
                        break  # Stop iterating over sides if point is within tolerance

    return polygon1,polygon2



import datetime
def save_to_file(filename, parcelid, geometry,officename):
    # Get current date and time
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Convert geometry to string if it's not already
    if not isinstance(geometry, str):
        geometry = str(geometry)


    # Append parcel ID and geometry to the file
    with open(filename, "a") as file:
        file.write("\nCommit Time: ")
        file.write(current_time)
        file.write("\n")
        file.write(f"Office: {officename}\n")
        file.write(f"Parcel ID: {parcelid}\n")
        file.write("Geometry (WKT):")
        file.write(geometry)
        file.write("\n\n")  # Add a newline for better readability

# Define a global variable for the filename
FILE_NAME = "parcel_data.txt"


def revert_to_original_start_vertex(new_polygon_wkt,old_polygon_wkt,tolerance):
    start_vertex = get_starting_vertex(old_polygon_wkt)
    get_index_in_new = get_vertex_index_within_tolerance(new_polygon_wkt,start_vertex,tolerance)
    new_polygon = load_wkt(new_polygon_wkt)
    new_polygon_wkt = change_starting_vertex(new_polygon,get_index_in_new)

    return Polygon(new_polygon_wkt)
