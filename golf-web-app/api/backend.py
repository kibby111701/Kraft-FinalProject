import cv2
from time import sleep
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['mov', 'mp4'])
UPLOAD_FOLDER = '../public/static/videos/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowedFile(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_extn(filename):
    return filename.rsplit('.', 1)[1].lower()


@app.route('/')
def hello():
    return 'Hello!'

@app.route('/test')
def test():
    return {'Name': "Chris",
            "Age": "22",
            "Understanding": "Absolutely none"}

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        print('here')
        f = request.files['file']
        filename = secure_filename(f.filename)
        if allowedFile(filename):
            print(filename)
            savepath = UPLOAD_FOLDER+'base.'+get_extn(f.filename)
            f.save(savepath)
            sleep(2)
            return {'filename': filename, 'status': 'success'}
        else:
            return {'status': 'failed'}
    except Exception as e:
        print(e)
        return {'status': 'failed'}



if __name__ == "__main__":
    app.run(debug=True)