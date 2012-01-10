from google.appengine.ext import db

from bottle import abort


class Model(db.Model):
    @classmethod
    def get_by_key_name_or_abort(cls, key_name, status=404):
        result = cls.get_by_key_name(key_name)
        if not result:
            abort(status, u"%s %s not found" % (cls.__name__, key_name))
        return result
    
    @classmethod
    def abort_if_exists(cls, key_name, status=409):
        result = cls.get_by_key_name(key_name)
        if result:
            abort(status, u"%s %s already exists" % (cls.__name__, key_name))
    
    class Meta:
        key_parts = ['key_name']


class WeavrsInstance(Model):
    """A deployment of the weavrs platform that we can talk to."""
    # key holds the name of the instance
    link = db.LinkProperty(required=True, indexed=False)
    consumer_key = db.StringProperty(required=True, indexed=False)
    consumer_secret = db.StringProperty(required=True, indexed=False)
    enabled = db.BooleanProperty(required=True, default=True)

    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    
    class Meta:
        key_parts = ['instance_name']
    
    def _get_oauth_url(self, url_type):
        base_url = self.link
        if not base_url.endswith('/'):
            base_url += '/'
        oauth_url = u"%soauth/%s/" % (base_url, url_type)
        return oauth_url

    def _get_request_token_url(self):
        return self._get_oauth_url('request_token')
    request_token_url = property(_get_request_token_url)

    def _get_access_token_url(self):
        return self._get_oauth_url('access_token')
    access_token_url = property(_get_access_token_url)

    def _get_authorize_url(self):
        return self._get_oauth_url('authorize')
    authorize_url = property(_get_authorize_url)

    def get_api_url(self, action, version='1'):
        base_url = self.link
        if not base_url.endswith('/'):
            base_url += '/'
        api_url = u"%sapi/%s/%s/" % (base_url, version, action)
        return api_url
    
    def get_weavrs(self):
        # "localhost /"
        # "localhost / foo"
        # "localhost / bar"
        # "localhost/"        <--- bigger than this
        # "localhost/foo"
        # "localhost/bar"
        # "localhost0"        <--- smaller than this
        # "localhost0/bar"
        # "someothersite/"    <--- smaller than this
        return Weavr.all(keys_only=True)\
            .filter('enabled = ', True)\
            .filter('__key__ >', db.Key.from_path('Weavr', u"%s/" % self.key().name()))\
            .filter('__key__ < ', db.Key.from_path('Weavr', u"%s0" % self.key().name()))\
            .order('__key__')
        


class Weavr(Model):
    """A weavr on a particular weavrs platform (that we have or have had an access token for)."""
    # key is instance-name "/" weavr-name
    oauth_key = db.StringProperty(required=True, indexed=False)
    oauth_secret = db.StringProperty(required=True, indexed=False)
    oauth_revoked = db.DateTimeProperty()
    enabled = db.BooleanProperty(required=True, default=True)

    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)

    class Meta:
        key_parts = ['weavrs_instance_name', 'weavr_name']
    
    @classmethod
    def get_weavr_or_abort(cls, weavr_instance, key_or_name):
        if key_or_name.find('/') == -1:
            key_name = u"%s/%s" % (weavrs_instance.key().name(), key_or_name)
        elif isinstance(key_or_name, db.Key):
            key_name = key_or_name.name()
        else:
            key_name = key_or_name
        return self.get_by_key_name_or_abort(key_name)
    
    def get_instance(self):
        instance_name = self.key().name().split('/', 1)[0]
        return WeavrsInstance.get_by_key_name(instance_name)


class RequestToken(Model):
    """A temporary oauth request token."""
    # key is the oauth_token
    secret = db.StringProperty(required=True, indexed=False)

    created = db.DateTimeProperty(auto_now_add=True)

    class Meta:
        key_parts = ['key']
