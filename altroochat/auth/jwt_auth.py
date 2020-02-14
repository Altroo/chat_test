# -*- coding: utf-8 -*-

from channels.auth import AuthMiddlewareStack
from django.db import close_old_connections
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt import decode as jwt_decode
from django.conf import settings
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser



class SimpleJwtTokenAuthMiddleware:
    """
    Simple JWT Token authorization middleware for Django Channels 2,
    ?token=<Token> querystring is reuired with the endpoint using this authentication
    middleware to work in synergy with Simple JWT
    """
    
    def __init__(self, inner):
        self.inner = inner
        
    def __call__(self, scope):
        # Close old database connections to prevent usage of timed out connections
        close_old_connections()
        
        # Get the token
        token = parse_qs(scope["query_string"].decode("utf8"))["token"][0]
        
        # Try to authenticate the user
        try:
            UntypedToken(token)
        except (InvalidToken, TokenError) as e:
            scope['user'] = AnonymousUser()

        else:
            #  Then token is valid, decode it
            decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = get_user_model().objects.get(id=decoded_data["user_id"])
            scope['user'] = user
        return self.inner(scope)
            
SimpleJwtTokenAuthMiddlewareStack = lambda inner: SimpleJwtTokenAuthMiddleware(AuthMiddlewareStack(inner))
