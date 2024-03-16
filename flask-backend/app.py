from flask import Flask, jsonify
from pymongo import MongoClient
import json

app = Flask(__name__)

client = MongoClient("localhost", 27017)
db = client["ProjectS"]

package_collection = db["packages"]

vulnerabilities = [
    {
        "package_name": "bootstrap",
        "current_version": "5.3",
        "vulnerabilities": [
            "no vulnerabilities found.",
            "Positive Health"
        ]
    }
]

@app.route("/")
def index():
    return jsonify(vulnerabilities)

@app.route("/vulnerabilities")
def vulList():
    return jsonify(vulnerabilities)

if __name__ == "__main__":
    app.run(debug=True)