import types
import logging
import datetime

from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.db.metadata import Kind

from bottle import Bottle, run, template, abort, request, response, redirect
from cork import get_flash, set_flash, SUCCESS, ERROR, stripslashes

import settings
import models


app = Bottle()

def get_kinds():
    return [x.__name__ for x in models.__dict__.values()
            if type(x) == db.PropertiedClass
                and issubclass(x, db.Model)
                and not x.__name__ == 'Model']


def is_kind_name(kindname):
    return kindname in get_kinds()


def check_kind_name(kindname):
    if not is_kind_name(kindname):
        abort(404, u"No such kind %s" % kindname)


def get_kind(kindname):
    check_kind_name(kindname)
    return getattr(models, kindname)


@app.get('/admin/')
def index():
    kinds = get_kinds()
    flash = get_flash()
    return template('admin_index', **locals())


@app.get('/admin/<kindname>/')
def kind_index(kindname):
    kind = get_kind(kindname)
    flash = get_flash()
    return template('admin_kind_index', **locals())


@app.get('/admin/<kindname>/add/')
def kind_add(kindname, values=None, flash=None):
    if values is None:
        values = {}
    kind = get_kind(kindname)
    flash = flash or get_flash()
    edit = False
    return template('admin_kind_add', **locals())


def getproperty(kind, p, key=False):
    if key:
        input_name = 'input__p__key__%s' % p
    else:
        input_name = 'input__p__%s' % p
    v = getattr(request.forms, input_name)
    if not key:
        property_class = kind._properties[p]
    else:
        property_class = db.StringProperty()
    logging.info("p = %s" % p)
    logging.info("v = %s" % v)
    logging.info("property_class = %s" % property_class)
    if not v:
        v = None
    else:
        if isinstance(property_class, db.BooleanProperty):
            if v.lower() in ['false', 'no']:
                v = False
            else:
                v = bool(v)
        elif isinstance(property_class, db.IntegerProperty):
            v = long(v)
        elif isinstance(property_class, db.FloatProperty):
            v = float(v)
        elif isinstance(property_class, db.DateTimeProperty):
            v = datetime.datetime.strptime(v, '%Y-%m-%d %H:%M:%S.%f')
        elif isinstance(property_class, db.LinkProperty):
            v = db.Link(v)
        elif isinstance(property_class, db.TextProperty):
            v = db.Text(v)
        elif isinstance(property_class, db.BlobProperty):
            v = db.Blob(v)
        elif isinstance(property_class, db.EmailProperty):
            v = db.Email(v)
        elif isinstance(property_class, db.GeoPtProperty):
            lat, lon = [float(x) for x in v.split(',', 1).strip()]
            v = db.GeoPt(lat, lon)
        elif isinstance(property_class, db.RatingProperty):
            v = db.Rating(int(v))
        elif isinstance(property_class, db.CategoryProperty):
            v = db.Category(v)
        elif isinstance(property_class, (db.ListProperty, db.StringListProperty)):
            # todo assumes list of strings
            v = list([v.strip() for v in v.split(",")])
        elif isinstance(property_class, db.ReferenceProperty):
            kindname = property_class.reference_class.__name__
            v = db.Key(kindname, v)
        elif isinstance(property_class, blobstore.BlobReferenceProperty):
            v = blobstore.BlobKey(v)
        elif isinstance(property_class, (
                    db.IMProperty,
                    db.PhoneNumberProperty,
                    db.PostalAddressProperty
                )):
            abort(500, 'Unsupported property type %s for model %s' % (property_class, kind.__name__))
    if key and v is None:
        abort(400, 'Property %s is part of the key for model %s so is required' % (p, kind.__name__))
    return v
    

@app.post('/admin/<kindname>/add/')
def kind_add_do(kindname):
    kind = get_kind(kindname)
    
    key_parts = [getproperty(kind, p, True) for p in kind.Meta.key_parts]
    key = u"/".join(key_parts)
    
    kind.abort_if_exists(key)
    try:
        do_put(kindname, kind, key)
    except db.BadValueError, e:
        return kind_add(kindname, values=request.forms, flash=(ERROR, e.message))


@app.get('/admin/<kindname>/edit/<name:path>')
def kind_edit(kindname, name, values=None, flash=None):
    if values is None:
        values = {}
    name = stripslashes(name)
    kind = get_kind(kindname)
    obj = kind.get_by_key_name_or_abort(name)
    key_name = obj.key().name()
    assert key_name is not None
    num_parts = len(kind.Meta.key_parts)
    key_parts = key_name.split(u"/")
    i = 0
    for k in kind.Meta.key_parts:
        v = key_parts[i]
        values[k] = v
        i += 1
    for p in kind.properties():
        if not p in values:
            values[p] = str(getattr(obj, p))
    del obj
    flash = flash or get_flash()
    edit = True
    return template('admin_kind_add', **locals())


@app.post('/admin/<kindname>/edit/<name>/')
def kind_edit_do(kindname, name):
    kind = get_kind(kindname)
    obj = kind.get_by_key_name_or_abort(name)
    key = str(obj.key())

    try:
        do_put(kindname, kind, key, instance=obj)
    except db.BadValueError, e:
        return kind_edit(kindname, values=request.forms, flash=(ERROR, e.message))


def do_put(kindname, kind, key, instance=None):
    properties = dict(
        [(k,v) for k,v in
            [(p,getproperty(kind, p)) for p in kind.properties()]
        if v is not None]
    )
    if instance is None:
        properties['key_name'] = key
        key_name = key
        instance = kind(**properties)
    else:
        key_name = db.Key(key).name()
        for k, v in properties.iteritems():
            setattr(instance, k, v)
    instance.put()
    set_flash(SUCCESS, '%s was saved' % key_name)
    redirect('/admin/%s/' % kindname)


@app.get('/admin/<kindname>/delete/<key:path>/')
def kind_delete(kindname, key):
    kind = get_kind(kindname)
    flash = get_flash()
    return template('admin_kind_delete', **locals())


@app.post('/admin/<kindname>/delete/<key:path>/')
def kind_delete_do(kindname, key):
    kind = get_kind(kindname)
    flash = get_flash()
    
    instance = kind.get_by_key_name_or_abort(key)
    instance.delete()
    set_flash(SUCCESS, '%s was deleted' % key)
    redirect('/admin/%s/' % kindname)
