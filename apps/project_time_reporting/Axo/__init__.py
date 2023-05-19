import requests
import  json
from .validate import validate_response, validate_address, validate_required_params


SUPPORTED_API_VERSIONS = set([6])
DEFAULT_API_VERSION = 6


class Axosoft(object):
    def __init__(self, client_id, client_secret, domain, token=None):
        self.__consumer = {
            "client_id": client_id,
            "client_secret": client_secret,
            "domain": domain
        }
        self.__token = token
        self.__api_version = str(DEFAULT_API_VERSION)
        self.__api_path = 'api'
        self.__base_url = 'https://{0}.axosoft.com/{1}' \
            .format(
            self.__consumer["domain"],
            self.__api_path
        )

    def is_authenticated(self):
        """ Test if there is a valid token."""
        if self.__token is None:
            authenticated = False
        else:
            try:
                self.get('me')
            except ValueError:
                authenticated = False
            else:
                authenticated = True

        return authenticated

    def authenticate_by_password(self, user, password, scope="read write"):
        """
        Authenticate.
        Get a new token if one doesn't exist.
        Otherwise return the existing token.
        """
        authenticated = self.is_authenticated()
        if authenticated:
            return self.__token
        else:
            uri = '%s/oauth2/token?grant_type=password&username=%s&password=%s&client_id=%s&client_secret=%s&scope=%s' % (
            self.__base_url, user, password, self.__consumer['client_id'], self.__consumer['client_secret'], scope)
            response = requests.get(uri)
            success = validate_response(response, 200)
            if success:
                auth = response.json()
                assert auth['token_type'] == 'bearer'
                self.__token = auth['access_token']
                return self.__token

    def print_token(self):
        print(self.__token)

    def get(self, address, resourse_id=None, arguments=None, payload=None, element=None):
        """ Get a resource. """
        resource = validate_address(address, 'GET', element)
        uri = '{0}/v{1}/{2}' \
            .format(
            self.__base_url,
            self.__api_version,
            resource['address']
        )

        if address == "picklists":
            if element is not None:
                uri = '{0}/{1}'.format(uri, element)
            else:
                pass
            if resourse_id is not None:
                uri = '{0}/{1}'.format(uri, resourse_id)
            else:
                pass
        else:
            if resourse_id is not None:
                uri = '{0}/{1}'.format(uri, resourse_id)
            else:
                pass

            if element is not None:
                uri = '{0}/{1}'.format(uri, element)
            else:
                pass

        if arguments is not None:
            uri = '{0}?{1}'.format(uri, arguments)
        else:
            pass

        response = requests.get(
            uri,
            params=payload,
            headers={'Authorization': 'Bearer ' + self.__token}
        )

        validate_response(response, 200)

        response = response.json()

        return response

    def create(self, address, payload, resource_id=None, element=None):
        """ Create a resource. """
        resource = validate_address(address, 'POST', element)

        uri = '{0}/v{1}/{2}' \
            .format(
            self.__base_url,
            self.__api_version,
            resource['address']
        )

        if element is None:
            validate_required_params(resource, payload)
        else:
            uri = '{0}/{1}/{2}'.format(uri, resource_id, element)

        headers = {
            'Content-type': 'application/json; charset=utf-8',
            'Authorization': 'Bearer ' + self.__token
        }
        response = requests.post(
            uri,
            data=json.dumps(payload),
            headers=headers
        )

        validate_response(response, 201)

        data = response.json()
        return data

    def update(self, address, resourse_id, payload):
        """ Update a resource. """
        resource = validate_address(address, 'POST')

        uri = '{0}/v{1}/{2}/{3}' \
            .format(
            self.__base_url,
            self.__api_version,
            resource['address'],
            resourse_id
        )

        headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + self.__token
        }
        response = requests.post(
            uri,
            data=json.dumps(payload),
            headers=headers
        )

        validate_response(response, 200)

        data = response.json()
        return data
