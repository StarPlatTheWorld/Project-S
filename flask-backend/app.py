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

# --- Sets up an authorization token utilising JWT. This generates a token for users trying to login to protected API routes. --- 
def administrator_required(func):
    @wraps(func)
    def administrator_required_wrapper(*args, **kwargs):
        # Sets the existing token to None.
        token = None
        # If 'x-access-token' exists within request.headers, then assign that value to variable token.
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        # If no token is present, then throw an error that a token is missing.
        if not token:
            return jsonify({'message': 'Token is missing. Please assign a token.'}), 401
        # Takes the token that has been saved above, verifies and decodes it utilising the secret key provided, and specifies the usage of the HS256 algorithm to decode the token.
        try:
            data = jwt.decode(token, secret_key, algorithms=['HS256'])
            # If the data matches an administrator account, then pass positional arguments utilising *args and keyword arguments utilisng **kwargs.
            if data['admin']:
                return func(*args, **kwargs)
            # Else, return a response that states that Admin access is required and that the user must provide administrator details.
            else:
                return make_response(jsonify({'message': 'Admin Access is required to proceed. Please verify with an Admin account.'}), 401)
        # Creates an exception, based on if the token has become invalid after it's validity timer has expired.
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
    # Creates an array of field names from the database and assigns them to the variable valid_package_fields
    valid_package_fields = ['packageName', 'currentVer', 'threatLevel', 'vulnerableVersions', 'vulnerability']
    # If statement to check if all the fields exist within the request.form instance.
    if all([field in request.form for field in valid_package_fields]):
        # If all the field names are present, insert the new_package function into the collection within the database.
        new_package = {
            field: request.form[field] for field in valid_package_fields
        }
        package_collection.insert_one(new_package)
        # Return a response that the new package was added successfully, along with a 201 status code.
        return make_response( jsonify({"message": "New Package added successfully."}), 201)
    # Else, return a response that the form data was incomplete or ran into an error, and to verify that all information was entered and is correct. Also, return a 404 status code.
    else:
        return make_response(jsonify({'error': "Form data is incomplete or ran into an error. Please verify the information you entered is correct and try again."}), 404)
    
# --- Editing Existing Vulnerabilities/Packages API route. ---
@app.route("/api/packages/<string:id>", methods = ['PUT'])
@administrator_required
def edit_package(id):
    # Creates an array of field names from the database and assigns them to the variable edited_package_fields
    edited_package_fields = ['packageName', 'vulnerability']
    # If state to check if all the fields exist within the request.form instance
    if all ([field in request.form for field in edited_package_fields]):
        # If all fields exist, then update the package with the following form information.
        edited_package = package_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {field: request.form[field] for field in edited_package_fields}}
        )
        # Return and make a response with the success message 'Package edited successfully' and the 200 status code.
        return make_response( jsonify({'message': 'Package edited successfully.'}), 200)
    # Else, make a response that there was an error and that the package could not be found and a status code of 404.
    else:
        return make_response( jsonify({'error': 'Package could not be found, please ensure you entered the correct package information.'}), 404)
    
# --- Deleting Existing Vulnerabilities/Packages API route. ---
@app.route("/api/packages/<string:id>", methods = ['DELETE'])
@administrator_required
def delete_package(id):
    # Creates a variable called selected_package and uses a mongodb query to find a document within the collection with the specified id.
    selected_package = package_collection.find_one({'_id': ObjectId(id)})
    # If the id does not match an id within the database, then an error will be thrown stating that the package could not be found.
    if not selected_package:
        return make_response( jsonify({'error': 'Package could not be found. Please ensure that the information provided is correct.'}), 404)
    # A standard mongodb query to delete a document within a collection based on the id provided within the url.
    deleted_package = package_collection.delete_one({'_id': ObjectId(id)})
    # An if statement that checks if exactly one document has been deleted from the database.
    if deleted_package.deleted_count == 1:
        return make_response( jsonify({'message': 'Package has been deleted successfully.'}), 200)
    # Otherwise, throw an error to state that the package has not been deleted and to ensure that the information provided is correct.
    else:
        return make_response( jsonify({'error': 'Failed to delete package. Please ensure that the information provided is correct.'}), 500)


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