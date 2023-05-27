import os
import random
import csv


def get_first_200_sounds():
    sound_files = []
    i = 0
    # Read the CSV file to exclude the first line
    with open('output.csv', 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the first line
        
        for row in csv_reader:
            if i == 0:
                term = row
            else:
                sound_files.append(row)
            i = i+1


    # Randomly shuffle the list of sound files
    random.shuffle(sound_files)

    term.append(sound_files)

    # Get the first 200 sound files
    first_200_sounds = sound_files[:200]
    print(first_200_sounds)

    return first_200_sounds

first_200_sounds = get_first_200_sounds()

