import os
from ultralytics import YOLO

current_dir = os.getcwd()
filename = 'best.pt'
file_path = os.path.join(current_dir, filename)

model = YOLO(file_path)

# Run the model on the image and save the output
results = model("/home/sergienko/newton/dice-3.jpg", save=False)

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
