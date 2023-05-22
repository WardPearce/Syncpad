from app.controllers import account, session
from litestar import Router

routes = Router(path="/controllers", route_handlers=[account.router, session.router])
