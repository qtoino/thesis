from flask import Flask, abort, request, jsonify
from flask_cors import CORS, cross_origin
import torch
import json
import sqlite3
import base64

from backend import GenerativeF

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


generated_i = 0

generate = GenerativeF(generated_i)

@app.route('/input', methods = ["POST"])
@cross_origin()
def input():
    
    data = request.data.decode('utf-8')  # Decode the data to string
    data_dict = json.loads(data)
    print(data_dict)
    # x = torch.randn((1, 1, 128, 512))
    # ret = generate.audioAsInput(x)
        
    # try:
    #     response_data = jsonify({"audio_file": ret, "color": "red"})
    # except:
    #     abort(400)

    # print(response_data)    
    return jsonify({"message": "Success"})

@app.route('/addnew', methods = ["POST"])
@cross_origin()
def addnew():
    
    data = request.data.decode('utf-8')  # Decode the data to string
    data_dict = json.loads(data)

    filepath = generate.coorAsInput(data_dict)

    audio_name = filepath.split("/")[-1]
        
    # write to database
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()

    c.execute("INSERT INTO audio_files (name, x, y, z, radius, class, path, favorite) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (audio_name, data_dict["x"], data_dict["y"], data_dict["z"], 1, 'red', "./ESC50/generated/", 0))
   
    # Commit the changes to the database
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Success"})
    

@app.route('/remove', methods=['POST'])
@cross_origin()
def remove():
    data = request.data.decode('utf-8')  # Decode the data to string
    data_dict = json.loads(data)
    
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()

    c.execute('DELETE FROM audio_files WHERE name = ?', (data_dict["filename"],))
    conn.commit()
    
    return jsonify({"message": "Audio file removed successfully"}) 

@app.route('/favorite', methods=['POST'])
@cross_origin()
def add_favorite():
    data = request.data.decode('utf-8')  # Decode the data to string
    data_dict = json.loads(data)

    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    
    c.execute("UPDATE audio_files SET favorite = ? WHERE name = ?", (1, data_dict["filename"]))
    conn.commit()

    return jsonify({"message": "Audio file added to favorites successfully"}) 

@app.route('/unfavorite', methods=['POST'])
@cross_origin()
def remove_favorite():
    data = request.data.decode('utf-8')  # Decode the data to string
    data_dict = json.loads(data)

    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    
    c.execute("UPDATE audio_files SET favorite = ? WHERE name = ?", (0, data_dict["filename"]))
    conn.commit()

    return jsonify({"message": "Audio file removed to favorites successfully"}) 


# # define the route for retrieving 1 audio file
# @app.route('/audio-file', methods=['POST'])
# @cross_origin()
# def get_audio_file():
#     conn = sqlite3.connect('mydatabase.db')
#     c = conn.cursor()
#     data = request.data.decode('utf-8')  # Decode the data to string
#     data_dict = json.loads(data)
#     print(data_dict)

#     c.execute('SELECT data FROM audio_files WHERE name= ?', (data_dict["soundFile"],))
#     audio_file = c.fetchone() [0]
#     if audio_file:
#         # Encode the audio data as a base64-encoded string
#         audio_data_b64 = base64.b64encode(audio_file).decode('utf-8')
#         # Close the database connection
#         conn.close()
#         return jsonify({'audio_data': audio_data_b64})
#     else:
#         # Close the database connection
#         conn.close()
#         return jsonify({'error': 'Audio file not found'})

# define the route for retrieving  audio file
@app.route('/all-audio-files', methods=['GET'])
@cross_origin()
def get_all_audio_files():
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()

    c.execute('SELECT id, name, class, x, y, z, radius, path, favorite FROM audio_files')
    audio_files = c.fetchall()
    if audio_files:
        # create a list of dictionaries from the list of tuples
        audio_data = []
        for audio_file in audio_files:
            audio_data.append({
                'id': audio_file[0],
                'name': audio_file[1],
                'color': audio_file[2],
                'x': audio_file[3],
                'y': audio_file[4],
                'z': audio_file[5],
                'radius': audio_file[6],
                'path': audio_file[7],
                'favorite': audio_file[8],
            })
        # Close the database connection
        conn.close()
        return jsonify({'audio_data': audio_data})
    else:
        # Close the database connection
        conn.close()
        return jsonify({'error': 'Audio file not found'})

@app.route('/favorite-audio-files', methods=['GET'])
@cross_origin()
def get_fav_audio_files():
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    
    c.execute('SELECT name FROM audio_files WHERE favorite = ?', (1,))
    audio_files = c.fetchall()
    if audio_files:
        conn.close()
        return jsonify({'audio_data': audio_files})
    else:
        # Close the database connection
        conn.close()
        return jsonify({'error': 'Audio file not found'}) 


@app.route('/health', methods = ["GET", "POST"])
@cross_origin()
def health():
    print("Hello")
    return {"test" : "test"}
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
    

    