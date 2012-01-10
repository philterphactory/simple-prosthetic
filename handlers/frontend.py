import urlparse
import urllib
import logging

from bottle import Bottle, request, template, abort, redirect, template
from cork import get_flash, set_flash, SUCCESS, stripslashes

import oauth2 as oauth

import settings
import models
import weavrsclient
from backend import queue_run_weavr


app = Bottle()

@app.get('/')
def index(flash=None):
    weavrs_instances = models.WeavrsInstance.all(keys_only=True)
    flash = flash or get_flash()
    return template('frontend_index', **locals())


@app.get('/run/')
def run(flash=None):
    weavrs_instances = models.WeavrsInstance.all(keys_only=True)
    flash = flash or get_flash()
    return template('frontend_run_index', **locals())


@app.get('/run/instance/<name:path>')
def run_instance(name, flash=None):
    name = stripslashes(name)
    weavrs_instance = models.WeavrsInstance.get_by_key_name_or_abort(name)
    weavrs = weavrs_instance.get_weavrs()
    flash = flash or get_flash()
    return template('frontend_run_instance', **locals())


@app.get('/run/weavr/<name:path>')
def run_weavr(name, flash=None):
    name = stripslashes(name)
    weavr = models.Weavr.get_by_key_name_or_abort(name)
    queue_run_weavr(name)
    set_flash(SUCCESS, u"Run queued for weavr %s" % name)
    redirect('/')


@app.get('/oauth/start/weavr/<key>/')
def oauth_start(key):
    weavrs_instance = models.WeavrsInstance.get_by_key_name_or_abort(key)
    consumer = oauth.Consumer(weavrs_instance.consumer_key, weavrs_instance.consumer_secret)
    client = oauth.Client(consumer)
    client.force_exception_to_status_code = True
    next = request.query.next or '/'
    
    logging.debug(u"Connecting to %s" % weavrs_instance.request_token_url)
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
            current_url.scheme, current_url.netloc, weavrs_instance.key().name(), next)
    oauth_callback_url = urllib.quote_plus(oauth_callback_url)
    authorize_url = "%s?oauth_token=%s&oauth_callback=%s" % (weavrs_instance.authorize_url,
            request_key, oauth_callback_url)
    redirect(authorize_url)


@app.get('/oauth/complete/weavr/')
def oauth_complete():
    request_key = request.query.oauth_token
    oauth_verifier = request.query.oauth_verifier
    weavrs_instance_key = request.query.weavrs_instance
    next = request.query.next or '/'
    
    request_token = models.RequestToken.get_by_key_name_or_abort(key_name=request_key)
    try:
        weavrs_instance = models.WeavrsInstance.get_by_key_name_or_abort(key_name=weavrs_instance_key)
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
        
        key_name = u"%s/%s" % (weavrs_instance.key().name(), weavr_name)
        weavr = models.Weavr(key_name=key_name, oauth_key=access_key, oauth_secret=access_secret)
        weavr.save()
        set_flash(SUCCESS, u"OAuth authorization complete for weavr %s" % weavr_name)
        redirect(next)
    finally:
        try:
            request_token.delete()
        except Exception, e:
            logging.error(u"Error deleting RequestToken %s" % oauth_token)
    
    resp, content = client.request()
