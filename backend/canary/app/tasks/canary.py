from typing import TYPE_CHECKING

from app.tasks._tasks import CronTask

if TYPE_CHECKING:
    from app.types import State


async def canary_owner_alerts(state: "State") -> None:
    pass


tasks = [CronTask(spec="*/1 * * * *", func=canary_owner_alerts)]
