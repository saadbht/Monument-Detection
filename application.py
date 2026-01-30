from flask import Flask, request, render_template, flash, redirect
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from detector_test import Detector

# Setting environment variables for language configuration
os.environ['LANG'] = 'en_US.UTF-8'
os.environ['LC_ALL'] = 'en_US.UTF-8'

application = Flask(__name__)
CORS(application)

# Never hard-code real secrets in a repo.
application.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
application.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static')
if not os.path.exists(application.config['UPLOAD_FOLDER']):
    os.makedirs(application.config['UPLOAD_FOLDER'])

class ImageNotFoundError(Exception):
    """Exception raised when an image is not found."""
    def __init__(self, message="Image not found"):
        self.message = message
        super().__init__(self.message)


@application.route("/")
def index():
    """Render the main page of the website."""
    return render_template('index.html')


@application.route('/', methods=['POST'])
def submit_file():
    """
    Handle file upload and object detection.
    Returns the result of object detection to the user.
    """
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading', 'error')
            return redirect(request.url)
        
        filename = secure_filename(file.filename)
        file_path = os.path.join(application.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        try:
            object_detector = Detector(filename)
            result = object_detector.detect_action()
            encoded_image = result['image']
            return render_template('index.html', detected=encoded_image, original='static/'+filename)
        except Exception as e:
            flash('Failed to process the image', 'error')
            return redirect(request.url)


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5000)
