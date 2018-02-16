=============
Release Notes
=============

WaiverDB 0.7
============

Released 16 Feb 2018.

* Fixed schema migrations for result_id backward compatibility.

WaiverDB 0.6
============

Released 13 Feb 2018.

* Dummy authentication for CLI for developing and debugging reasons.

* Added logo in the README page.

* You can now waive the absence of a result. Now it is possible to 
  submit waivers using a subject/testcase.

* Backward compatibility for submitting a waiver using the result_id.
  This feature will be removed in the near future.

WaiverDB 0.5
============

Released 17 Jan 2018.

* Database migrations have been introduced, and will be a part of future
  releases.  Users upgrading to 0.5 will need to run these commands::

  $ waiverdb db stamp 0a27a8ad723a
  $ waiverdb db upgrade

* Error messages are now returned by the API in JSON format.

* A new authentication method: ssl auth.  See the docs for more on
  configuration.

* The API now supports a proxyuser argument.  A limited set of superusers,
  configured server-side, are able to submit waivers on behalf of other users.

WaiverDB 0.4
============

Released 08 Nov 2017.

A number of issues have been resolved in this release:

* New WaiverDB CLI for creating waivers (#82).

* New `/about` API endpoint to expose the current running version and the method
  used for authentication of the server.

* Improved the process of building docs by using sphinxcontrib.issuetracker
  extension.

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

* Supports a new HTTP API `/api/v1.0/waivers/+by-result-ids`.
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
