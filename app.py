from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from recognizer import proceed as p
import os
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def proceed():
    if not os.path.isdir(os.path.join(os.path.dirname(__file__),'temp')):
        os.mkdir(os.path.join(os.path.dirname(__file__),'temp'))
    if 'file' not in request.files:
        return jsonify({'error':'no file uploaded'})
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join(os.path.dirname(__file__),'temp',filename))
    config={
        "level" : request.form.get("level",False), 
        "deaths" : request.form.get("deaths",False), 
        "mobs" : request.form.get("mobs",False), 
        "eliminations" : request.form.get("eliminations",False), 
        "xp" : request.form.get("xp",False), 
        "gold" : request.form.get("gold",False), 
        "damage" : request.form.get("damage",False), 
        "healing" : request.form.get("healing",False)
    }
    return jsonify(p(os.path.join(os.path.dirname(__file__),'temp', filename),config=config))

if __name__ == "__main__":
    app.run("0.0.0.0",port=5000, debug=True)