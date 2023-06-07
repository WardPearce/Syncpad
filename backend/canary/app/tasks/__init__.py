from typing import List

from app.tasks import canary
from app.tasks._tasks import CronTask

tasks: List[List[CronTask]] = [canary.tasks]

__all__ = ["tasks"]
