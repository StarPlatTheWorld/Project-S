# --- Imports Python Modules into App Instance ---
from flask import Flask, jsonify, request, make_response
from pymongo import MongoClient
import json
from flask_cors import CORS
from bson import ObjectId
from werkzeug.utils import secure_filename
import os

# --- Initialises the Flask app instance and applies CORS to all endpoints. ---
app = Flask(__name__)
# --- CORS is an additional extension for Flask. This allows for Cross-Origin Resource Sharing, which allows the back-end API to interact with the front-end application, and vice versa. ---
CORS(app)

# UPLOAD_FOLDER = 'uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# ALLOWED_EXTENSIONS = {'txt', 'json'}

# --- Sets up the connection to MongoDB utilising pymongo. This allows both the database and collection to be accessed directly by the API, allowing for data manipulation and queries. ---
client = MongoClient("localhost", 27017)
db = client["ProjectS"]
package_collection = db["packages"]

# def allowed_file_types(filename):
#     return '.' in filename and \
#             filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- The Index API route. ---
@app.route("/api/", methods = ['GET'])
def index():
    return jsonify()

# @app.route("/api/upload", methods = ['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400
#     if file and allowed_file_types(file.filename):
#         filename = secure_filename(file.filename)
#         file_path = (os.path.join(app.config['UPLOAD_FOLDER'], filename))
#         file.save(file_path)

#         with open(file_path, 'r') as f:
#             file_contents = f.read()
#             collection = package_collection
#             query_results = collection.find({'match_field': {
#                 '$regex': file_contents
#             }})
#             scan_results = list(query_results)
#         return jsonify({'message': 'Your file has been uploaded sucessfully', 'results': scan_results}), 200
#     else:
#         return jsonify({'error': 'Invalid file extension. Please choose .txt or .json'}), 400

# --- The Scan Results API route. ---
@app.route("/api/results")
def scanResults():
    return jsonify()

# --- The Package List API route. ---
@app.route("/api/packages", methods = ['GET'])
def get_packList():
    packages = list(package_collection.find())

    for package in packages:
        package['_id'] = str(package['_id'])

    return jsonify(packages)

# --- IF statement to allow the app to run with debug mode enabled when __name__ == __main__. 
if __name__ == "__main__":
    app.run(debug=True)