#!/bin/sh
set -euf
if ! cmp -s package.json .deployed.package.json; then
	npm prune
	npm install
	cp package.json .deployed.package.json
fi
nodejs node_modules/.bin/gulp
rebuilt_ve=0
if ! cmp -s requirements.txt .deployed.requirements.txt; then
	rm -rf ../virtualenv/
	virtualenv -p python3 --system-site-packages ../virtualenv/
	../virtualenv/bin/pip install -r requirements.txt
	cp requirements.txt .deployed.requirements.txt
	rebuilt_ve=1
fi
../virtualenv/bin/python manage.py collectstatic --noinput
../virtualenv/bin/python manage.py migrate --noinput
../virtualenv/bin/python manage.py load_pages

if [ $rebuilt_ve -gt 0 ]; then
	sudo service apache2 reload
else
	touch wsgi.py
fi
