Roadmap
=======

This describes some plans for the future of WaiverDB. Items are listed in 
approximate order of importance.

Using WaiverDB
--------------

Currently there is no easy way to actually *use* WaiverDB as a user submitting 
waivers. Ultimately we envisage that the consuming tools (for example, Bodhi) 
will include some user interface elements to create new waivers in the same 
place where they show the failing test results. However as a stop-gap there is:

* #82: Provide a command-line interface to submit waivers

There is one additional wrinkle. WaiverDB deployments running in OpenShift 
cannot use Kerberos authentication, because clients mostly default to 
``dns_canonicalize_hostname=true`` which is fundamentally incompatible with how 
OpenShift routes traffic to applications. In that case, something like SSL 
certification authentication will need to be used instead:

* #76: Support SSL certificate authentication

But we can't reasonably expect end users to obtain an SSL certificate for 
submitting waivers, so we will need the consuming tool (Bodhi or equivalent) to 
make the request to WaiverDB on behalf of the real human user. In that case 
WaiverDB will need to trust the calling service to tell it who the real human 
user was:

* #77: Allow "proxy user" waiving for a configured list of "super users"

Results may be absent
---------------------

One situation we anticipate is that a gating point is being held up a slow test 
system or an outage in the infrastructure. In some cases (for example, shipping 
urgent security advisories) humans may decide that it is worth the risk to 
bypass the test requirement *even if there is no result yet*.

* #80: Ability to waive the absence of a result
* #81: Ability to waive all results
