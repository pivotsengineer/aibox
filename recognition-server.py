import os
import requests
from flask import Flask, request, jsonify
from ultralytics import YOLO
from PIL import Image
from io import BytesIO

# Initialize Flask app
app = Flask(__name__)

# Define model path and load the YOLO model
current_dir = os.getcwd()
model_path = os.path.join(current_dir, "runs/classify/train/weights/best.pt")

if not os.path.isfile(model_path):
    print(f"Model file not found: {model_path}")
    exit(1)

model = YOLO(model_path)
print("Model loaded successfully.")

# Define route to accept image file and return recognition results
@app.route('/predict', methods=['POST'])
def predict():
    if 'image_url' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    try:
        # Retrieve the uploaded image file
        image_file = request.files['image_url']
        image = Image.open(image_file.stream)
        
        # Run the YOLO model on the image
        results = model(image, save=False)

        # Process results and return the highest probability class
        predictions = []
        for result in results:
            probs = result.probs
            if probs is not None:
                max_prob_index = probs.top1
                class_name = result.names[max_prob_index]
                confidence = probs.top1conf
                predictions.append({
                    'class': class_name,
                    'confidence': confidence.item()
                })
            else:
                predictions.append({'error': 'No class prediction found'})
        
        return jsonify({'predictions': predictions})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
