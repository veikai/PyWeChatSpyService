from flask import Flask, request
from werkzeug.utils import secure_filename


app = Flask(__name__)


@app.route("/upload", methods=["POST"])
def upload():
    print(request.files)
    f = request.files["file"]
    print(f.filename)
    f.save("file.jpg")
    return "1"


if __name__ == '__main__':
    app.run()