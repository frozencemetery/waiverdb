# WaiverDB

![logo of WaiverDB](https://pagure.io/waiverdb/raw/master/f/logo.png)

## What is WaiverDB

WaiverDB is a companion service to
[ResultsDB](https://pagure.io/taskotron/resultsdb), for recording waivers
against test results.

## Quick development setup

Install dependencies:

    $ sudo dnf builddep waiverdb.spec

Run the server::

    $ cp conf/settings.py.example conf/settings.py
    $ PYTHONPATH=~/waiverdb DEV=true python waiverdb/manage.py run -h localhost -p 5004 --debugger

Migrate the db::

    $ PYTHONPATH=~/waiverdb DEV=true python waiverdb/manage.py db upgrade

The server is now running at <http://localhost:5004> and API calls can be sent to
<http://localhost:5004/api/v1.0>. All data is stored inside `/var/tmp/waiverdb_db.sqlite`.
You can verify the server is running correctly by visiting <http://localhost:5004/api/v1.0/about>.


## Adjusting configuration

You can configure this app by copying `conf/settings.py.example` into
`conf/settings.py` and adjusting values as you see fit. It overrides default
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

### WaiverDB CLI
WaiverDB has a command-line client interface for creating new waivers against test
results. A sample configuration is installed as ``/usr/share/doc/waiverdb/client.conf.example``.
Copy it to ``/etc/waiverdb/client.conf`` and edit it there. Or you can use ``--config-file``
to specify one.
```
Usage: waiverdb-cli [OPTIONS]

  Creates new waivers against test results.

  Examples:

      waiverdb-cli -r 123 -r 456 -p "fedora-26" -c "It's dead!"
or

      waiverdb-cli -t dist.rpmlint -s '{"item": "python-requests-1.2.3-1.fc26", "type": "koji_build"}' -p "fedora-26" -c "It's dead!"


Options:
  -C, --config-file PATH      Specify a config file to use
  -r, --result-id INTEGER     Specify one or more results to be waived
  -s, --subject TEXT          Specify one subject for a result to waive
  -t, --testcase TEXT         Specify a testcase for the subject
  -p, --product-version TEXT  Specify one of PDC's product version
                              identifiers.
  --waived / --no-waived      Whether or not the result is waived
  -c, --comment TEXT          A comment explaining why the result is waived
  -h, --help                  Show this message and exit.
```
