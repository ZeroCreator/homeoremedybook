from dataclasses import dataclass
from typing import List

@dataclass
class Category:
    name: str
    slug: str
    is_acute: bool = False

# Основные категории
CATEGORIES = [
    Category(name="Общие препараты", slug="general", is_acute=False),
    Category(name="Острые случаи", slug="acute_cases", is_acute=True)
]
