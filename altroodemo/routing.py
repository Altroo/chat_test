#! -*- coding: utf-8 -*-

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from altroochat import routing as core_routing
from altroochat.auth.middleware import TokenAuthMiddleware

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter(
            core_routing.websocket_urlpatterns
        )
    ),
})
