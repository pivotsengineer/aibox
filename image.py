from flask import Flask, send_from_directory, render_template_string
import os

app = Flask(__name__)
IMAGE_PATH = 'test.jpg'  # Replace with the path to your image

# HTML template for the web page
HTML_TEMPLATE = '''
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Image Display</title>
  </head>
  <body>
    <h1>Test Image</h1>
    <img src="/image" alt="Test Image" width="640" height="480">
  </body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/image')
def image():
    return send_from_directory(os.path.dirname(IMAGE_PATH), os.path.basename(IMAGE_PATH))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
