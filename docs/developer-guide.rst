=================
Development Guide
=================

Quick development setup
=======================

Install packages required by pip to compile some python packages::
    
    $ sudo dnf install swig systemd-devel openssl-devel cpp gcc

Set up a python virtualenv::

    $ sudo dnf install python-virtualenv
    $ virtualenv env_waiverdb
    $ source env_waiverdb/bin/activate
    $ pip install -r requirements.txt

Install the project::

    $ python setup.py develop

Run the server::

    $ cp conf/settings.py.example conf/settings.py
    $ PYTHONPATH=~/waiverdb DEV=true python waiverdb/manage.py run -h localhost -p 5004 --debugger

Migrate the db::

    $ PYTHONPATH=~/waiverdb DEV=true python waiverdb/manage.py db upgrade

The server is now running at on `localhost port 5004`_. Consult the
:ref:`rest-api` for available API calls. All data is stored inside
``/var/tmp/waiverdb_db.sqlite``.


Adjusting configuration
=======================

You can configure this app by copying ``conf/settings.py.example`` into
``conf/settings.py`` and adjusting values as you see fit. It overrides default
values in ``waiverdb/config.py``.


Running test suite
==================

You can run this test suite with the following command::

    $ py.test tests/

To test against all supported versions of Python, you can use tox::

    $ sudo dnf install python3-tox
    $ tox

.. _localhost port 5004: http://localhost:5004
