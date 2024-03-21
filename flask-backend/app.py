from flask import Flask, jsonify, request, make_response
from pymongo import MongoClient
import json
from flask_cors import CORS
from bson import ObjectId

app = Flask(__name__)
CORS(app)

client = MongoClient("localhost", 27017)
db = client["ProjectS"]

package_collection = db["packages"]

@app.route("/")
def index():
    return jsonify()

@app.route("/vulnerabilities", methods = ['GET'])
def get_vulList():
    packages = list(package_collection.find())

    for package in packages:
        package['_id'] = str(package['_id'])

    return jsonify(packages)

if __name__ == "__main__":
    app.run(debug=True)