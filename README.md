# WaiverDB

WaiverDB is a companion service to 
[ResultsDB](https://pagure.io/taskotron/resultsdb), for recording waivers 
against test results.

## Quick development setup

Set up a python virtualenv:

    $ sudo dnf install python-virtualenv
    $ virtualenv env_waiverdb
    $ source env_waiverdb/bin/activate
    $ pip install -r requirements.txt

Install the project:

    $ python setup.py develop

Run the server:

    $ python run-dev-server.py

The server is now running at <http://localhost:5004> and API calls can be sent to
<http://localhost:5004/api/v1.0>. All data is stored inside `/var/tmp/waiverdb_db.sqlite`.

## Adjusting configuration

You can configure this app by copying `conf/settings.py.example` into
`conf/setting.py` and adjusting values as you see fit. It overrides default
values in `waiverdb/config.py`.

## Running test suite

You can run this test suite with the following command::

    $ py.test tests/

To test against all supported versions of Python, you can use tox::

    $ sudo dnf install python3-tox
    $ tox

## Building the docs

You can view the docs locally with::

    $ cd docs
    $ make html
    $ firefox _build/html/index.html

## Viewing published fedmsgs

You can view fedmsgs published when new waivers get created by doing::

    $ fedmsg-relay --config-filename fedmsg.d/config.py &
    $ fedmsg-tail --config fedmsg.d/config.py --no-validate --really-pretty
