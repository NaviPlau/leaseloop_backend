from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from lease_auth.models import LoginToken

class CustomLoginTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Token '):
            return None
        token = auth_header[6:]
        try:
            login_token = LoginToken.objects.get(token=token)
            if not login_token.is_valid():
                login_token.delete()
                raise AuthenticationFailed('Please log in again.')

            return (login_token.user, None)

        except LoginToken.DoesNotExist:
            raise AuthenticationFailed('Please log in again.')