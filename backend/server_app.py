from flask import Flask, abort, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
import torch
import json
import sqlite3
import base64
import numpy as np

from backend import GenerativeF, load_model, load_model_s

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


model = load_model()

model_s = load_model_s() 

generate = GenerativeF(model, model_s)

# audio_files_cache = None

@app.route('/input', methods = ["POST"])
@cross_origin()
def input():
    
    data = request.data.decode('utf-8')  # Decode the data to string
    data_dict = json.loads(data)
    print(data_dict)
    # x = torch.randn((1, 1, 128, 512))
    # ret, generated_i = generate.audioAsInput(x)
        
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

    filepath, generated_number = generate.coorAsInput(data_dict)

    audio_name = filepath.split("/")[-1]

    # path_to_file = "./audio/generated/" 
    
    # return send_from_directory(path_to_file, audio_name)

    with open(f"./static/generated/{audio_name}", "rb") as f:
        audio_data = f.read()

    # Encode the audio data in Base64
    audio_data_base64 = base64.b64encode(audio_data).decode("utf-8")

    # Return a JSON object containing the audio_name and the Base64 encoded audio data
    response = {
        "audio_name": audio_name,
        "audio_data": audio_data_base64
    }
    return jsonify(response)


@app.route('/addnew2', methods = ["POST"])
@cross_origin()
def addnew2():
    
    data = request.data.decode('utf-8')  # Decode the data to string
    data_dict = json.loads(data)

    filepath, generated_number = generate.coorAsInput(data_dict)

    audio_name = filepath.split("/")[-1]

    # path_to_file = "./audio/generated/" 
    
    # return send_from_directory(path_to_file, audio_name)

    response = {
        "audio_name": audio_name,
        # "audio_data": audio_data_base64
    }
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()

    c.execute("INSERT INTO audio_files (name, x, y, z, radius, color, class, path, favorite) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (audio_name, data_dict["x"], data_dict["y"], data_dict["z"], 1, 'red', 'generated', "https://thesis-production-0069.up.railway.app/static/generated/", 0))
   
    # Commit the changes to the database
    conn.commit()
    conn.close()

    return jsonify(response)


@app.route('/interpole', methods = ["POST"])
@cross_origin()
def interpol():
    
    data = request.data.decode('utf-8')  # Decode the data to string
    data_dict = json.loads(data)
    
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()

    c.execute('SELECT name, path FROM audio_files WHERE x=? AND y=? AND z=?', (data_dict["ball1_x"], data_dict["ball1_y"], data_dict["ball1_z"]))
    audio_file_a = c.fetchone()
    
    c.execute('SELECT name, path FROM audio_files WHERE x=? AND y=? AND z=?', (data_dict["ball2_x"], data_dict["ball2_y"], data_dict["ball2_z"]))
    audio_file_b = c.fetchone()
    
    ball_a = np.array([float(data_dict["ball1_x"]), float(data_dict["ball1_y"]), float(data_dict["ball1_z"])])
    ball_b = np.array([float(data_dict["ball2_x"]), float(data_dict["ball2_y"]), float(data_dict["ball2_z"])])
    ball_c = np.array([float(data_dict["x"]), float(data_dict["y"]), float(data_dict["z"])])

    dist_a_c = np.linalg.norm(ball_c - ball_a)
    dist_b_c = np.linalg.norm(ball_c - ball_b)
    total_distance = dist_a_c + dist_b_c

    influence_a = (dist_b_c / total_distance)
    influence_b = (dist_a_c / total_distance)
    
    print(audio_file_a[0])
    
    filepath, generated_number = generate.interpolation(audio_file_a, audio_file_b, influence_a, influence_b)
    
    audio_name = filepath.split("/")[-1]
    
    # path_to_file = "./audio/generated/" 
    
    # return send_from_directory(path_to_file, audio_name)
    with open(f"./static/generated/{audio_name}", "rb") as f:
        audio_data = f.read()

    # Encode the audio data in Base64
    audio_data_base64 = base64.b64encode(audio_data).decode("utf-8")

    # Return a JSON object containing the audio_name and the Base64 encoded audio data
    response = {
        "audio_name": audio_name,
        "audio_data": audio_data_base64
    }

    # Commit the changes to the database
    conn.commit()
    conn.close()
    
    
    return jsonify(response)

@app.route('/interpole2', methods = ["POST"])
@cross_origin()
def interpol2():
    
    data = request.data.decode('utf-8')  # Decode the data to string
    data_dict = json.loads(data)
    
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()

    c.execute('SELECT name, path FROM audio_files WHERE x=? AND y=? AND z=?', (data_dict["ball1_x"], data_dict["ball1_y"], data_dict["ball1_z"]))
    audio_file_a = c.fetchone()
    
    c.execute('SELECT name, path FROM audio_files WHERE x=? AND y=? AND z=?', (data_dict["ball2_x"], data_dict["ball2_y"], data_dict["ball2_z"]))
    audio_file_b = c.fetchone()
    
    ball_a = np.array([float(data_dict["ball1_x"]), float(data_dict["ball1_y"]), float(data_dict["ball1_z"])])
    ball_b = np.array([float(data_dict["ball2_x"]), float(data_dict["ball2_y"]), float(data_dict["ball2_z"])])
    ball_c = np.array([float(data_dict["x"]), float(data_dict["y"]), float(data_dict["z"])])

    dist_a_c = np.linalg.norm(ball_c - ball_a)
    dist_b_c = np.linalg.norm(ball_c - ball_b)
    total_distance = dist_a_c + dist_b_c

    influence_a = (dist_b_c / total_distance)
    influence_b = (dist_a_c / total_distance)
    
    print(audio_file_a[0])
    
    filepath, generated_number = generate.interpolation(audio_file_a, audio_file_b, influence_a, influence_b)
    
    audio_name = filepath.split("/")[-1]
    
    # path_to_file = "./audio/generated/" 
    
    # # return send_from_directory(path_to_file, audio_name)
    # with open(f"./static/generated/{audio_name}", "rb") as f:
    #     audio_data = f.read()

    # # Encode the audio data in Base64
    # audio_data_base64 = base64.b64encode(audio_data).decode("utf-8")

    # Return a JSON object containing the audio_name and the Base64 encoded audio data
    response = {
        "audio_name": audio_name,
        # "audio_data": audio_data_base64
    }

    c.execute("INSERT INTO audio_files (name, x, y, z, radius, color, class, path, favorite) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (audio_name, data_dict["x"], data_dict["y"], data_dict["z"], 1, 'red', 'generated', "https://thesis-production-0069.up.railway.app/static/generated/", 0))
   
    # Commit the changes to the database
    conn.commit()
    conn.close()
    
    return jsonify(response)

@app.route('/addpath', methods = ["POST"])
@cross_origin()
def addpath():
    data = request.data.decode('utf-8')  # Decode the data to string
    data_dict = json.loads(data)

    # write to database
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()

    c.execute("INSERT INTO audio_files (name, x, y, z, radius, color, class, path, favorite) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (data_dict["name"], data_dict["x"], data_dict["y"], data_dict["z"], 1, 'red', 'generated', data_dict["url"], 0))
   
    # Commit the changes to the database
    conn.commit()
    conn.close()

    return jsonify({"message": "Audio file added successfully"}) 

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
# define the route for retrieving  audio file
@app.route('/all-audio-files', methods=['GET'])
@cross_origin()
def get_all_audio_files():
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()

    c.execute('SELECT id, name, color, class, x, y, z, radius, path, favorite FROM audio_files')
    audio_files = c.fetchall()
    if audio_files:
        # create a list of dictionaries from the list of tuples
        audio_data = []
        for audio_file in audio_files:
            audio_data.append({
                'id': audio_file[0],
                'name': audio_file[1],
                'color': audio_file[2],
                'class': audio_file[3],
                'x': audio_file[4],
                'y': audio_file[5],
                'z': audio_file[6],
                'radius': audio_file[7],
                'path': audio_file[8],
                'favorite': audio_file[9],
            })
        # Close the database connection
        conn.close()
        return jsonify({'audio_data': audio_data})
    else:
        # Close the database connection
        conn.close()
        return jsonify({'error': 'Audio file not found'})

@app.route('/delete-generated-sounds', methods=['POST'])
def delete_generated_sounds():
    try:
        conn = sqlite3.connect('mydatabase.db')
        c = conn.cursor()
        c.execute("DELETE FROM audio_files WHERE name LIKE 'GD_%'")
        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        print(e)
        return jsonify({'status': 'error', 'message': 'An error occurred while deleting generated sounds.'})

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
    app.run(host='0.0.0.0', port=8000)
    

    