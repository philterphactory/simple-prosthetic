import urlparse

from bottle import Bottle, request, template, abort, redirect, template
from cork import set_flash, SUCCESS

import oauth2 as oauth

import settings
import models


app = Bottle()

@app.get('/')
def index():
    weavrs_instances = models.WeavrsInstance.all(keys_only=True)
    return template('frontend_index', **locals())


@app.get('/oauth/start/weavr/<key>/')
def oauth_start(key):
    weavrs_instance = models.WeavrsInstance.get_by_key_name_or_abort(key)
    consumer = oauth.Consumer(weavrs_instance.consumer_key, weavrs_instance.consumer_secret)
    client = oauth.Client(consumer)
    next = request.query.next or '/'
    
    resp, content = client.request(weavrs_instance.request_token_url, 'GET')
    status = resp.status
    if status == 401:
        abort(500, u"OAuth consumer credentials for weavr instance %s not accepted" % key)
    elif status >= 500:
        abort(503, u"Could not get request token from weavrs instance %s, status %d" % (
                key, status))
    elif status >= 400:
        abort(500, u"Could not get request token from weavrs instance %s, status %d" % (
                key, status))
    elif status >= 300:
        abort(500, u"Could not get request token from weavrs instance %s, status %d" % (
                key, status))
    
    response_dict = dict(urlparse.parse_qsl(content))
    request_key = response_dict['oauth_token']
    request_secret = response_dict['oauth_token_secret']
    request_token = models.RequestToken(key_name=request_key, secret=request_secret)
    request_token.save()
    
    current_url = request.urlparts
    oauth_callback_url = "%s://%s/oauth/complete/weavr/?weavrs_instance=%s&next=%s" % (
            current_url.scheme, current_url.netlock, weavrs_instance.key().name(), next)
    authorize_url = "%s?oauth_token=%s&oauth_callback=%s" % (weavrs_instance.authorize_url,
            oauth_token, oauth_callback_url)
    redirect(authorize_url)


@app.get('/oauth/complete/weavr/')
def oauth_complete():
    request_key = request.query.oauth_token
    oauth_verifier = request.query.oauth_verifier
    weavrs_instance_key = request.query.weavrs_instance
    next = request.query.next or '/'
    
    request_token = models.RequestToken.get_by_key_name_or_abort(key_name=request_oauth_token)
    try:
        weavrs_instance = modelw.WeavrsInstance.get_by_key_name_or_abort(key_name=weavrs_instance_key)
        consumer = oauth.Consumer(weavrs_instance.consumer_key, weavrs_instance.consumer_secret)
        token = oauth.Token(request_key, request_token.secret)
        token.set_verifier(oauth_verifier)
        client = oauth.Client(consumer, token)
        
        resp, content = client.request(weavrs_instance.access_token_url, 'POST')
        status = resp.status
        if status == 401:
            abort(500, u"OAuth request token for weavr instance %s not accepted" % key)
        elif status >= 500:
            abort(503, u"Could not get access token from weavrs instance %s, status %d" % (
                    key, status))
        elif status >= 400:
            abort(500, u"Could not get access token from weavrs instance %s, status %d" % (
                    key, status))
        elif status >= 300:
            abort(500, u"Could not get access token from weavrs instance %s, status %d" % (
                    key, status))
        
        response_dict = dict(urlparse.parse_qsl(content))
        access_key = response_dict['oauth_token']
        access_secret = response_dict['oauth_token_secret']

        temp_weavr = models.Weavr(oauth_key=access_key, oauth_secret=access_secret)
        weavrs_client = weavrsclient.WeavrsClient(weavrs_instance, temp_weavr)
        config = weavrs_client.get_weavr_configuration()
        
        weavr_name = config.get('name')
        if not weavr_name:
            if temp_weavr.is_saved():
                try:
                    temp_weavr.delete()
                except Exception, e:
                    logging.error(u"Could not erase temporary Weavr %s" % temp_weavr.key().id_or_name())
            abort(503, u"Could not get weavr name from weavrs instance at %s, got content %s" % (
                    weavrs_instance.link, content))
        
        key_name = u"%s/%s" % (weavrs_instance.key.name(), weavr_name)
        weavr = Weavr(key_name=key_name, oauth_key=access_key, oauth_secret=access_secret)
        weavr.save()
        set_flash(SUCCESS, u"OAuth authorization complete for weavr %s" % weavr_name)
        redirect(next)
    finally:
        try:
            request_token.delete()
        except Exception, e:
            logging.error(u"Error deleting RequestToken %s" % oauth_token)
    
    resp, content = client.request()
