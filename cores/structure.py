from dataclasses import dataclass
from datetime import datetime
@dataclass
class datastruct:
    id: int
    amount: float
    type: str
    category: str
    note: str
    date: datetime