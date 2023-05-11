import csv
from math import sqrt

def distance_to_origin(x, y, z):
    return sqrt(x ** 2 + y ** 2 + z ** 2)

def separate_csv_rows(input_file, output_file1, output_file2, threshold):
    with open(input_file, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        near_rows = []
        far_rows = []

        for row in reader:
            try:
                x, y, z, radius, color, sound = float(row[0]), float(row[1]), float(row[2]), float(row[3]), row[4], row[5]
                distance = distance_to_origin(x, y, z)

                if distance < threshold:
                    near_rows.append(row)
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
distance_threshold = 170.0

separate_csv_rows(input_csv, output_csv_near, output_csv_far, distance_threshold)