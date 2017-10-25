=============
Release Notes
=============

WaiverDB 0.3
============

Released 26 Sep 2017.

A number of issues have been resolved in this release:

* Fixed some type errors in the API docs examples (#73).

* Updated README to recommend installing package dependencies using dnf builddep (#74).

* Fixed the health check API to return a proper error if the application is not
  able to serve requests (#75).

Other updates
-------------

* Supports a new HTTP API :http:post:`/api/v1.0/waivers/+by-result-ids`.
* Package dependencies are switched to python2-* packages in Fedora.

WaiverDB 0.2
============

Released 16 June 2017.

* Supports containerized deployment in OpenShift. ``DATABASE_PASSWORD`` and
  ``FLASK_SECRET_KEY`` can now be passed in as environment variables instead of 
  being defined in the configuration file.

* Supports publishing messages over AMQP, in addition to Fedmsg.
  The ``ZEROMQ_PUBLISH`` configuration option has been renamed to 
  ``MESSAGE_BUS_PUBLISH``.

* The :file:`/etc/waiverdb/settings.py` configuration file is no longer
  installed by default. For new installations, you can copy the example 
  configuration from :file:`/usr/share/doc/waiverdb/conf/settings.py.example`.

* Numerous improvements to the test and build process for WaiverDB.

WaiverDB 0.1
============

Initial release, 12 April 2017.
