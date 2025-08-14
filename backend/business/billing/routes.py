# Billing Service Routes
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import io

from .models import Invoice, InvoiceUpdate
from .pdf_generator import generate_invoice_pdf
from database import get_collection

router = APIRouter(prefix="/api/billing", tags=["Billing"])

# ---------- Utils ----------
async def _find_one_by_field(col, field: str, value: Any) -> Optional[Dict[str, Any]]:
    docs = await col.find({})
    for d in docs:
        if d.get(field) == value:
            return d
    return None

# ---------- Endpoints ----------
@router.get("/status")
async def status():
    col = await get_collection("invoices")
    docs = await col.find({})
    total = len(docs)
    paid = len([d for d in docs if d.get("status") == "paid"])
    overdue = len([d for d in docs if d.get("status") == "overdue"])
    amount_total = sum([d.get("amount", 0.0) for d in docs])
    amount_paid = sum([d.get("amount", 0.0) for d in docs if d.get("status") == "paid"])
    return {
        "status": "operational", 
        "service": "Billing", 
        "counts": {"invoices": total, "paid": paid, "overdue": overdue}, 
        "revenue": {"total": round(amount_total, 2), "paid": round(amount_paid, 2)}
    }

@router.post("/invoice", response_model=Invoice)
async def create_invoice(invoice: Invoice):
    # Calculate amount if not provided
    if not invoice.amount:
        invoice.amount = sum([it.quantity * it.unit_price for it in invoice.items])
    # Default due date in 30 days if not set
    if not invoice.due_date:
        invoice.due_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
    col = await get_collection("invoices")
    await col.insert_one(invoice.model_dump())
    return invoice

@router.get("/invoices", response_model=List[Invoice])
async def list_invoices():
    col = await get_collection("invoices")
    docs = await col.find({})
    return [Invoice(**d) for d in docs]

@router.get("/invoice/{invoice_id}", response_model=Invoice)
async def get_invoice(invoice_id: str):
    col = await get_collection("invoices")
    doc = await _find_one_by_field(col, "invoice_id", invoice_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return Invoice(**doc)

@router.put("/invoice/{invoice_id}")
async def update_invoice(invoice_id: str, payload: InvoiceUpdate):
    col = await get_collection("invoices")
    doc = await _find_one_by_field(col, "invoice_id", invoice_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Invoice not found")
    update_fields = payload.model_dump(exclude_none=True)
    # If items updated, recompute amount unless amount provided explicitly
    if "items" in update_fields and "amount" not in update_fields:
        update_fields["amount"] = sum([it["quantity"] * it["unit_price"] for it in update_fields["items"]])
    update_fields["updated_at"] = datetime.utcnow().isoformat()
    res = await col.update_one({"_id": doc["_id"]}, {"$set": update_fields})
    return {"matched": res.get("matched_count", 0), "modified": res.get("modified_count", 0)}

@router.post("/invoice/{invoice_id}/mark-paid")
async def mark_invoice_paid(invoice_id: str):
    col = await get_collection("invoices")
    doc = await _find_one_by_field(col, "invoice_id", invoice_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Invoice not found")
    res = await col.update_one({"_id": doc["_id"]}, {"$set": {"status": "paid", "updated_at": datetime.utcnow().isoformat()}})
    return {"matched": res.get("matched_count", 0), "modified": res.get("modified_count", 0)}

@router.delete("/invoice/{invoice_id}")
async def delete_invoice(invoice_id: str):
    col = await get_collection("invoices")
    doc = await _find_one_by_field(col, "invoice_id", invoice_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Invoice not found")
    res = await col.delete_one({"_id": doc["_id"]})
    return {"deleted": res.get("deleted_count", 0)}

@router.get("/invoice/{invoice_id}/pdf")
async def download_invoice_pdf(invoice_id: str):
    col = await get_collection("invoices")
    doc = await _find_one_by_field(col, "invoice_id", invoice_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Generate PDF using the dedicated module
    buffer = generate_invoice_pdf(doc)
    
    filename = f"invoice_{invoice_id}.pdf"
    headers = {
        "Content-Disposition": f"inline; filename={filename}",
        "X-Content-Type-Options": "nosniff"
    }
    return StreamingResponse(buffer, media_type="application/pdf", headers=headers)