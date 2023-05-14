import sqlite3
import os
import csv

class_color_map = {
    'snares': '#ff355e',
    'claps': '#fd5b78',
    'clicks': '#ff6037',
    'hihat': '#ff9966',
    'perc': '#ff9933',
    'percussive': '#ffcc33',
    'crash': '#ffff66',
    'kick': '#ccff00',
    'rides': '#66ff66',
    'shaker': '#aaf0d1',
    'synth': '#16d0cb',
    'tom': '#50bfe6',
    'bongo': '#9c27b0',
    'tribal': '#ee34d2',
    'fx': '#ff00cc',
    'else': 'gray',
}

conn = sqlite3.connect('mydatabase.db')

c = conn.cursor()

c.execute("""DROP TABLE IF EXISTS audio_files;""")

c.execute("""CREATE TABLE audio_files (
            id INTEGER PRIMARY KEY,
            name TEXT,
            color TEXT,
            class TEXT,
            x FLOAT,
            y FLOAT,
            z FLOAT,
            radius INTEGER,
            path TEXT,
            favorite INTEGER
            )""")

# Name of the CSV file
csv_file = './near_points.csv'

# Directory path where the audio files are located
# dir_path = './ESC50/audio'

# Open the CSV file for reading
with open(csv_file, mode='r') as f:
    reader = csv.DictReader(f)
    
    
    # Loop over each row in the CSV file
    for row in reader:
        
        # Extract the data from the row
        try:
            x = float(row['x'])
            y = float(row['y'])
            z = float(row['z'])
        except:
            x = "null"
        radius = row['radius']
        color = row['color']
        filename = row['sound'].replace('&', '_')

        # Check if the file is an audio file (e.g. mp3, wav, etc.)
        if filename.endswith('.mp3') or filename.endswith('.wav'):
            # # Do something with the data (e.g. process the audio file)
            # with open(os.path.join(dir_path, filename), 'rb') as audio_file:
            #     audio_data = audio_file.read()
                # Insert the audio file data into the "audio_files" table
                
            if x == "null":
                c.execute("INSERT INTO audio_files (name, path) VALUES (?, ?)",
                        (filename, "./audio/VENGEWAV/"))
            else:
                # Check if the audio file already exists in the database
                c.execute("SELECT * FROM audio_files WHERE name = ?", (filename,))
                if c.fetchone() is None:
                    class_name_found = False
                    for class_name, class_color in class_color_map.items():
                        if class_name in filename.lower():
                            color = class_color
                            class_name_found = True
                            print(filename.lower())

                            c.execute("INSERT INTO audio_files (name, x, y, z, radius, color, class, path, favorite) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                    (filename, x, y, z, radius, color, class_name, "https://thesis-production-0069.up.railway.app/static/VENGEWAV/", 0))
                            break
                    
                    if not class_name_found:
                        c.execute("INSERT INTO audio_files (name, x, y, z, radius, color, class, path, favorite) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                (filename, x, y, z, radius, 'gray', "others", "https://thesis-production-0069.up.railway.app/static/VENGEWAV/", 0))
                        



# Commit the changes to the database
conn.commit()

# Close the database connection
conn.close()