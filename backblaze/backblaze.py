from requests import get, post
from base64   import b64encode
from hashlib  import sha1
from os       import path

from .utils   import _get_output

class Backblaze(object):
    def __init__(self, account_id, application_id):
        self.application_id = application_id
        self.account_id     = account_id
        self.id_and_key     = '{}:{}'.format(self.account_id, self.application_id)
        self.auth_string    = 'Basic ' + b64encode(self.id_and_key.encode()).decode()
        self.headers        = {'Authorization' : self.auth_string}

        self.api_url           = None
        self.auth_token        = None
        self.upload_url        = None
        self.download_url      = None
        self.upload_auth_token = None

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

    def buckets(self, bucket_name=None):
        if self.validate():
            request = get('%s/b2api/v1/b2_list_buckets' % self.api_url,
                params  = {'accountId' : self.account_id},
                headers = {'Authorization' : self.auth_token})
            if request.ok:
                if bucket_name:
                    return [bkt['bucketId'] for bkt in request.json()
                           ['buckets'] if bkt['bucketName'] == bucket_name][0]
                return request.json()
            return False

    def _upload_url(self, bucket_name):
        bucket_id = self.buckets(bucket_name)
        request   = get('%s/b2api/v1/b2_get_upload_url' % self.api_url,
                    params  = {'bucketId' : bucket_id},
                    headers = {'Authorization' : self.auth_token})
        self.upload_url        = request.json()['uploadUrl']
        self.upload_auth_token = request.json()['authorizationToken']

    def upload(self, bucket_name, upload_file, author_name = 'Unknown'):
        file_data = open(upload_file, 'rb').read()
        sha1_file = sha1(file_data).hexdigest()
        file_name = path.basename(upload_file)
        self._upload_url(bucket_name)

        request = post(self.upload_url, files = {'file' : file_data},
            headers = {'Authorization'     : self.upload_auth_token,
                       'X-Bz-File-Name'    : file_name,
                       'Content-Type'      : '*/*',
                       'X-Bz-Info-Author'  : author_name,
                       'X-Bz-Content-Sha1' : sha1_file})

        print(request)