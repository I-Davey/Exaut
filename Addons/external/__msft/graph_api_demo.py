import webbrowser
import msal
from msal import PublicClientApplication
from pydrive2.auth import GoogleAuth
import requests
from wsgiref.simple_server import make_server



APPLICATION_ID = 'a11f68df-20cb-4203-933e-8075ef4d1de1'
CLIENT_SECRET = 'xus8Q~RAdLb2pRtUXnaRuO5zQ65gnqNQh1SNqaUk'
authority_url = 'https://login.microsoftonline.com/consumers/'
base_url = 'https://graph.microsoft.com/v1.0/'
endpoint = base_url + 'me'
callback_url = 'http://localhost:8000/callback'
SCOPES = ['User.Read', 'User.Export.All']


client_instance = msal.ConfidentialClientApplication(
    client_id = APPLICATION_ID,
    client_credential = CLIENT_SECRET,
    authority = authority_url
)
authorization_request_url = client_instance.get_authorization_request_url(SCOPES)
#Open browser and wait for response on http://localhost:8000/callback
webbrowser.open(authorization_request_url, new=2)
#Handle GET request with ?code=... in the URL

def handle_request(environ, start_response):
    global auth_code
    start_response('200 OK', [('Content-Type', 'text/html')])
    auth_code = environ['QUERY_STRING'][5:]
    return [b'You can close this window now.']

httpd = make_server('', 8000, handle_request)
httpd.handle_request()
print(auth_code)

        


r = requests.request('LISTEN', 'http://localhost:8000/callback', stream=True)
for line in r.iter_lines():
    if line:
        decoded_line = line.decode('utf-8')
        print(decoded_line)
