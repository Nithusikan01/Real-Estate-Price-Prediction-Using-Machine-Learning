from flask import Flask, request, jsonify
from flask_cors import CORS
import util

app = Flask(__name__)
CORS(app)

@app.route('/')
def root():
    return "Welcome to the Housing Price Prediction API!"

@app.route('/get_predicted_price', methods=['POST'])
def get_predicted_price():
    try:
        data = request.get_json()
        if not data or 'input' not in data:
            return jsonify({"error": "Invalid input format, expected JSON with 'input' key"}), 400
        
        input_features = data['input']
        
        if not util.validate_input_format(input_features):
            return jsonify({"error": "Input features do not match expected format"}), 400
        
        estimated_price = util.get_estimated_price(input_features)
        return jsonify({"estimated_price": estimated_price}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Starting Flask server for Housing Price Prediction..") 

    # Load model artifacts
    util.load_saved_artifacts()

    # Start the Flask server
    app.run(debug=True)