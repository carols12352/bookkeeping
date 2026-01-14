from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Transaction:
    id: Optional[int]
    amount: float
    type: str
    category: str
    note: str
    date: date
