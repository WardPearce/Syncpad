from typing import List

from app.tasks import canary
from lib.tasks import Tab

tasks: List[List[Tab]] = [canary.tasks]

__all__ = ["tasks"]
