from datetime import datetime
from decimal import Decimal
from sys import maxsize
from typing import List, Optional
from sqlalchemy import BigInteger, String, DateTime, Numeric, ForeignKey, Index, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    ...

