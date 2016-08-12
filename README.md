# Bricks

Bricks is a WSGI framework for writing http applications in Python.
It includes a simple dependency injection system for loading components,
a router and has support for rendering [Mako templates](https://github.com/zzzeek/mako) and JSON.

## Installation

Bricks is tested with Python 3.4 and above.
It's recommended to develop in a virtualenv. Create your environment with

```bash
$ python3 -m venv env
$ cd env
```

clone the repository and install using the setup.py script.

```bash
git clone https://github.com/Zer0-/bricks.git
./bin/python ./bricks/setup.py develop
```

## Dependency Injection

There is a `Bricks` class that creates instances of classes, passing as arguments
objects that the class may not know how to create itself. Consider the following example (You will
need a `settings.json` file containing the key "foo" in your cwd if you want to run this for yourself):

```python
from bricks import Bricks, Settings

class NeedsConfiguring:
    requires_configured = [ 'json_settings' ]

    def __init__(self, settings):
        self.foo_val = settings['foo']

    def foo(self):
        return self.foo_val

class Main:
    depends_on = [ NeedsConfiguring ]

    def __init__(self, doesfoo):
        self.doesfoo = doesfoo

    def __call__(self):
        return self.doesfoo.foo()

if __name__ == "__main__":
    bricks = Bricks()
    bricks.add(Settings)
    main = bricks.add(Main)
    print(main())
```

The result of running this program prints the value of "foo" that you put in your settings.json.

Notice that the Main class depends on a specific type (NeedsConfiguring) but avoids creating it.

Instead it relies on Bricks to create an instance of it and pass it as an argument.

NeedsConfiguring in turn declares that it needs any object providing a `json_settings` api,
which can be any object that has `provides = ['json_settings']` as an attribute. In
this example we are using the default Settings class from this package. You could
just as easily write your own dictionary like class that, say fetches settings from the web,
and use it place of Settings without changing anything else.

Let's try a more real-world example

## Hello World

```python
from bricks import Bricks, wsgi, BaseMC, Route
from bricks.render import string_response
from ceramic_forms import Use

class Name:
    @string_response
    def GET(self, request, response):
        name = request.route.vars[0]
        return 'Hello ' + name

routemap = Route() + {
    Use(str): Route(handler=Name)
    }

class Main(BaseMC):
    depends_on = [routemap]

if __name__ == "__main__":
    from wsgiref.simple_server import make_server

    bricks = Bricks()
    main = bricks.add(Main)
    app = wsgi(main)
    make_server('', 8080, app).serve_forever()
```

Try running this example and going to http://127.0.0.1:8080/yournamehere

Here we introduce the Route object. The Route object has a few named parameters,
the most important of which is `handler`, the value of which should be a class.

We use Name for the class. Bricks will create an instance of it and if the
correct route is requested by the client, it will call the method of the Name instance
corresponding with the request method, in this case GET, Name could have
defined POST, PUT, DELETE, OPTIONS methods as well.

These methods accept a WebOb request and response object and must return
a response object. The `string_response` decorator simply saves us from
explicitly modifying and returning the response object, as well as setting
the content type.

Also, we're using Python's built in reference wsgi server. It accepts a wsgi application.
This package contains a function `wsgi` that takes a BaseMC instance (which
can be thought of as the main starting point for a request comming in) and makes
a wsgi callable.

#### What is this routemap thing?

The routemap is the definition of accessible routes on the website. It should
be thought of as a tree, defined by dictionaries and Route objects.

```python
routemap = Route(name='home', handler=Homepage)
```

Would define a website where only the root '/' is accesible, and the Homepage
class would handle it.

The hello example above does not define a handler for the root route, so it will
404. 

Routes use the '+' syntax to create a tree of valid paths. Consider

```python
routemap = Route() + {
  'apples': Route(name='apples', handler=Apples),
  'oranges' Route(name='oranges', handler=Oranges)
}
```

Assuming we have Apples and Oranges defined this will serve up exactly two paths
/apples and /oranges

And one could further nest things by adding dictionaries to the apples and oranges
Routes to handle deeper paths.

However keys in the dictionaries are not limited to strings, as we have seen in the
hello example. In fact they can be any [ceramic_forms](https://code.vitrostudios.com/phil/ceramic_forms)
validator. For example `Use(And(str, lambda x: len(x) < 20))` can be used to match
any string of length less than 20, and this unknown value will be available
under request.route.vars in your handler.

Another feature of Routes is reverse lookup. If you are using the apples and oranges
routemap then in your handler you can use `request.route.find('oranges')` to get
/oranges; this works for any named Route.

### TODO
* Explain how to lookup routes with parameters
* Write an example using a database with [common_components](https://github.com/Zer0-/common_components) plugins for Bricks.
