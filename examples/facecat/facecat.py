# -*- encoding: utf-8 -*-
#
# Copyright (c) 2014, OVH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Except as contained in this notice, the name of OVH and or its trademarks
# (and among others RunAbove) shall not be used in advertising or otherwise to
# promote the sale, use or other dealings in this Software without prior
# written authorization from OVH.

from __future__ import unicode_literals
from __future__ import division
import os

import cv2
import cv2.cv as cv
from PIL import Image
from bottle import route, request, static_file,\
                   run as bottle_run, view, redirect

from runabove import Runabove
from runabove.exception import ResourceNotFoundError

application_key = 'xxx'
application_secret = 'xxx'
consumer_key = 'xxx'
container_name = 'facecat'

# Create the Runabove SDK interface
run = Runabove(application_key,
               application_secret,
               consumer_key=consumer_key)

# Store our pictures in a random region
region = run.regions.list().pop()

# Create a container for our application
container = run.containers.create(region, container_name)

# Set the container public
container.set_public()

@route('/')
@view('views/index.html')
def index():
    """Show the main page."""
    return

@route('/error')
@view('views/index.html')
def err():
    """Show the main page with an error message."""
    return {'error': True}

@route('/static/<path:path>')
def callback(path):
    """Serve static files like CSS and JS."""
    return static_file(path, root='static/')

@route('/all')
@view('views/all.html')
def show_all():
    """List all the objects in the container."""
    objects = []
    for stored_object in container.list_objects():
        if stored_object.content_type == 'image/jpeg':
            objects.append(stored_object)
    return {'objects': objects}

@route('/show/<name>')
@view('views/show.html')
def show(name):
    """Show one object from the container."""
    try:
        stored_object = container.get_object_by_name(name)
    except ResourceNotFoundError:
        redirect('/error')
    return {'obj': stored_object}

@route('/delete/<name>')
def delete(name):
    """Delete an object from the container."""
    container.delete_object(name)
    redirect('/all')

@route('/upload', method='POST')
@view('views/show.html')
def upload():
    """Cattify a picture and upload it to the container."""
    # Check uploaded file
    upload = request.files.get('upload')
    if not upload:
        redirect('/error')
    name, ext = os.path.splitext(upload.filename)
    if ext.lower() not in ('.png', '.jpg', '.jpeg'):
        redirect('/error')

    # Create temporary directory for storing our files
    if not os.path.exists("/tmp/facecat"):
        os.makedirs("/tmp/facecat")

    # Save the uploaded picture to temporary directory
    upload.file.seek(0)
    file_path = "/tmp/facecat/" + upload.filename
    upload.save(file_path, True)

    # Cattify the picture ;)
    img = Cat(file_path)
    try:
        file_path = img.cattify()
    except IOError:
        os.remove(file_path)
        redirect('/error')
    path, file_name = os.path.split(file_path)

    # Upload the modified picture to the container
    new_object = container.create_object(file_name,
                                         open(file_path))

    # Clean temporary file
    os.remove(file_path)

    return {'obj': new_object}


class Cat(object):
    """Class that transforms people to cats."""

    image_max_size = 700, 700

    def __init__(self, image_file):
        self.image_file = image_file
        self.original_file = image_file

    def cattify(self):
        """Apply the changes to the image."""
        self.resize()
        self.transform()
        name, ext = os.path.splitext(self.original_file)
        final_name = name + '.jpeg'
        os.rename(self.image_file, final_name)
        return final_name

    def resize(self):
        """Resize the image as 'image_max_size' pixels."""
        new_name = self.image_file + '.resized'
        im = Image.open(self.image_file)
        im.thumbnail(self.image_max_size, Image.ANTIALIAS)
        im.save(new_name, "JPEG")
        os.remove(self.image_file)
        self.image_file = new_name

    def transform(self):
        new_name = self.image_file + '.cat.jpeg'
        img_color = cv2.imread(self.image_file)
        overlay = cv2.imread("media/cat.png", -1)

        height, width, depth = overlay.shape
        img_gray = cv2.cvtColor(img_color, cv.CV_RGB2GRAY)
        img_gray = cv2.equalizeHist(img_gray)

        rects = self.detect(img_gray)
        img_out = img_color.copy()
        self.draw_img(img_out, rects, overlay, width, height)
        cv2.imwrite(new_name, img_out)
        os.remove(self.image_file)
        self.image_file = new_name

    def draw_img(self, img, rects, overlay, width, height):
        for x1, y1, x2, y2 in rects:
            xsize = x2 - x1
            ysize = y2 - y1
            fx=xsize/width
            fy=ysize/height
            x_offset= x1
            y_offset= y1

            s_img = cv2.resize(overlay, (0,0), fx=fx, fy=fy)
            for c in range(0,3):
                img[y_offset:y_offset+s_img.shape[0],\
                x_offset:x_offset+s_img.shape[1], c] =\
                    s_img[:,:,c] * (s_img[:,:,3]/255.0) +\
                    img[y_offset:y_offset+s_img.shape[0],\
                    x_offset:x_offset+s_img.shape[1], c] *\
                    (1.0 - s_img[:,:,3]/255.0)

    def detect(self, img, cascade_fn='media/haarcascade_frontalface_alt.xml',
               scaleFactor=1.3, minNeighbors=4, minSize=(20, 20),
               flags=cv.CV_HAAR_SCALE_IMAGE):
        cascade = cv2.CascadeClassifier(cascade_fn)
        rects = cascade.detectMultiScale(img,
                                         scaleFactor=scaleFactor,
                                         minNeighbors=minNeighbors,
                                         minSize=minSize,
                                         flags=flags)
        if len(rects) == 0:
            return []
        rects[:, 2:] += rects[:, :2]
        return rects


if __name__ == '__main__':
    bottle_run(host='0.0.0.0', port=8080)
