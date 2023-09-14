import asyncio
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List

import humanize

from app.env import SETTINGS
from app.errors import DomainValidationError, UserNotFoundException
from app.lib.canary import Canary
from app.lib.crontabs import Tab
from app.lib.smtp import send_email
from app.lib.url import untrusted_http_request
from app.lib.user import User
from app.models.canary import CanaryModel, PublishedCanaryWarrantModel
from app.models.user import NotificationEnum

if TYPE_CHECKING:
    from app.custom_types import State


async def __handle_canary_verification(state: "State", canary: CanaryModel) -> None:
    try:
        await Canary(state, canary.domain).user(canary.user_id).attempt_verify()
    except DomainValidationError:
        return

    try:
        user = await User(state, canary.user_id).get()
    except UserNotFoundException:
        return

    await send_email(
        to=user.email,
        subject="Canary domain verified!",
        content=f"Your canary domain {canary.domain} has been verified!",
    )


async def canary_domain_verification(state: "State") -> None:
    futures = []

    async for canary in state.mongo.canary.find(
        {
            "domain_verification.completed": False,
            "created": {"$gte": datetime.utcnow() - timedelta(days=1)},
        }
    ):
        futures.append(
            __handle_canary_verification(state=state, canary=CanaryModel(**canary))
        )

    if futures:
        asyncio.gather(*futures)


async def canary_owner_alerts(state: "State") -> None:
    now = datetime.utcnow()

    async for canary_warrant in state.mongo.canary_warrant.find(
        {
            "active": True,
            "published": True,
            "next_canary": {"$gte": now, "$lte": now + timedelta(hours=24)},
            "alerted": False,
        }
    ):
        try:
            user = await User(state, canary_warrant["user_id"]).get()
        except UserNotFoundException:
            continue

        canary = await state.mongo.canary.find_one({"_id": canary_warrant["canary_id"]})
        if not canary:
            continue

        due_in = humanize.naturaltime(
            canary_warrant["next_canary"], future=True, when=now
        )

        futures: List = []

        if any(
            NotificationEnum.canary_renewals.value == enum.value
            for enum in user.notifications.email
        ):
            futures.append(
                send_email(
                    user.email,
                    f"Canary renewal due in {due_in}",
                    f"Your canary for {canary['domain']} is due in {due_in}.\nPlease renew it at {SETTINGS.proxy_urls.frontend}/dashboard/canary/publish/{canary['domain']}/",
                )
            )

        if any(
            NotificationEnum.canary_renewals.value == enum.value
            for enum in user.notifications.webhooks
        ):
            for webhook in user.notifications.webhooks[
                NotificationEnum.canary_renewals
            ]:
                futures.append(
                    untrusted_http_request(
                        state=state,
                        url=webhook,
                        method="POST",
                        json=PublishedCanaryWarrantModel(**canary_warrant).dict(),
                    )
                )

        if futures:
            asyncio.gather(*futures)

        await state.mongo.canary_warrant.update_one(
            {"_id": canary_warrant["_id"]}, {"alerted": True}
        )


tasks: list[Tab] = [
    # Check 1 minute for canary warrants that are due to expire
    Tab(spec="*/1 * * * *", func=canary_owner_alerts),
    Tab(spec="0 */1 * * *", func=canary_domain_verification),
]
