from ultralytics import YOLO

# Load the trained model
model = YOLO("/Users/sergeysergienko/Library/Mobile Documents/com~apple~CloudDocs/Projects/newton/best.pt")

# Run the model on the image and save the output
results = model("/Users/sergeysergienko/Library/Mobile Documents/com~apple~CloudDocs/Projects/newton/Dice-1/test/dice 2/20240402141330-jpg-4qc0evbk-ingestion-766bc49b8d-rd6xz_jpg.rf.fae7eddf9b9e9dd0bda06c1ee85561ba.jpg", save=True)

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
