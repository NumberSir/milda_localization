from dataclasses import dataclass

@dataclass
class ItemData:
    id: int
    description: str
    name: str


@dataclass
class EventCodeData:
    id: int
    code: int
    param: list[str]


__all__ = [
    "ItemData",
    "EventCodeData"
]
