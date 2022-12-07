from enum import Enum


class Status(str, Enum):
    open = 'open'
    closed = 'closed'


class Flag(str, Enum):
    none = 'none'
    checked = 'checked'
    unchecked = 'unchecked'
