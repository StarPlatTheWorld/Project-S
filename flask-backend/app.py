# --- Imports Python Modules into App Instance ---
from flask import Flask, jsonify, request, make_response
from pymongo import MongoClient
import json
import jwt
import bcrypt
import datetime
from functools import wraps
from flask_cors import CORS
from bson import ObjectId
from werkzeug.utils import secure_filename
from config import Config
import os

# --- Initialises the Flask app instance ---
app = Flask(__name__)

# --- Sets up configuration from an object, that has been imported from a separate config file --- 
app.config.from_object(Config)

# --- Retrieves secret key from our config file and assigns it to variable ---
secret_key = app.config['SECRET_KEY']

# --- CORS is an additional extension for Flask. This allows for Cross-Origin Resource Sharing, which allows the back-end API to interact with the front-end application, and vice versa. ---
CORS(app)

# UPLOAD_FOLDER = 'uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# ALLOWED_EXTENSIONS = {'txt', 'json'}

# --- Sets up the connection to MongoDB utilising pymongo. This allows both the database and collection to be accessed directly by the API, allowing for data manipulation and queries. ---
client = MongoClient("localhost", 27017)
db = client["ProjectS"]
package_collection = db["packages"]
staffList_collection = db["staffList"]

staff = [
    {
        "name": "Ethan",
        "username": "McFarlaneE1",
        "password": b"mcfar_1",
        "admin": True
    },
    {
        "name": "Ethan",
        "username": "McFarlaneE2",
        "password": b"mcfar_2",
        "admin": False
    }
]

for new_staff_member in staff:
    new_staff_member["password"] = bcrypt.hashpw(new_staff_member["password"], \
    bcrypt.gensalt())
    staffList_collection.insert_one(new_staff_member)

# def allowed_file_types(filename):
#     return '.' in filename and \
#             filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Sets up an authorization token utilising JWT. This generates a token for users trying to login to protected API routes. If no token is present, an error message with the 401 status code will be displayed. If a token is present, it will decode it using the token, secret key and the HS256 algorithm. If an invalid token has been used, an error message with a 401 status code will be displayed. If the token matches an administrator account, it will be given access to the API route, else it will provide an error message stating that an administrator account is required to proceed. --- 
def administrator_required(func):
    @wraps(func)
    def administrator_required_wrapper(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token is missing. Please assign a token.'}), 401
        try:
            data = jwt.decode(token, secret_key, algorithms=['HS256'])
            if data['admin']:
                return func(*args, **kwargs)
            else:
                return make_response(jsonify({'message': 'Admin Access is required to proceed. Please verify with an Admin account.'}), 401)
        except:
            return jsonify({'message': 'Token is invalid. Please provide a valid token.'}), 401
    return administrator_required_wrapper

# --- The Index API route. ---
@app.route("/api/", methods = ['GET'])
@administrator_required
def index():
    return jsonify()

# --- Adding New Vulnerabilities/Packages API route. ---
@app.route("/api/packages", methods = ['POST'])
def add_package():
    if "packageName" in request.form and \
        "currentVer" in request.form and \
        "threatLevel" in request.form and \
        "vulnerableVersions" in request.form and \
        "vulnerability" in request.form:
        new_package = {
            "packageName": request.form["packageName"],
            "currentVer": request.form["currentVer"],
            "threatLevel": request.form["threatLevel"],
            "vulnerableVersions": request.form["vulnerableVersions"],
            "vulnerability": request.form["vulnerability"]
        }
        package_collection.insert_one(new_package)
        return make_response( jsonify({"message": "New Package added successfully."}), 201)
    else:
        return make_response(jsonify({'error': "Form data is incomplete or ran into an error. Please verify the information you entered is correct and try again."}), 404)

# @app.route("/api/upload", methods = ['POST'])
# def upload_file():
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'error': 'No file selected'}), 400
#     if file:
#         data = json.load(file)
#         packages = [package for package in data.get('dependencies', {}).keys()]
#         matching_packages = package_collection.find(packages)
#         return jsonify({'matching_packages': matching_packages}), 200

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

# --- Login API route. ---
@app.route('/api/login', methods = ['GET'])
def login():
    auth = request.authorization
    if auth:
        user = staffList_collection.find_one({'username': auth.username})
        if user is not None:
            if bcrypt.checkpw(bytes(auth.password, 'UTF-8'), \
                              user['password']):
                token = jwt.encode( \
                    {'user': auth.username,
                     'admin': user['admin'],
                     'exp': datetime.datetime.utcnow() + \
                        datetime.timedelta(minutes=30)
                        }, secret_key)
                return make_response(jsonify({'token': token}), 200)
            else:
                return make_response(jsonify({'message': 'Bad Password'}), 401)
        else:
            return make_response(jsonify({'message': 'Bad Username'}), 401)
    return make_response(jsonify({'message': 'Authentication is REQUIRED to access this route.'}), 401)

# --- IF statement to allow the app to run with debug mode enabled when __name__ == __main__. 
if __name__ == "__main__":
    app.run(debug=True)