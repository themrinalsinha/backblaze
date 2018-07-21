from requests import get
from base64   import b64encode

from .utils   import _get_output

class Backblaze(object):
    def __init__(self, account_id, application_id):
        self.application_id = application_id
        self.account_id     = account_id
        self.id_and_key     = '{}:{}'.format(self.account_id, self.application_id)
        self.auth_string    = 'Basic ' + b64encode(self.id_and_key.encode()).decode()
        self.headers        = {'Authorization' : self.auth_string}

        self.api_url        = None
        self.auth_token     = None
        self.download_url   = None

    def validate(self):
        request = get('https://api.backblazeb2.com/b2api/v1/b2_authorize_account',
                  headers = self.headers)
        if request.ok:
            response          = request.json()
            self.api_url      = response.get('apiUrl')
            self.auth_token   = response.get('authorizationToken')
            self.download_url = response.get('downloadUrl')
            return True
        return False

