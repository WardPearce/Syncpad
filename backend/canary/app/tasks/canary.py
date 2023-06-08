import asyncio
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

import humanize
from app.env import SETTINGS
from app.lib.smtp import send_email
from app.lib.user import User
from app.tasks._tasks import CronTask
from errors import UserNotFoundException

if TYPE_CHECKING:
    from app.types import State


async def canary_owner_alerts(state: "State") -> None:
    now = datetime.now(tz=timezone.utc)
    current_iso = now.date().isoformat()

    alerts = [
        now + timedelta(days=90),
        now + timedelta(days=30),
        now + timedelta(days=7),
        now + timedelta(days=3),
        now + timedelta(days=1),
        now + timedelta(hours=6),
        now + timedelta(hours=3),
        now + timedelta(hours=1),
    ]
    async for canary_warrant in state.mongo.canary_warrant.find(
        {
            "active": True,
            "last_alert": {"$ne": current_iso},
            "$or": [
                {
                    "next_canary": {
                        "$gte": alert,
                        "$lt": alert + timedelta(days=1),
                    }
                }
                for alert in alerts
            ],
        }
    ):
        try:
            user = await User(state, canary_warrant["user_id"]).get()
        except UserNotFoundException:
            continue

        canary = await state.mongo.canary.find_one({"_id": canary_warrant["canary_id"]})
        if not canary:
            continue

        due_in = humanize.naturaltime(canary_warrant["next_canary"])

        asyncio.create_task(
            send_email(
                user.email,
                f"Canary renewal due in {due_in}",
                f"Your canary for {canary['domain']} is due in {due_in}.\nPlease renew it at {SETTINGS.proxy_urls.frontend}/dashboard/canary/publish/{canary['domain']}/",
            )
        )

        await state.mongo.canary_warrant.update_one(
            {"_id": canary_warrant["_id"]}, {"$set": {"last_alert": current_iso}}
        )


tasks = [CronTask(spec="*/15 * * * *", func=canary_owner_alerts)]
