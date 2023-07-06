from typing import List

from app.lib.tasks import Tab
from app.tasks import canary

tasks: List[List[Tab]] = [canary.tasks]

__all__ = ["tasks"]
