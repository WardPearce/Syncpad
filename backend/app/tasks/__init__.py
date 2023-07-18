from typing import List

from app.lib.crontabs import Tab
from app.tasks import canary

tasks: List[List[Tab]] = [canary.tasks]

__all__ = ["tasks"]
