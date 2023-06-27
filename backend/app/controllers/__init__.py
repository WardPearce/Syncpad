from app.controllers import account, canary, session
from litestar import Router

routes = Router(
    path="/controllers", route_handlers=[account.router, session.router, canary.router]
)
