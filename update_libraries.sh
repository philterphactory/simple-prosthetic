#!/usr/bin/env bash

set -e
set -x

git clone git@github.com:philterphactory/python-oauth2.git
rsync -a --delete ./python-oauth2/oauth2/ ./oauth2/
rm -Rf ./python-oauth2/
git add ./oauth2/

hg clone https://code.google.com/p/httplib2/ httplib2-temp
cd httplib2-temp/
hg checkout 0.7.2
cd ..
rsync -a --delete ./httplib2-temp/python2/httplib2/ ./httplib2/
git add ./httplib2/
