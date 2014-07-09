Facecat
=======

This is an example application of RunAbove Object Storage with the Python SDK.  
It uses the bottle web framework and OpenCV to make a funny picture hosting 
webapp. Images are stored in RunAbove Object Storage and served to clients 
directly from there.

To allow clients to download objects directly, the container is made public.

How to install it on Debian/Ubuntu?
--------------------------------

First make sure that you installed the RunAbove Python SDK on your machine.  
Then you can install the requirements used by the example application.

The application requires OpenCV to apply modifications to the stored images.  
OpenCV and its Python bindings are available from repositories in Debian and 
Ubuntu.

```bash
apt-get install libjpeg-dev python-dev python-opencv
pip install bottle pillow
```

If you want to get the application working quickly without installing OpenCV on
your computer you can install it on a Debian instance in RunAbove.

In the file `facecat.py` you must put your application key, application secret 
and consumer key which are the credentials needed to access your RunAbove 
account from the API.

You can launch the web server and access it with your browser:

```bash
python facecat.py
```
