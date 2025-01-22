import math

# Function to calculate the corner coordinates
def get_corners(mapsheet_number):
    first_parts = int(mapsheet_number[:3])
    second_parts = int(get_part_or_zero(mapsheet_number[3:7].strip()))
    third_part = int(get_part_or_zero(mapsheet_number[7:].strip()))

    first_part = first_parts if 0 < first_parts < 181 else None
    second_part = second_parts if 0 < second_parts < 1601 else None

    first_1 = reduce_first(first_part)
    second_1 = reduce_second(second_part)
    third_1 = reduce_second(third_part)

    first2 = int(first_1 / 6)
    first3 = int(first_1 % 6)

    second2 = int(second_1 / 40)
    second3 = int(second_1 % 40)

    third2 = div_third(mapsheet_number, third_1)
    third3 = mod_third(mapsheet_number, third_1)

    scale = evaluate_scale(mapsheet_number)

    top_north = get_top_north(scale, first2, second2, third2)
    bottom_north = get_bottom_north(scale, top_north)

    left_east = get_left_east(scale, first3, second3, third3)
    right_east = get_right_east(scale, left_east)

    if first_part is None:
        raise ValueError("Invalid mapsheet number. First part: {}".format(first_parts))
    if second_part is None:
        raise ValueError("Invalid mapsheet number. Second part: {}".format(second_parts))

    third_digit1, third_digit2 = process_third_part(third_part)

    if third_digit1 is None or third_digit2 is None:
        raise ValueError("Invalid mapsheet number. Third Part: {}".format(third_part))

    # Calculate corners coordinates
    top_left = (round(left_east), round(top_north))
    bottom_left = (round(left_east), round(bottom_north))
    top_right = (round(right_east), round(top_north))
    bottom_right = (round(right_east), round(bottom_north))

    # Return corner coordinates if needed
    return top_left, bottom_left, top_right, bottom_right, scale

def reduce_first(value):
    result = value % 60
    if result == 0:
        return 60 - 1
    else:
        return result - 1

def reduce_second(value):
    if value == 0:
        return value
    else:
        return value - 1

def div_third(mapsheet, third):
    if len(str(mapsheet)) == 8:
        return int(third / 2)
    else:
        return int(third / 5)

def mod_third(mapsheet, third):
    if len(str(mapsheet)) == 8:
        return int(third % 2)
    else:
        return int(third % 5)

def evaluate_scale(mapsheetno):
    left_part = int(mapsheetno[:3])

    if 0 < left_part < 181 and len(mapsheetno) == 3:
        return 100000
    elif 0 < left_part < 181 and len(mapsheetno) == 7:
        mid_part = int(mapsheetno[3:7])
        if 0 < mid_part < 1601:
            return 2500
    elif 0 < left_part < 181 and len(mapsheetno) == 8:
        mid_part = int(mapsheetno[3:7])
        last_part = int(mapsheetno[7])
        if 0 < mid_part < 1601 and 0 < last_part < 5:
            return 1250
    elif 0 < left_part < 181 and len(mapsheetno) == 9:
        mid_part = int(mapsheetno[3:7])
        last_two_digits = int(mapsheetno[7:9])
        if 0 < mid_part < 1601 and 0 < last_two_digits < 26:
            return 500

    return "E"

def get_top_north(scale, first2, second2, third2):
    if scale == 500:
        return 3400000 - (first2 * 50000) - (second2 * 1250) - (third2 * 250)
    else:
        return 3400000 - (first2 * 50000) - (second2 * 1250) - (third2 * 625)

def get_bottom_north(scale, top_north):
    if scale == 500:
        return top_north - 250
    elif scale == 1250:
        return top_north - 625
    else:
        return top_north - 1250

def get_left_east(scale, first3, second2, third3):
    if scale == 500:
        return 350000 + (first3 * 50000) + (second2 * 1250) + (third3 * 250)
    else:
        return 350000 + (first3 * 50000) + (second2 * 1250) + (third3 * 625)

def get_right_east(scale, left_east):
    if scale == 500:
        return left_east + 250
    elif scale == 1250:
        return left_east + 625
    else:
        return left_east + 1250

def get_corners_adjusted(mapsheet_number):
    top_left, bottom_left, top_right, bottom_right, scale = get_corners(mapsheet_number)
    first_part = int(mapsheet_number[:3])

    if first_part < 61:
        top_left = (top_left[0] + 300000, top_left[1])
        top_right = (top_right[0] + 300000, top_right[1])
        bottom_left = (bottom_left[0] + 300000, bottom_left[1])
        bottom_right = (bottom_right[0] + 300000, bottom_right[1])
    elif first_part > 120:
        top_left = (top_left[0] - 300000, top_left[1])
        top_right = (top_right[0] - 300000, top_right[1])
        bottom_left = (bottom_left[0] - 300000, bottom_left[1])
        bottom_right = (bottom_right[0] - 300000, bottom_right[1])

    return top_left, bottom_left, top_right, bottom_right, scale

def process_third_part(third_part):
    third_part_str = str(third_part)

    if len(third_part_str) == 1 and int(third_part_str) < 5:
        return int(third_part_str), 0  # Return single digit, no second value
    elif len(third_part_str) == 2 and int(third_part_str) < 26:
        return 0, int(third_part_str)  # Return two digits separately
    else:
        return None, None  # If third part is not 1 or 2 digits, return None

def get_part_or_zero(value):
    try:
        return str(int(value))
    except ValueError:
        return '0'

# Main program
def main():
    try:
        mapsheet_number = input("Enter the mapsheet number (format: row-col): ")
        top_left, bottom_left, top_right, bottom_right, scale = get_corners(mapsheet_number)

        print("Top-Left Coordinate: {}".format(top_left))
        print("Bottom-Left Coordinate: {}".format(bottom_left))
        print("Top-Right Coordinate: {}".format(top_right))
        print("Bottom-Right Coordinate: {}".format(bottom_right))
        print("Scale: {}".format(scale))

    except ValueError as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
