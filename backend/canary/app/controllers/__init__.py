from app.controllers import account
from litestar import Router

routes = Router(path="/controllers", route_handlers=[account.router])
