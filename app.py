# web-app for API image manipulation

from flask import Flask, request, render_template, send_from_directory, redirect, url_for
import os
from PIL import Image
import cv2

app = Flask(__name__)
app.secret_key = '1'
app.debug = True
APP_ROOT = os.path.dirname(os.path.abspath(__file__))


# default access page
@app.route("/")
def main():
    return render_template('index.html')


# upload selected image and forward to processing page
@app.route("/upload", methods=["POST"])
def upload():
    x = True
    target = os.path.join(APP_ROOT, 'static/images/')

    # create image directory if not found
    if not os.path.isdir(target):
        os.mkdir(target)

    # retrieve file from html file-picker
    upload = request.files.getlist("file")[0]
    print("File name: {}".format(upload.filename))
    filename = upload.filename

    # file support verification
    ext = os.path.splitext(filename)[1]  # type: ignore
    if (ext == ".jpg") or (ext == ".png") or (ext == ".bmp") or (ext == ".jpeg"):
        print("File accepted")
    else:
        return render_template("error.html", message="The selected file is not supported"), 400

    # save file
    destination = "/".join([target, filename])  # type: ignore
    print("File saved to to:", destination)
    upload.save(destination)

    # forward to processing page
    return render_template("processing_new.html", image_name=filename, x=x)


# rotate filename the specified degrees
@app.route("/rotate", methods=["POST"])
def rotate():
    # Controller #
    x = False
    # retrieve parameters from html form
    angle = request.form['angle']
    filename = request.form['image']

    # open and process image
    target = os.path.join(APP_ROOT, 'static/images')
    destination = "/".join([target, filename])
    image_destination = "static/images/" + filename

    img = Image.open(destination)
    img = img.rotate(-1*int(angle))

    # save and return image
    destination = "/".join([target, 'temp.png'])
    if os.path.isfile(destination):
        os.remove(destination)
    img.save(destination)

    return render_template('processing_new.html', img1="static/images/temp.png", img2=image_destination, x=x)
    


# flip filename 'vertical' or 'horizontal'
@app.route("/flip", methods=["POST"])
def flip():
    # Controller #
    x = False

    # retrieve parameters from html form
    if 'horizontal' in request.form['mode']:
        mode = 'horizontal'
    elif 'vertical' in request.form['mode']:
        mode = 'vertical'
    else:
        return render_template("error.html", message="Mode not supported (vertical - horizontal)"), 400
    filename = request.form['image']

    # open and process image
    target = os.path.join(APP_ROOT, 'static/images')
    destination = "/".join([target, filename])
    image_destination = "static/images/" + filename


    img = Image.open(destination)

    if mode == 'horizontal':
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    else:
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

    # save and return image
    destination = "/".join([target, 'temp.png'])
    if os.path.isfile(destination):
        os.remove(destination)
    img.save(destination)
    return render_template('processing_new.html', img1="static/images/temp.png", img2=image_destination, x=x)


@app.route("/cropSquare", methods=['POST'])     # type: ignore
def sCrop():
    x = False

    filename = request.form['image']

    # open image
    target = os.path.join(APP_ROOT, 'static/images')
    destination = "/".join([target, filename])
    image_destination = "static/images/" + filename
    img = Image.open(destination)

    # Crop image
    box = (250,250,750,750)
    img2 = img.crop(box)

     # save and return image
    destination = "/".join([target, 'temp.png'])
    if os.path.isfile(destination):
        os.remove(destination)
    img2.save(destination)
    return render_template('processing_new.html', img1="static/images/temp.png", img2=image_destination,x=x)




@app.route('/negative', methods=['POST','GET'])
def negative():
    # Controller #
    x = False
    # open image
    filename = request.form['image']
    target = os.path.join(APP_ROOT, 'static/images')
    destination = "/".join([target, filename])
    image_destination = "static/images/" + filename
    
    img = cv2.imread(destination, flags=cv2.IMREAD_COLOR)
    img_neg = 255 - img  # type: ignore
    
    # opencv save image
    directory = '/'.join([target])
    os.chdir(directory)
    cv2.imwrite('temp.png', img_neg)
    
    return render_template('processing_new.html', img1="static/images/temp.png", img2=image_destination, x=x)

    
    
    


@app.route('/blur', methods=['POST','GET'])
def blur():
    # Controller #
    x = False

    # open image
    filename = request.form['image']
    target = os.path.join(APP_ROOT, 'static/images')
    destination = "/".join([target, filename])
    image_destination = "static/images/" + filename

    
    img = cv2.imread(destination, flags=cv2.IMREAD_COLOR)
    blurImg = cv2.blur(img, (10,10))
    
    
    # opencv save image
    directory = '/'.join([target])
    os.chdir(directory)
    cv2.imwrite('temp.png', blurImg)
    
    
    
    
    
    return render_template('processing_new.html', img1="static/images/temp.png", img2=image_destination, x=x)


@app.route('/grayscale', methods=['POST','GET'])
def grayscale():
    # Controller #
    x = False
     # open image
    filename = request.form['image']
    target = os.path.join(APP_ROOT, 'static/images')
    destination = "/".join([target, filename])
    image_destination = "static/images/" + filename
    
    img = cv2.imread(destination, flags=cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # opencv save image
    directory = '/'.join([target])
    os.chdir(directory)
    cv2.imwrite('temp.png', gray)
    
    return render_template('processing_new.html', img1="static/images/temp.png", img2=image_destination, x=x)

    


if __name__ == "__main__":
    app.run()

