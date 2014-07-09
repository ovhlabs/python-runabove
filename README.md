Python SDK for RunAbove API
===========================

This is a Python SDK to use Instances and Object Storage on 
[RunAbove](https://www.runabove.com). The SDK uses the simple API provided by 
RunAbove.

Quickstart
------------------------------

To start with the SDK, you have to download the code or clone the official 
repository. Then, you can install the SDK with:

    python setup.py install

RunAbove SDK can then be included in your Python programs. Some examples of
applications using the SDK are available in the `examples` directory.

Authenticate to RunAbove API
----------------------------

Each **application** that uses RunAbove API needs to be authenticated. For that 
you have to register your application, it is very easy and can be done at this 
address: https://api.runabove.com/createApp

Then each **user** using your application will be securely authenticated with a 
consumer key. Thanks to this mecanism users don't need to give their plain text 
password to the application. The first time a user will use your application, 
he will be redirected to a web page where he can securely get his **consumer 
key**.

How to get a consumer key with the SDK?
---------------------------------------

To communicate with the API, each call made by your application must be signed 
and include the consumer key of the user. The signature process is 
automatically handled by the SDK. However if the user don't have a valid 
consumer key yet you can redirect him to RunAbove authentication page with the 
following code:

```python
from runabove import Runabove

application_key = 'your_app_key'
application_secret = 'your_app_secret'

# Create an instance of Runabove SDK interface
run = Runabove(application_key, application_secret)

# Request an URL to securely authenticate the user
print "You should login here: %s" % run.get_login_url()
raw_input("When you are logged, press Enter")

# Show the consumer key
print "Your consumer key is: %s" % run.get_consumer_key()
```

How to manage instances?
------------------------

Launching an instance is easy. First get the flavor, image and region where you 
want your instance to be created and call `Runabove.instances.create()`. To 
delete an instance just call the `instance.delete()` method:

```python
from runabove import Runabove

application_key = 'your_app_key'
application_secret = 'your_app_secret'
consumer_key = 'your_consumer_key'

# Create the Runabove SDK interface
run = Runabove(application_key,
               application_secret,
               consumer_key=consumer_key)

# Get a region, flavor and image
region = run.regions.list().pop()
flavor = run.flavors.list_by_region(region).pop()
image = run.images.list_by_region(region).pop()

# Launch a new instance
instance = run.instances.create(region, 'My instance', flavor, image)

# List instances
print 'Instances:'
for i in run.instances.list():
    print ' - %s (%s)' % (i.name, i.image.name)

# Delete the newly created instance
instance.delete()
print '%s deleted' % instance.name
```

How to use storage?
-------------------

```python
from runabove import Runabove

application_key = 'your_app_key'
application_secret = 'your_app_secret'
consumer_key = 'your_consumer_key'

# Create an instance of Runabove SDK interface
run = Runabove(application_key,
               application_secret,
               consumer_key=consumer_key)

# Get a region available
region = run.regions.list().pop()

# Create a new container
container_name = 'storage_test'
container = run.containers.create(region, container_name)
print "Storage container '%s' created" % container.name

# Create a new object
object_name = 'object.txt'
container.create_object(object_name, 'This is the content')
print "Object '%s' created" % object_name

# List objects of the container
print "Objects in '%s':" % container.name
for obj in container.list_objects():
    print " - %s (%d bytes)" % (obj.name, obj.size)

# Delete the object
obj.delete()
print "Object '%s' deleted" % obj.name

# Delete the container
container.delete()
print "Storage container '%s' deleted" % container.name
```

How to build the documentation?
-------------------------------

Documentation is based on sphinx. If you have not already installed sphinx, you 
can install it on your virtualenv:

    pip install sphinx

To generate the documentation in the `doc/build` directory, it's possible to 
use directly:

    python setup.py build_sphinx

How to run tests?
-----------------

To run tests, you need to install some dependencies:

    pip install -r test-requirements.txt

Then, you can directly run the unit tests

    python setup.py test

License
-------

The SDK code is released under a MIT style license, which means that it should 
be easy to integrate it to your application.  
Check the [LICENSE](LICENSE) file for more information.

