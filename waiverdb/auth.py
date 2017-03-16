
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import os
import kerberos
from flask import current_app, Response
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack
from socket import gethostname
from werkzeug.exceptions import Unauthorized, Forbidden

#Inspired by https://github.com/mkomitee/flask-kerberos/blob/master/flask_kerberos.py
class KerberosAuthenticate(object):

    def __init__(self):
        if current_app.config['KERBEROS_HTTP_HOST']:
            hostname = current_app.config['KERBEROS_HTTP_HOST']
        else:
            hostname = gethostname()
        self.service_name = "HTTP@%s" % (hostname)
        if 'KRB5_KTNAME' in os.environ:
            try:
                principal = kerberos.getServerPrincipalDetails('HTTP', hostname)
            except kerberos.KrbError as exc:
                raise Unauthorized("Authentication Kerberos Failure: %s" % exc.message[0])
            else:
                current_app.logger.debug("Kerberos: server is identifying as %s" % principal)
        else:
            raise Unauthorized("Kerberos: set KRB5_KTNAME to your keytab file")

    def _gssapi_authenticate(self, token):
        '''
        Performs GSSAPI Negotiate Authentication
        On success also stashes the server response token for mutual authentication
        at the top of request context with the name kerberos_token, along with the
        authenticated user principal with the name kerberos_user.
        '''
        state = None
        ctx = stack.top
        try:
            rc, state = kerberos.authGSSServerInit(self.service_name)
            if rc != kerberos.AUTH_GSS_COMPLETE:
                current_app.logger.error('Unable to initialize server context')
                return None
            rc = kerberos.authGSSServerStep(state, token)
            if rc == kerberos.AUTH_GSS_COMPLETE:
                current_app.logger.debug('Completed GSSAPI negotiation')
                ctx.kerberos_token = kerberos.authGSSServerResponse(state)
                ctx.kerberos_user = kerberos.authGSSServerUserName(state)
                return rc
            elif rc == kerberos.AUTH_GSS_CONTINUE:
                current_app.logger.debug('Continuing GSSAPI negotiation')
                return kerberos.AUTH_GSS_CONTINUE
            else:
                current_app.logger.debug('Unable to step server context')
                return None
        except kerberos.GSSError as e:
            current_app.logger.error('Unable to authenticate: %s', e)
            return None
        finally:
            if state:
                kerberos.authGSSServerClean(state)

    def process_request(self, token):
        """
        Authenticates the current request using Kerberos.
        """
        kerberos_user = None
        kerberos_token = None
        ctx = stack.top
        rc = self._gssapi_authenticate(token)
        if rc == kerberos.AUTH_GSS_COMPLETE:
            kerberos_user = ctx.kerberos_user
            kerberos_token = ctx.kerberos_token
        elif rc != kerberos.AUTH_GSS_CONTINUE:
            raise Forbidden("Invalid Kerberos ticket")
        return kerberos_user, kerberos_token

def get_user(request):
    user = None
    headers = dict()
    if 'KRB5_KTNAME' in os.environ:
        header = request.headers.get("Authorization")
        if not header:
            response = Response('Unauthorized', 401, {'WWW-Authenticate': 'Negotiate'})
            raise Unauthorized(response=response)
        token = ''.join(header.split()[1:])
        user, kerberos_token = KerberosAuthenticate().process_request(token)
        # remove realm
        user = user.split("@")[0]
        if kerberos_token is not None:
            headers = {'WWW-Authenticate': ' '.join(['negotiate', kerberos_token])}
    else:
        raise Unauthorized("Authenticated user required")
    return user, headers