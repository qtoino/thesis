import sqlite3
import os
import csv

conn = sqlite3.connect('mydatabase.db')

c = conn.cursor()

c.execute("""DROP TABLE IF EXISTS audio_files;""")

c.execute("""CREATE TABLE audio_files (
            id INTEGER PRIMARY KEY,
            name TEXT,
            class TEXT,
            x FLOAT,
            y FLOAT,
            z FLOAT,
            radius INTEGER,
            path TEXT,
            favorite INTEGER
            )""")

# Name of the CSV file
csv_file = './output-2.csv'

# Directory path where the audio files are located
dir_path = './ESC50/audio'

# Open the CSV file for reading
with open(csv_file, mode='r') as f:
    reader = csv.DictReader(f)
    
    i = 0
    # Loop over each row in the CSV file
    for row in reader:
        i = i+1
        # Extract the data from the row
        try:
            x = float(row['x'])
            y = float(row['y'])
            z = float(row['z'])
        except:
            x = "null"
        radius = row['radius']
        color = row['color']
        filename = row['sound']

        # Check if the file is an audio file (e.g. mp3, wav, etc.)
        if filename.endswith('.mp3') or filename.endswith('.wav'):
            # # Do something with the data (e.g. process the audio file)
            # with open(os.path.join(dir_path, filename), 'rb') as audio_file:
            #     audio_data = audio_file.read()
                # Insert the audio file data into the "audio_files" table
                
                if x == "null":
                    c.execute("INSERT INTO audio_files (name, path) VALUES (?, ?)",
                            (filename, "./audio/ESC50/"))
                else:
                    if i % 2 :
                        c.execute("INSERT INTO audio_files (name, x, y, z, radius, class, path, favorite) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (filename, x, y, z, radius, 'orange', "./audio/ESC50/", 0))
                    else:
                        c.execute("INSERT INTO audio_files (name, x, y, z, radius, class, path, favorite) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (filename, x, y, z, radius, 'blue', "./audio/ESC50/", 0))


# Commit the changes to the database
conn.commit()

# Close the database connection
conn.close()