#!/usr/bin/env python3

#
#
# RestAPI that deliver DNS automation services
#
#

# Imports
import json
import bcrypt
import jwt
import datetime
import ipaddress
from flask import Flask, request, jsonify, make_response
from flask_restplus import Api, Resource, fields
from functools import wraps


# Initialize Flask app and RestPlus
app = Flask(__name__)
app.config['PRESHARED_SECRET_KEY'] = 'keyusertosignJTWtockens!'
api = Api(app=app, title = "RestAPI POC", description = "Example of RestAPI with flask and RestPLUS" )


# Functions
def load_db_user(inputfile):
    '''Load user/password db from json file'''
    with open(inputfile) as f:
        userdb = json.load(f)
        return userdb

# Decorators
def token_validate(original_function):
    ''' Decorator for token valitation to be applied to protected route'''

    @wraps(original_function)
    def decorated(*args, **kwargs):

        token = None

        # Check if token is passed in the header of the request, if the case set token to this value
        # Checking for "x-access-token" or "Authorization: Bearer"
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].replace('Bearer ', '')

        # If token is not provided return 401
        if not token:
            return {'message': 'Authentication token is missing!'}, 401

        # Check token validity 
        try:
            token_data = jwt.decode(token, app.config['PRESHARED_SECRET_KEY'])
            user_from_token = token_data['username']
            exp_date_from_token = datetime.datetime.fromtimestamp(token_data['exp']).strftime('%Y-%m-%d %H:%M:%S')

        except jwt.ExpiredSignatureError:
            return {'message': 'Token is expired!'}, 403

        except:
            return {'message': 'Token provided is not valid'}, 401

        return original_function(*args, **kwargs)

    return decorated


# Initialize static data 
userdb = load_db_user('userdb.json')

# Routes
## Login route
@api.route('/login', methods=['GET'])
class LoginUser(Resource):
    def get(self):
        '''Login to get a token in order to perform write operation (HTTP Basic Auth) '''
        # Gather request informations about authentication
        auth = request.authorization

        # If the object auth is missing then pop up request for authentication
        if not auth or not auth.username or not auth.password:
            return make_response('Can not verify identity. Unauthorized!', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

        # Check username & password
        if auth.username in userdb and bcrypt.checkpw(auth.password.encode('UTF-8'), userdb[auth.username]['pwhash'].encode('UTF-8')):
            token = jwt.encode({'username': auth.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['PRESHARED_SECRET_KEY'])
            #return jsonify({'token': token.decode('UTF-8')}), 200
            return {'token': token.decode('UTF-8')}, 200
        else:
            return {'message': 'Username or password incorrect!'}, 401

        return {'message': 'Unauthorized!'}, 401




# Defining JSON structure for the posts
json_model = api.model("addrecord",
                                    {
                                    "domain": fields.String(description="Domain / Zone", required=True),
                                    "hostname": fields.String(description="hostname", required=True),
                                    "ip": fields.String(description="ip address", required=True),
                                    }
                                )


# Creating header model to be interpreted by the swagger interface
#  (purely for documentation on swagger, non for functionality)
auth_header_model = {'Authorization': {'name': 'Authorization Bearer',
                              'in': 'header',
                              'type': 'string',
                              'description': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1NjUwMTk0MDAsInVzZXJuYW1lIjoiY'}}


## Post route
@api.route('/addrecord', methods=['POST'])
@api.doc(params=auth_header_model) # This is to document the -H "Authorization: Bearer"  header
class PostRecord(Resource):
    decorators=[token_validate] # This is to decorate the RestPlus class with the tocken validation decorator
    @api.expect(json_model, validate=True) # This is to force the validation of the posted JSON 
    def post(self):
        '''POST POC'''

        # Read input (POST body JSON)
        json_data = request.json
        domain = json_data['domain'].strip()
        hostname = json_data['hostname'].strip()
        ip_addr = json_data['ip'].strip()

        # Check if provided ip is valid ip number
        try:
            ipaddress.ip_address(ip_addr)
        except:
            return {"message": "Not a valid ip!"}, 400
        else:
            return {"message": 'Creating record {}.{}  =  {}'.format(hostname, domain, ip_addr)}, 201



# Initialize main app
if __name__ == '__main__':
    app.run(host='0.0.0.0',port='8080', debug=True)

