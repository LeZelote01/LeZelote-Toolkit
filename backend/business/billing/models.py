# Billing Service Models
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class InvoiceItem(BaseModel):
    description: str
    quantity: int = 1
    unit_price: float = 0.0

class Invoice(BaseModel):
    invoice_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str
    items: List[InvoiceItem] = []
    amount: float = 0.0
    currency: str = "EUR"
    status: str = "draft"  # draft, sent, paid, overdue
    due_date: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class InvoiceUpdate(BaseModel):
    items: Optional[List[InvoiceItem]] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[str] = None