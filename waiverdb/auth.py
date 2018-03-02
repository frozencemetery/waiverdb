# SPDX-License-Identifier: GPL-2.0+


import base64
import os
import gssapi
from flask import current_app, Response, g
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack
from socket import gethostname
from werkzeug.exceptions import Unauthorized, Forbidden

# Inspired by https://github.com/mkomitee/flask-kerberos/blob/master/flask_kerberos.py
# Later cleaned and ported to python-gssapi
def process_gssapi_request(token):
    if current_app.config['KERBEROS_HTTP_HOST']:
        hostname = current_app.config['KERBEROS_HTTP_HOST']
    else:
        hostname = gethostname()

    service_name = gssapi.Name("HTTP@%s" % hostname,
                               gssapi.NameType.hostbased_service)

    try:
        stage = "initialize server context"
        sc = gssapi.SecurityContext(usage="accept")

        stage = "step context"
        token = sc.step(token if token != "" else None)
        token = token if token is not None else ""

        # The current architecture cannot support continuation here
        stage = "checking completion"
        if not sc.complete:
            current_app.logger.error(
                'Multiple GSSAPI round trips not supported')
            raise Forbidden("Attempted multiple GSSAPI round trips")

        current_app.logger.debug('Completed GSSAPI negotiation')

        stage = "getting remote user"
        user = str(sc.initiator_name)
        return user, token
    except gssapi.exceptions.GSSError as e:
        current_app.logger.error(
            'Unable to authenticate: failed to %s: %s' %
            (stage, e.gen_msg()))
        raise Forbidden("Authentication failed")


def get_user(request):
    user = None
    headers = dict()
    if current_app.config['AUTH_METHOD'] == 'OIDC':
        if 'Authorization' not in request.headers:
            raise Unauthorized("No 'Authorization' header found.")
        token = request.headers.get("Authorization").strip()
        prefix = 'Bearer '
        if not token.startswith(prefix):
            raise Unauthorized('Authorization headers must start with %r' % prefix)
        token = token[len(prefix):].strip()
        required_scopes = [
            'openid',
            current_app.config['OIDC_REQUIRED_SCOPE'],
        ]
        validity = current_app.oidc.validate_token(token, required_scopes)
        if validity is not True:
            raise Unauthorized(validity)
        user = g.oidc_token_info['username']
    elif current_app.config['AUTH_METHOD'] == 'Kerberos':
        if 'Authorization' not in request.headers:
            response = Response('Unauthorized', 401, {'WWW-Authenticate': 'Negotiate'})
            raise Unauthorized(response=response)
        header = request.headers.get("Authorization")
        token = ''.join(header.strip().split()[1:])
        user, token = process_gssapi_request(base64.b64decode(token))
        # remove realm
        user = user.split("@")[0]
        headers = {'WWW-Authenticate': ' '.join(
            ['negotiate', base64.b64encode(token).decode()])}
    elif current_app.config['AUTH_METHOD'] == 'SSL':
        # Nginx sets SSL_CLIENT_VERIFY and SSL_CLIENT_S_DN in request.environ
        # when doing SSL authentication.
        ssl_client_verify = request.environ.get('SSL_CLIENT_VERIFY')
        if ssl_client_verify != 'SUCCESS':
            raise Unauthorized('Cannot verify client: %s' % ssl_client_verify)
        if not request.environ.get('SSL_CLIENT_S_DN'):
            raise Unauthorized('Unable to get user information (DN) from the client certificate')
        user = request.environ.get('SSL_CLIENT_S_DN')
    elif current_app.config['AUTH_METHOD'] == 'dummy':
        # Blindly accept any username. For testing purposes only of course!
        if not request.authorization:
            response = Response('Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="dummy"'})
            raise Unauthorized(response=response)
        user = request.authorization.username
    else:
        raise Unauthorized("Authenticated user required")
    return user, headers
