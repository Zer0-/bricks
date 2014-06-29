"""
This module was taken directly from the pyramid_mako project.
Please read the original license for this file:
   https://raw.githubusercontent.com/Pylons/pyramid_mako/master/LICENSE.txt
"""

import os
import posixpath
from mako.lookup import TemplateLookup
from mako.exceptions import (
    TemplateLookupException,
    TopLevelLookupException,
    text_error_template,
)
from .asset import resolve_spec

class ResourceTemplateLookup(TemplateLookup):
    """TemplateLookup subclass that handles asset specification URIs"""
    def adjust_uri(self, uri, relativeto):
        """Called from within a Mako template, avoids adjusting the
        uri if it looks like an asset specification"""
        # Don't adjust asset spec names
        isabs = os.path.isabs(uri)
        if (not isabs) and (':' in uri):
            return uri
        if not(isabs) and ('$' in uri):
            return uri.replace('$', ':')
        if relativeto is not None:
            relativeto = relativeto.replace('$', ':')
            if not(':' in uri) and (':' in relativeto):
                if uri.startswith('/'):
                    return uri
                pkg, relto = relativeto.split(':')
                _uri = posixpath.join(posixpath.dirname(relto), uri)
                return '{0}:{1}'.format(pkg, _uri)
            if not(':' in uri) and not(':' in relativeto):
                return posixpath.join(posixpath.dirname(relativeto), uri)
        return TemplateLookup.adjust_uri(self, uri, relativeto)

    def get_template(self, uri):
        """Fetch a template from the cache, or check the filesystem
        for it

        In addition to the basic filesystem lookup, this subclass will
        use pkg_resource to load a file using the asset
        specification syntax.

        """
        isabs = os.path.isabs(uri)
        if (not isabs) and (':' in uri):
            # Windows can't cope with colons in filenames, so we replace the
            # colon with a dollar sign in the filename mako uses to actually
            # store the generated python code in the mako module_directory or
            # in the temporary location of mako's modules
            adjusted = uri.replace(':', '$')
            try:
                if self.filesystem_checks:
                    return self._check(adjusted, self._collection[adjusted])
                else:
                    return self._collection[adjusted]
            except KeyError:
                asset = resolve_spec(uri)
                if os.path.exists(asset):
                    return self._load(asset, adjusted)
                raise TopLevelLookupException(
                    "Can not locate template for uri %r" % uri)
        try:
            return TemplateLookup.get_template(self, uri)
        except TemplateLookupException:
            if isabs:
                return self._load(uri, uri)
            else:
                raise
