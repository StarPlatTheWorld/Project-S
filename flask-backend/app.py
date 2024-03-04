from flask import Flask, jsonify

app = Flask(__name__)

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

@app.route("/api/")
def index():
    return jsonify(vulnerabilities)

if __name__ == "__main__":
    app.run(debug=True)