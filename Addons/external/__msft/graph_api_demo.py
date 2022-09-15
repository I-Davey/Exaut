import webbrowser
import msal
from msal import PublicClientApplication
from pydrive2.auth import GoogleAuth
import requests
from wsgiref.simple_server import make_server





        



class Temp:

    def __init__(self) -> None:
        self.APPLICATION_ID = 'a11f68df-20cb-4203-933e-8075ef4d1de1'
        self.CLIENT_SECRET = 'xus8Q~RAdLb2pRtUXnaRuO5zQ65gnqNQh1SNqaUk'
        self.authority_url = 'https://login.microsoftonline.com/consumers/'
        self.base_url = 'https://graph.microsoft.com/v1.0/'
        self.endpoint = self.base_url + 'me'
        self.callback_url = 'http://localhost:8000/callback'
        self.SCOPES = ['User.Read', 'User.Export.All']
        self.auth_code = None
    def main(self):
        client_instance = msal.ConfidentialClientApplication(
            client_id = self.APPLICATION_ID,
            client_credential = self.CLIENT_SECRET,
            authority = self.authority_url
        )
        authorization_request_url = client_instance.get_authorization_request_url(self.SCOPES)
        #Open browser and wait for response on http://localhost:8000/callback
        webbrowser.open(authorization_request_url, new=2)
        #Handle GET request with ?code=... in the URL



        httpd = make_server('', 8000, self.handle_request)
        httpd.handle_request()
        print(self.auth_code)
        r = requests.request('LISTEN', 'http://localhost:8000/callback', stream=True)
        for line in r.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                print(decoded_line)


    def handle_request(self, environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        auth_code = environ['QUERY_STRING'][5:]
        self.auth_code = auth_code
        return [b'You can close this window now.']

if __name__ == '__main__':
    Temp().main()
    

