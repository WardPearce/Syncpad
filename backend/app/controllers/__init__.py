from litestar import Router

from app.controllers import account, canary, session, survey

routes = Router(
    path="/controllers",
    route_handlers=[
        account.router,
        session.router,
        canary.router,
        survey.router,
    ],
)
