from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from recognize import proceed as p
import os
app = Flask(__name__)

@app.route('/')
def index():
    return '<form method="POST" enctype="multipart/form-data"><input type="file" name="file" accept="image/*"><button>Submit</button></form>'

@app.route('/', methods=['POST'])
def proceed():
    if not os.path.isdir(os.path.join(os.path.dirname(__file__),'temp')):
        os.mkdir(os.path.join(os.path.dirname(__file__),'temp'))
    if 'file' not in request.files:
        return jsonify({'error':'no file uploaded'})
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join(os.path.dirname(__file__),'temp',filename))
    return jsonify(p(os.path.join(os.path.dirname(__file__),'temp', filename)))

if __name__ == "__main__":
    app.run("0.0.0.0",port=5000)