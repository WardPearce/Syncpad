from datetime import timezone
from typing import TYPE_CHECKING, Any, Callable, List

import aiocron
from pydantic import BaseModel

if TYPE_CHECKING:
    from custom_types import State


class Tab(BaseModel):
    spec: str
    func: Callable[["State"], Any]


class CronTabs:
    def __init__(self, state: "State", tasks: List[List[Tab]]) -> None:
        self.__tasks = []

        for task in tasks:
            for t in task:
                self.__tasks.append(
                    aiocron.crontab(
                        t.spec, func=t.func, args=(state,), start=False, tz=timezone.utc
                    )
                )

    def start(self) -> None:
        for task in self.__tasks:
            task.start()

    def stop(self) -> None:
        for task in self.__tasks:
            task.stop()
