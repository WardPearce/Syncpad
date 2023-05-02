from typing import TYPE_CHECKING

from app.models.user import Argon2Modal
from litestar import Router
from litestar.controller import Controller
from litestar.handlers import get

if TYPE_CHECKING:
    from app.types import State


class EmailController(Controller):
    path = "/{email:str}"

    @get(path="/kdf", description="Public KDF details")
    async def kdf(self, state: "State", email: str) -> Argon2Modal:
        pass


router = Router(path="/account", route_handlers=[EmailController])
