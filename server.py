from flask import Flask, jsonify
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/start-model', methods=['GET'])
def start_model():
    # Your model logic here
    return jsonify({"message": "Model started successfully"})

if __name__ == '__main__':
    app.run(debug=True)
    
import subprocess

app = Flask(__name__)

@app.route('/start-model', methods=['GET'])
def start_model():
    try:
        # Run your Python model
        subprocess.Popen(["python", "main.py"])
        return jsonify({"message": "Model started successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
