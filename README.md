# Installing locally

* Checkout this repository
* Create a py3k virtualenv: `virtualenv -p python3 ve`
* Activate the virtualenv: `. ve/bin/activate`
* Install the requirements: `pip install -r requirements.txt`
* Create a `localsettings.py`: `cp localsettings.py.sample localsettings.py`
* Run migrations (creates the DB): `./manage.py migrate`
* Install bower: `npm install`
* Download and build static assets: `node_modules/.bin/gulp`
* Run the webserver: `./manage.py runserver`

# Installing in production
* apt install python3 memcached npm python3-libravatar \
  python3-tz python3-requests python3-pil python3-psycopg2 virtualenv

# Also see

https://wiki.debconf.org/wiki/Wafer
