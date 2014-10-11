import __main__
import os

def read_settings(location, filename=None):
    """Reads and parses a json file from a given directory "location".
    If the filename argument is not given it will attempt to read a file named
    "settings.local.json", failing to find that it will try "settings.json".
    This allows a default settings file and a local version to coexist."""
    from json import loads
    if filename is None:
        filepath = os.path.join(location, 'settings.local.json')
        if not os.path.exists(filepath):
            filepath = os.path.join(location, 'settings.json')
        if not os.path.exists(filepath):
            raise IOError('settings.json file cannot be found!')
    else:
        filepath = os.path.join(location, filename)
    with open(filepath, 'r') as jsonsettings:
        return loads(jsonsettings.read())

class Settings(dict):
    provides = ['json_settings']

    def __init__(self, location=None):
        dict.__init__(self)
        if location is not None:
            settings = read_settings(location)
        else:
            try:
                location = os.getcwd()
                settings = read_settings(location)
            except IOError:
                if hasattr(__main__, '__file__'):
                    location = os.path.dirname(__main__.__file__)
                else:
                    location = os.path.dirname(__file__)
                settings = read_settings(location)
        self.update(settings)
        self['project_dir'] = here
