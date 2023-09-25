from litestar import Controller, Router, get
from pydantic import BaseModel

from app.env import SETTINGS, Documents, Enabled


class SettingsController(Controller):
    @get("/documents", exclude_from_auth=True)
    async def documents(self) -> Documents:
        return SETTINGS.canary.documents

    @get("/enabled", exclude_from_auth=True)
    async def enabled(self) -> Enabled:
        return SETTINGS.enabled


router = Router(
    path="/settings", route_handlers=[SettingsController], tags=["settings"]
)
