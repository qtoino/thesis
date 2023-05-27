import csv
from math import sqrt
import random

def distance_to_origin(x, y, z):
    return sqrt(x ** 2 + y ** 2 + z ** 2)

def separate_csv_rows(input_file, output_file1, output_file2, threshold):
    with open(input_file, newline='') as csvfile:
        reader = list(csv.reader(csvfile, delimiter=','))  # Convert reader to a list
        header = reader[0]  # Store the header row

        random.shuffle(reader[1:])  # Shuffle the list of rows except the header

        near_rows = [header]  # Add the header row to near_rows
        far_rows = [header]  # Add the header row to far_rows
        near_count = 0
        for row in reader[1:]:
            try:
                x, y, z, radius, color, sound = float(row[0]), float(row[1]), float(row[2]), float(row[3]), row[4], row[5]
                distance = distance_to_origin(x, y, z)

                if distance < threshold:
                    if near_count < 200:  # Check if the near_rows count is less than 300
                        near_rows.append(row)
                        near_count += 1
                else:
                    far_rows.append(row)
            except:
                near_rows.append(row)
                far_rows.append(row)

        with open(output_file1, 'w', newline='') as close:
            writer1 = csv.writer(close, delimiter=',')
            writer1.writerows(near_rows)

        with open(output_file2, 'w', newline='') as far:
            writer2 = csv.writer(far, delimiter=',')
            writer2.writerows(far_rows)

input_csv = 'output.csv'
output_csv_near = 'near_points.csv'
output_csv_far = 'far_points.csv'
distance_threshold = 150.0

separate_csv_rows(input_csv, output_csv_near, output_csv_far, distance_threshold)
