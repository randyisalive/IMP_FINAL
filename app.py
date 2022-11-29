# web-app for API image manipulation

from flask import Flask, request, render_template, send_from_directory, redirect, url_for
import os
from PIL import Image
from flask_debugtoolbar import DebugToolbarExtension
import numpy as np
import cv2
from convolve import convolve

app = Flask(__name__)
app.secret_key = '1'
app.debug = True
toolbar = DebugToolbarExtension(app)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))


# default access page
@app.route("/")
def main():
    return render_template('index.html')


# upload selected image and forward to processing page
@app.route("/upload", methods=["POST"])
def upload():
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
    if (ext == ".jpg") or (ext == ".png") or (ext == ".bmp"):
        print("File accepted")
    else:
        return render_template("error.html", message="The selected file is not supported"), 400

    # save file
    destination = "/".join([target, filename])  # type: ignore
    print("File saved to to:", destination)
    upload.save(destination)

    # forward to processing page
    return render_template("processing.html", image_name=filename)


# rotate filename the specified degrees
@app.route("/rotate", methods=["POST"])
def rotate():
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

    return render_template('result.html', img1="static/images/temp.png", img2=image_destination)
    


# flip filename 'vertical' or 'horizontal'
@app.route("/flip", methods=["POST"])
def flip():

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
    return render_template('result.html', img1="static/images/temp.png", img2=image_destination)


# crop filename from (x1,y1) to (x2,y2)
@app.route("/crop", methods=["POST"])
def crop():
    # retrieve parameters from html form
    x1 = int(request.form['x1'])
    y1 = int(request.form['y1'])
    x2 = int(request.form['x2'])
    y2 = int(request.form['y2'])
    filename = request.form['image']

    # open image
    target = os.path.join(APP_ROOT, 'static/images')
    destination = "/".join([target, filename])
    image_destination = "static/images/" + filename
    img = Image.open(destination)

    # check for valid crop parameters
    width = img.size[0]
    height = img.size[1]

    crop_possible = True
    if not 0 <= x1 < width:
        crop_possible = False
    if not 0 < x2 <= width:
        crop_possible = False
    if not 0 <= y1 < height:
        crop_possible = False
    if not 0 < y2 <= height:
        crop_possible = False
    if not x1 < x2:
        crop_possible = False
    if not y1 < y2:
        crop_possible = False

    # crop image and show
    if crop_possible:
        img = img.crop((x1, y1, x2, y2))
        
        # save and return image
        destination = "/".join([target, 'temp.png'])
        if os.path.isfile(destination):
            os.remove(destination)
        img.save(destination)
        return render_template('result.html', img1="static/images/temp.png", img2=image_destination)

    else:
        return render_template("error.html", message="Crop dimensions not valid"), 400
    return '', 204


# blend filename with stock photo and alpha parameter
#@app.route("/blend", methods=["POST"])
# def blend():
    # retrieve parameters from html form
    alpha = request.form['alpha']
    filename1 = request.form['image']

    # open images
    target = os.path.join(APP_ROOT, 'static/images')
    filename2 = 'blend.jpg'
    destination1 = "/".join([target, filename1])
    destination2 = "/".join([target, filename2])

    img1 = Image.open(destination1)
    img2 = Image.open(destination2)

    # resize images to max dimensions
    width = max(img1.size[0], img2.size[0])
    height = max(img1.size[1], img2.size[1])

    img1 = img1.resize((width, height), Image.ANTIALIAS)
    img2 = img2.resize((width, height), Image.ANTIALIAS)

    # if image in gray scale, convert stock image to monochrome
    if len(img1.mode) < 3:
        img2 = img2.convert('L')

    # blend and show image
    img = Image.blend(img1, img2, float(alpha)/100)

     # save and return image
    destination = "/".join([target, 'temp.png'])
    if os.path.isfile(destination):
        os.remove(destination)
    img.save(destination)

    return send_image('temp.png')


@app.route('/negative', methods=['POST','GET'])
def negative():
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
    
    return render_template('result.html', img1="static/images/temp.png", img2=image_destination)

    
    
    


@app.route('/blur', methods=['POST','GET'])
def blur():

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
    
    
    
    
    
    return render_template('result.html', img1="static/images/temp.png", img2=image_destination)


@app.route('/grayscale', methods=['POST','GET'])
def grayscale():
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
    
    return render_template('result.html', img1="static/images/temp.png", img2=image_destination)

    
    
    
    
    


    


# retrieve file from 'static/images' directory
@app.route('/static/images/<filename>')
def send_image(filename):
    return send_from_directory("static/images", filename)


if __name__ == "__main__":
    app.run()

