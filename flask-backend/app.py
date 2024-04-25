# Imports Python Modules into App Instance.
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
from config import Config, staff
import os

# Initialises the Flask app instance.
app = Flask(__name__)

# Sets up configuration from an object, that has been imported from a separate config file.
app.config.from_object(Config)

# CORS is an additional extension for Flask. This allows for Cross-Origin Resource Sharing, 
# which allows the back-end API to interact with the front-end application, and vice versa. 
CORS(app)

# Retrieves secret key from our config file and assigns it to variable.
secret_key = app.config['SECRET_KEY']

# Sets up the connection to MongoDB utilising pymongo. This allows both the database and collection
# to be accessed directly by the API, allowing for data manipulation and queries.
client = MongoClient("localhost", 27017)
db = client["ProjectS"]
package_collection = db["packages"]
staffList_collection = db["staffList"]
scan_saves_collection = db["scanSaves"]

# Placeholder image for user uploaded packages
placeholder_img = '/assets/logoPlaceholder.png'

# Creates a variabe named staffList and assigns the value of staff
# which is defined in the config file that is imported above.
staffList = staff

# For each new staff member within the staffList, hash their
# password with bcrypt and insert it into the collection.
for new_staff_member in staffList:
    new_staff_member["password"] = bcrypt.hashpw(new_staff_member["password"], \
    bcrypt.gensalt())
    staffList_collection.insert_one(new_staff_member)

# Creates the upload folder for our os module to save files to.
# Defines an absolute path, being static/uploads. Also only allows
# files with the extension .txt
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'txt'}
def allowed_file_types(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Defines a list of valid package field names for the use in the add package endpoint.
VALID_FIELDS = ['packageName', 'currentVer', 'threatLevel', 'vulnerableVersions', 'vulnerability']

# Sets up an authorization token utilising JWT. 
# This generates a token for users trying to login to protected API routes. 
def administrator_required(func):
    @wraps(func)
    def administrator_required_wrapper(*args, **kwargs):
        # Sets the existing token to None.
        token = None
        # If 'x-access-token' exists within request.headers, 
        # then assign that value to variable token.
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        # If no token is present, then throw an error that a token is missing.
        if not token:
            return jsonify({'message': 'Token is missing. Please assign a token.'}), 401
        # Takes the token that has been saved above, verifies and decodes it utilising the secret key provided, 
        # and specifies the usage of the HS256 algorithm to decode the token.
        try:
            data = jwt.decode(token, secret_key, algorithms=['HS256'])
            # If the data matches an administrator account, then pass positional arguments 
            # utilising *args and keyword arguments utilisng **kwargs.
            if data['admin']:
                return func(*args, **kwargs)
            # Else, return a response that states that Admin access is required 
            # and that the user must provide administrator details.
            else:
                return make_response(jsonify({'message': 'Admin Access is required to proceed. Please verify with an Admin account.'}), 401)
        # Creates an exception, based on if the token has become invalid after it's validity timer has expired.
        except:
            return jsonify({'message': 'Token is invalid. Please provide a valid token.'}), 401
    return administrator_required_wrapper

# The Index API route.
@app.route("/api/", methods = ['GET'])
def index():
    return make_response( jsonify({"message": "Welcome to Project-S"}), 200)
    
# Adding Package to Database API route. 
@app.route('/api/add_package', methods = ['POST'])
def add_package():
    # Receives the incoming data as JSON
    data = request.json 
    # Checks to see if all fields from incoming data match fields in VALID_FIELDS
    if all(field in data for field in VALID_FIELDS):
        # Assigns the field 'packageIcon' to data, even though the user did not provide this information, 
        # with a value that is predefined. Inserts the JSON data into the package_collection of the
        # MongoDB database.
        data['packageIcon'] = placeholder_img
        package_collection.insert_one(data)
        # Returns a response to state that the package has
        # successfully been added to the database, with a 
        # status code of 201.
        return make_response (jsonify({'message': 'Package has successfully been added to the database.'}), 201)
    # Else statement to make a response stating there was an error
    # with adding the package to the database, and that the user
    # should verify that all information is present and valid with
    # a status code of 401.
    else:
        return make_response (jsonify({'error': 'Package information is invalid or missing. Please try again.'}), 400)

# --- Editing Existing Vulnerabilities/Packages API route. ---
@app.route("/api/packages/<string:id>", methods = ['PUT'])
@administrator_required
def edit_package(id):
    # Creates an array of field names from the database 
    # and assigns them to the variable edited_package_fields
    edited_package_fields = ['packageName', 'vulnerability']
    # If state to check if all the fields exist within the request.form instance
    if all ([field in request.form for field in edited_package_fields]):
        # If all fields exist, then update the package with the following form information.
        edited_package = package_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {field: request.form[field] for field in edited_package_fields}}
        )
        # Return and make a response with the success message 'Package edited successfully'
        # and the 200 status code.
        return make_response( jsonify({'message': 'Package edited successfully.'}), 200)
    # Else, make a response that there was an error 
    # and that the package could not be found and a status code of 404.
    else:
        return make_response( jsonify({'error': 'Package could not be found, please ensure you entered the correct package information.'}), 404)
    
#  Deleting Existing Vulnerabilities/Packages API route.
@app.route("/api/packages/<string:id>", methods = ['DELETE'])
@administrator_required
def delete_package(id):
    # Creates a variable called selected_package and uses a mongodb 
    # query to find a document within the collection with the specified id.
    selected_package = package_collection.find_one({'_id': ObjectId(id)})
    # If the id does not match an id within the database, then an error will be thrown 
    # stating that the package could not be found.
    if not selected_package:
        return make_response( jsonify({'error': 'Package could not be found. Please ensure that the information provided is correct.'}), 404)
    # A standard mongodb query to delete a document 
    # within a collection based on the id provided within the url.
    deleted_package = package_collection.delete_one({'_id': ObjectId(id)})
    # An if statement that checks if exactly one document has been deleted from the database.
    if deleted_package.deleted_count == 1:
        return make_response( jsonify({'message': 'Package has been deleted successfully.'}), 200)
    # Otherwise, throw an error to state that the package has not been deleted 
    # and to ensure that the information provided is correct.
    else:
        return make_response( jsonify({'error': 'Failed to delete package. Please ensure that the information provided is correct.'}), 500)

# Uploading File for scanning API route.
@app.route('/api/upload', methods=['POST'])
def upload_file():
    # If no file has been selected to upload, make a response with error message 'No file part'.
    if 'file' not in request.files:
        return make_response ( jsonify({'error': 'No file part.'}), 400)
    # Takes the file from request.files property and assigns the value to variable
    # file. If the filename for variable file is blank, then throw an error stating
    # that no file was selected.
    file = request.files['file']
    if file.filename == '':
        return make_response ( jsonify({'error': 'No file selected.'}), 400)
    # If file does exist, has a name, and is selected then save the file to a local folder that is defined above. 
    # The file is then opened with Python and is opened as f. This is done using the os library.
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Everything from the line 170 to 182 is the standard way of saving an uploaded file to a local folder through Flask. This can be found on the official Flask documentation page under the category 'Uploading Files'.
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename)) as f:
            # Creates an empty list array and assigns it to the variable packages.
            packages = []
            # For each line within the file that is opened, split the package name and package version into separate lines.
            # Also removes the '==' that comes included within a requirements.txt file.
            for file_line in f:
                package_name, version = file_line.strip().split('==')
                # Appends the package name and the version to the empty list, creating a line for each.
                packages.append({'scannedName': package_name, 'version': version})
            # Finds the maximum value of scan_id that currently exists within the scanSaves collection.
            max_id_check = scan_saves_collection.find_one({}, sort=[('scan_id', -1)])
            # Checks if max_id is not None, to ensure that an entry exists within the collection. If that document exists, then extract the scan_id. 
            # The next_id is assigned the value of max_id + 1 for the next entry, incrementing the value.
            if max_id_check is not None:
                max_id = max_id_check.get('scan_id', 0)
                next_id = max_id + 1
            # Else, if no document exists within the collection, then start the next document with scan_id 1.
            else:
                next_id = 1
            # This is then inserted into a new collection called scanSaves,
            # which is defined above with the other collections.
            scan_saves_collection.insert_one({'scan_id': next_id, 'uploadedPackages': packages})
            return make_response ( jsonify({'message': 'File successfully scanned.'}), 201)

@app.route("/api/scan_results", methods = ['GET'])
def scan_results():
    # Creates a pipeline that will be used for aggregation within the mongo database.
    pipeline = [
                {
                    # Unwinds the array of uploadedPackages that exists 
                    # within the scanSaves collection using the $unwind operation.
                    '$unwind': '$uploadedPackages'
                },
                {
                    # The _id, which is of ObjectId is then unset using the $unset operator.
                    '$unset': '_id'
                },
                {
                    # The packages collection is then opened, we search for the field scannedName 
                    # from the local collection scanSaves, and the field packageName from the foreign collection packages.
                    '$lookup': {
                        'from': 'packages',
                        'localField': 'uploadedPackages.scannedName',
                        'foreignField': 'packageName',
                        'as': 'matchedPackages'
                    }
                },
                {
                    # It is then ensured that the matchedPackages do not return an empty array list.
                    '$match': {
                        'matchedPackages': {
                            '$ne': []
                        }
                    }
                },
                {
                    # The results are then grouped and the _id is set to the scannedName from uploadedPackages.
                    # After that , the matchedPackages use the $addToSet operator to add the results to an array.
                    '$group': {
                        '_id': 'uploadedPackages.scannedName',
                        'matchedPackages': {'$addToSet':{
                            'packageName': '$matchedPackages.packageName',
                            'threatLevel': {'$arrayElemAt': ['$matchedPackages.threatLevel', 0]},
                            'currentVer': {'$arrayElemAt': ['$matchedPackages.currentVer', 0]},
                            'vulnerableVersions': {'$arrayElemAt': ['$matchedPackages.vulnerableVersions', 0]},
                            'vulnerability': {'$arrayElemAt': ['$matchedPackages.vulnerability', 0]}
                        }
                    }
                }},
                {
                    # The _id field is then excluded from the final projection result and we project the results
                    # of matchedPackages.
                    '$project': {
                        '_id': 0,
                        'matchedPackages': 1,
                    }
                }
            ]
    # The scanSaves collection is then aggregated with the pipeline defined above and the results are saved
    # to a variable called scan. A list of the results within scan is then generated and assigned to the
    # variable scanMatches. A response is then made that returns the results of scanMatches.
    scan = scan_saves_collection.aggregate(pipeline)
    scanMatches = list(scan)
    return jsonify(scanMatches), 200

# The Package List API route.
@app.route("/api/packages", methods = ['GET'])
def get_packList():
    # Creates a listed version of every entry within the packages collection and assigns it
    # to the variable packages.
    packages = list(package_collection.find())
    # For each packages that exists within variable packages, then convert the package ObjectId(_id)
    # to a string, and then jsonify packages and return the results with the status code 200.
    for package in packages:
        package['_id'] = str(package['_id'])
    return jsonify(packages), 200

# Login API route.
@app.route('/api/login', methods = ['GET'])
def login():
    # Authorization is requested and the value is assigned to the variable auth.
    # If authorization exists, then the staffList collection is looked through to find
    # users within the collection.
    auth = request.authorization
    if auth:
        user = staffList_collection.find_one({'username': auth.username})
        # If user does exist, and the password provided matches the hashed password within the database, 
        # then generate a JWT token that includes the users username, an expiration date for the token, 
        # and the users admin status.
        if user is not None:
            if bcrypt.checkpw(bytes(auth.password, 'UTF-8'), \
                              user['password']):
                token = jwt.encode( \
                    {'user': auth.username,
                     'admin': user['admin'],
                     'exp': datetime.datetime.utcnow() + \
                        datetime.timedelta(minutes=30)
                        }, secret_key)
                # Returns a response that showcases the token generated with a status code of 200.
                return make_response(jsonify({'token': token}), 200)
            # Else, return a response with a message that states that the password provided was a bad password, 
            # and a status code of 401.
            else:
                return make_response(jsonify({'message': 'Bad Password'}), 401)
        # Else, return a response with a message that states that the username provided was a bad username,
        # and a status code of 401.
        else:
            return make_response(jsonify({'message': 'Bad Username'}), 401)
    # Return a response that states that authentication is required for access to this route to be provided, 
    # and a status code of 401.
    return make_response(jsonify({'message': 'Authentication is REQUIRED to access this route.'}), 401)

# --- IF statement to allow the app to run with debug mode enabled when __name__ == __main__. 
if __name__ == "__main__":
    app.run(debug=True)