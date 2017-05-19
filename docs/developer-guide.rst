=================
Development Guide
=================

Quick development setup
=======================

Set up a python virtualenv::

    $ sudo dnf install python-virtualenv
    $ virtualenv env_waiverdb
    $ source env_resultsdb/bin/activate
    $ pip install -r requirements.txt

Install the project::

    $ python setup.py develop

Run the server::

    $ python run-dev-server.py

The server is now running at on `localhost port 5004`_. Consult the
:ref:`rest-api` for available API calls. All data is stored inside
``/var/tmp/waiverdb_db.sqlite``.


Adjusting configuration
=======================

You can configure this app by copying ``conf/settings.py.example`` into
``conf/setting.py`` and adjusting values as you see fit. It overrides default
values in ``waiverdb/config.py``.


Running test suite
==================

You can run this test suite with the following command::

    $ py.test tests/

To test against all supported versions of Python, you can use tox::

    $ sudo dnf install python3-tox
    $ tox

.. _localhost port 5004: http://localhost:5004
