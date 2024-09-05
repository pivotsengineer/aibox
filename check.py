import os
from ultralytics import YOLO

current_dir = os.getcwd()
modelPath = "/home/sergienko/newton/runs/classify/train/weights/best.pt"
testImagePath = "/home/sergienko/newton/dice-3.jpg"

# Check if the file exists
if not os.path.isfile(modelPath):
    print(f"File not found: {modelPath}")
else:
    print(f"File found: {modelPath}")

    try:
        # Load the model
        model = YOLO(modelPath)
        print("Model loaded successfully.")

        # Run the model on the image and save the output
        results = model(testImagePath, save=False)

        # Access the probabilities and class names
        for result in results:
            probs = result.probs  # Get the class probabilities
            if probs is not None:
                # Get the class index with the highest probability (top 1) and the confidence score
                max_prob_index = probs.top1
                class_name = result.names[max_prob_index]
                confidence = probs.top1conf

                print(f"Predicted class: {class_name}")
                print(f"Confidence: {confidence.item()}")
            else:
                print("No class prediction found.")


    except Exception as e:
        print(f"Error loading model: {e}")