from litestar import Router

from app.controllers import account, canary, csrf, session, settings, survey
from app.env import SETTINGS

enabled_routers: list[Router] = []

if SETTINGS.enabled.survey:
    enabled_routers.append(survey.router)

if SETTINGS.enabled.canaries:
    enabled_routers.append(canary.router)

routes = Router(
    path="/controllers",
    route_handlers=[
        account.router,
        session.router,
        csrf.router,
        settings.router,
        *enabled_routers,
    ],
)
