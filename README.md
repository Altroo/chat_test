# Altroo Chat Section: 1
Final release of the Altroo chat with module build functionality, This document include following 
  - How to build the current code into a python module, which can be used in any django project.
  - complete functionality of the django channels chat
  - Async applicatin setup
  - sockets with session and token authenitication, custom middlewares

# What if I don't want to build this code into a module?
> If user don't want to build this code he/she can directly copy paste the altroochat sub-application into his project and
> add it into the installed application section of your project settings file. Along with that user need to install the requirements specific to Altroochat application provided in requirements directory of this project.

# Do I need to use the routers provided by altroochat subapplication or I can call API model viewsets from my own URL patterns/ routers?
> untill the user is including the alroochat subapplication url_pattrens directly into its base application or in some other sub-application. User is completely allowed to call the alroochat API endpoint using his custom router classes or URL patterns instead.

# How User can build this code into an module. In order to install this application in any django project using pip command line interface?
```sh
# Inside this project root run following commands to build the project with
# Virtualenvironment activated and all requirements already installed using followig command

$ pip install -r requirement.txt

# pack the code into a reusable module
$ python setup.py sdist

# Above given command will create a directory named 'dist' inside your project root.
# Inside this dist directory you will find the packed module named 'altroochat-0.1.tar.gz'
```

# How to install this packed module, received after performing above given commands?
```sh
# Inside your activated virtual environment you can install this altroochat-0.1.tar.gz package using following command
$ pip install --user <path to altroochat-0.1.tar.gz file>
# if --user doesn't work for your you. ie: in case you are using pyenv with shims, you can use following commands
$ pip install <path to altroochat-0.1.tar.gz file>
```
# what should be the change in settings files in order to get the application running?

```python
# Add following application to your installed applications
# of your django project.
INSTALLED_APPS += [
    'channels',
    'altroochat',
    'rest_framework',
    'rest_framework.authtoken', # Not necessery, if you plan to use without rest_framework authentication tokens]

# Add following lines to the end of your settings file

ASGI_APPLICATION = '<Your Root Application Name>.routing.application' #check the code block below for more info
MESSAGES_TO_LOAD = 15     #Number of messages to load by default, It specify the pagination page_size
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

# What is ASGI_APPLICATION mentioned above?
>ASGI_APPLICATION is Async Webserver Gateway Interface just like WSGI, In order to work with Django Channels we need to use this for websocket connections
>see bellow how we setup ASGI application file named routing.py.

```python
#! -*- coding: utf-8 -*-                                                                                                              

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from altroochat import routing as core_routing

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter(
            core_routing.websocket_urlpatterns
        )
    ),
})
```
 - AuthMiddleWareStack is used for session based authentication. 
- As the scope of application is not just limited to web, we also have a Token based authentication Middleware, which is Custom written inside altroochat.auth.middleware and altroochat.auth.jwt_auth_middleware.py you can also use that instesd of AuthMiddleWarStack.
 - User just need to copy paste above given code, Inside a new file name routing.py, in the root sub-application. see altroo_demo for more calrity of the concept.
 - this is the file which is mentioned in ASGI_APPLICATION settings mentioned above

# After this run migrations as mentioned below to make the models changes of altroochat appear in your database schema
```sh
$ python manage.py migrate
```

# How to use the URLS provided by AltrooChat Module?
> Users are allowed to user the URL patterns of the altroochat directly using Include statement in url_patterns or he/she can call the ModelViewset sirectly from his/her routers or url_patterns, if the user is not including the url_patterns of altroochat directly anywhere.


# what if I include the url_patterns of the altroochat directly, what should be the API and websocket path?
- API path will be at path   http://<your_host_name>/altroochat/api/v1/
- websocket will at path ws://<your_host_name>/altroochatws/
