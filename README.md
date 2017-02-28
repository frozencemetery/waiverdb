# WaiverDB

WaiverDB is a companion service to 
[ResultsDB](https://pagure.io/taskotron/resultsdb), for recording waivers 
against test results.

## Quick development setup

Set up a python virtualenv:

    $ sudo dnf install python-virtualenv
    $ virtualenv env_waiverdb
    $ source env_resultsdb/bin/activate
    $ pip install -r requirements.txt

Install the project:

    $ python setup.py develop

Run the server:

    $ DEV=true python runapp.py

The server is now running at <http://localhost:5004> and API calls can be sent to
<http://localhost:5004/api/v1.0>. All data is stored inside `/var/tmp/waiverdb_db.sqlite`.

## Adjusting configuration

You can configure this app by copying `conf/settings.py.example` into
`conf/setting.py` and adjusting values as you see fit. It overrides default
values in `waiverdb/config.py`.

## Running test suite

You can run this test suite with the following command::

    $ py.test tests/
