#!/usr/bin/env python3
import logging

import sys,os
sys.path.insert(0, os.path.abspath("flask-saml2"))

from flask import Flask, abort, redirect, request, session, url_for
from flask.views import MethodView
import flask
from flask_saml2.idp import IdentityProvider, SPHandler
from tests.idp.base import CERTIFICATE, PRIVATE_KEY, User
from tests.sp.base import CERTIFICATE as SP_CERTIFICATE
import secrets
import requests

logger = logging.getLogger(__name__)

database={}

class ExampleIdentityProvider(IdentityProvider):
    def login_required(self):
        if not self.is_user_logged_in():
            next = url_for('login', next=request.url)

            abort(redirect(next))

    def is_user_logged_in(self):
        return 'user' in session and session['user'] in users

    def logout(self):
        del session['user']

    def get_current_user(self):
        return users[session['user']]


# THIS IS NSO USERS
users = {user.username: user for user in [
    User('admin', 'admin'),
    User('oper', 'oper'),
    User('baduser', 'baduser'),
]}


idp = ExampleIdentityProvider()

def verify(otp,otp_key,nonce_url,nonce,user,otp_identity,status):
            if (otp==otp_key and nonce_url==nonce and status=='OK'):
                input_identity=database.get(user)
                if (otp_identity==input_identity):
                    return 0
                else:
                    logging.error("Login Key Mismatch Error")
                    logging.error("OTP Identity",otp_identity, input_identity)
                    return 1
            else:
                logging.error("Login Cloud Verify Error")
                logging.error("OTP",str(otp), str(otp_key))
                logging.error("Nounce", str(nonce_url), str(nonce))
                logging.error("Status", str(status), str('OK'))
                return 2

class Otp(MethodView):
                
    def get(self):
        select = (f'''
                  <div><label>Please Insert Your YubiKey and Press the Button</label></div>
                  <div class="center">
                    <div class="wave"></div>
                    <div class="wave"></div>
                    <div class="wave"></div>
                    <div class="wave"></div>
                    <div class="wave"></div>
                    <div class="wave"></div>
                    <div class="wave"></div>
                    <div class="wave"></div>
                    <div class="wave"></div>
                    <div class="wave"></div>
                </div>
                  ''')
        otp_key = f'<input id="otp_key" name="otp_key" type="hidden">'
        next_url = request.args.get('next')
        user = request.args.get('user')
        action = request.args.get('action')

        next = f'<input type="hidden" name="next" value="{next_url}">'

        user_block = f'<input type="hidden" name="user" value="{user}">'
        action_block = f'<input type="hidden" name="action" value="{action}">'

       #submit = '<div><input type="submit" value="Login"></div>'

        form = f'<form id="inputs" class="inputs" action="." method="post">{select}{otp_key}{user_block}{next}{action_block}</form>'
        js='<script src="/static/js/script.js"></script>'
        #js=''
        if (action == "login"):
            header = '''
            <head>
            <link rel="stylesheet" href="/static/css/mystyle.css">
            <title>Login</title><p>Please log in to continue.</p>
            </head>
            '''
        elif (action=='register'):
            header = '''
            <head>
            <link rel="stylesheet" href="/static/css/mystyle.css">
            <title>Login</title><p>Please register your key.</p>
            </head>
            '''
        body=f'<body id="body">{form}{js}</body>'
        response = flask.Response(header + body)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Content-Security-Policy']='frame-ancestors \'self\' http://localhost:8080/'
        return response

    def post(self):
        user = request.form['user']
        next = request.form['next']
        action = request.form['action']
        otp_key = request.form['otp_key']
        print("Validating OTP Key: "+otp_key)

        nonce_url = secrets.token_hex(20)

        id=1

        validate_url=f'https://api2.yubico.com/wsapi/2.0/verify?id={id}&otp={otp_key}&nonce={nonce_url}'
        PARAMS = {}

        r = requests.get(url = validate_url, params = PARAMS)
        data = r.text
        print(data)
        new_data=data.split()

        for dataset in new_data:
            print("dataset: ")  
            print(dataset)  
            split_data=dataset.split("=")
            key=split_data[0]
            data=""
            for string in split_data:
                if string != key:
                    data=data+string
            print(data)
            if key =="h":
                h=data
            elif key =="t":
                t=data
            elif key =="otp":
                otp=data
            elif key =="nonce":
                nonce=data
            elif key =="sl":
                sl=data
            elif key =="status":
                status=data
            else:
                logging.error("BAD DATA!!: "+key+" : "+data)

        if status != "OK":
            logging.error("Error Code: "+ status)
            return "Yubikey Key Malformat Error "+ status
        


        otp_secret=otp[:32]
        otp_identity=otp[:len(otp)-32]

        if (action == 'login'):
            verify_result=verify(otp,otp_key,nonce_url,nonce,user,otp_identity,status)
            if verify_result==0:
                    session['user'] = user
                    logging.info("Logged user", user, "in")
                    logging.info("Redirecting to", next)
                    js='<script src="/static/js/script.js"></script>'
                    header = f'''
                    <head>
                    <title>SAML Login</title><p>Processing..... Redirecting to: {next}</p>
                    </head>
                    '''
                    status='<div id="status"></div>'
                    iframe='<iframe name="dummyframe" id="dummyframe" width="100%" height="60%" hidden></iframe>'
                    body=f'<body id="body" onload = "auth_next()" >{status}{iframe}{js} </body>'
                    response = flask.Response(header + body)
                    response.headers['Access-Control-Allow-Origin'] = '*'
                    response.headers['Content-Security-Policy']='frame-ancestors \'self\' http://localhost:8080/'
                    return  redirect(next)
            elif verify_result==1:
                    return "Yubikey Key Mismatch Error "
            elif verify_result==2:
                return "Yubikey 2FA Cloud Verify Error"
          
        if (action == 'register'):
            if user not in database.keys():
                database[user] = otp_identity
                header = '''
                    <head>
                    <title>Register Success</title><p>Success!! Please Log in Again with Registered Key. Redirecting to login page.....</p>
                    </head>
                    '''
            else:
                header = '''
                    <head>
                    <title>Register Failed</title><p>Failed!! User already exist!! Please Log in with Correct Key. Redirecting to login page.....</p>
                    </head>
                    '''
            js='<meta http-equiv="refresh" content="3; URL=http://localhost:8080/" />'    
            body=f'<body id="body"onload = "redirect()">{js}</body>'
            response = flask.Response(header + body)
            return response
        return






class Login(MethodView):
    def get(self):
        options = \
                ''.join(f'<option value="{user.username}">{user.email}</option>'
                        for user in users.values())
        select = (f'<div><label>Select a user: <select name="user">{options}'
                   '</select></label></div>')
        logging.info(request.args)
        next_url = request.args.get('next')
        next = f'<input type="hidden" name="next" value="{next_url}">'

        submit = '''
                <div>
                    <input type="submit" name="action" value="Login">
                    <input type="submit" name="action" value="Register">
                </div>
                '''

        form = f'<form action="." method="post">{select}{next}{submit}</form>'
        header = '<title>Login</title><p>Please log in to continue.</p>'
        response = flask.Response(header + form+next_url)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Content-Security-Policy']='frame-ancestors \'self\' http://localhost:8080/'
        return response

    def post(self):
        print(request.form)
        user = request.form['user']
        next = request.form['next']
        if request.form['action'] == 'Login':
            return redirect('/otp/?next='+next+'&user='+user+'&action=login')
        elif request.form['action'] == 'Register':
            return redirect('/otp/?next='+next+'&user='+user+'&action=register')


class AttributeSPHandler(SPHandler):
    """
    Add attributes required by packageauth (groups, uid, gid, gids, homedir)
    to the SAMLResponse.
    """
    # FIXME create different auth data (groups, uid, gids, homedir) by user
    def build_assertion(self, request, *args, **kwargs):
        return {
            **super().build_assertion(request, *args, **kwargs),
            'ATTRIBUTES': {
                'groups': 'admin wheel',
                'uid': '1000',
                'gid': '1000',
                'gids': '100',
                'homedir': '/home/admin'
            },
        }
    pass

app = Flask(__name__, static_folder='static')
app.debug = True
app.secret_key = 'not a secret'
app.config['SERVER_NAME'] = 'localhost:8000'
app.config['SAML2_IDP'] = {
    'autosubmit': True,
    'certificate': CERTIFICATE,
    'private_key': PRIVATE_KEY,
}
app.config['SAML2_SERVICE_PROVIDERS'] = [
    {
        'CLASS': 'idp.AttributeSPHandler',
        'OPTIONS': {
            'display_name': 'NSO Service Provider',
            'entity_id': 'http://localhost:8080/sso/saml/metadata/',
            'acs_url': 'http://localhost:8080/sso/saml/acs/',
            'certificate': SP_CERTIFICATE,
        },
    }
]

app.add_url_rule('/login/', view_func=Login.as_view('login'))
app.add_url_rule('/otp/', view_func=Otp.as_view('otp'))

app.register_blueprint(idp.create_blueprint(), url_prefix='/saml/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
