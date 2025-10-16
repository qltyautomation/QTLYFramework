# Native libraries
from enum import Enum


class TestTarget(Enum):
    """
    Enumeration defining test case execution targets
    """
    UI = "UI",
    API = "API"
