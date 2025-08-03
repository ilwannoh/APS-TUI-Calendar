# FastAPI Backend for APS System
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import uvicorn
import pandas as pd
import json
import os
from pathlib import Path

# Import scheduling logic from original APS
import sys
sys.path.append(str(Path(__file__).parent.parent.parent / "NEW_APS"))
from app.core.scheduler import Scheduler
from app.core.data_manager import DataManager

app = FastAPI(title="APS Scheduling API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class Product(BaseModel):
    id: str
    name: str
    code: str
    category: Optional[str] = None

class Equipment(BaseModel):
    id: str
    name: str
    type: str
    capacity: Optional[int] = None

class BatchSchedule(BaseModel):
    id: str
    product_id: str
    product_name: str
    equipment_id: str
    process_name: str
    start_time: datetime
    end_time: datetime
    lot_number: str
    quantity: Optional[int] = None
    status: Optional[str] = "planned"

class ScheduleResponse(BaseModel):
    batches: List[BatchSchedule]
    summary: Dict[str, int]

# Initialize data manager and scheduler
data_manager = DataManager()
scheduler = Scheduler()

@app.get("/")
def read_root():
    return {"message": "APS Scheduling API", "version": "1.0.0"}

@app.get("/api/equipment", response_model=List[Equipment])
async def get_equipment():
    """Get all equipment list"""
    equipment_data = [
        Equipment(id="EQ001", name="혼합기 1호", type="mixer"),
        Equipment(id="EQ002", name="혼합기 2호", type="mixer"),
        Equipment(id="EQ003", name="타정기 1호", type="tablet_press"),
        Equipment(id="EQ004", name="타정기 2호", type="tablet_press"),
        Equipment(id="EQ005", name="코팅기 1호", type="coating"),
        Equipment(id="EQ006", name="코팅기 2호", type="coating"),
        Equipment(id="EQ007", name="포장기 1호", type="packaging"),
        Equipment(id="EQ008", name="포장기 2호", type="packaging")
    ]
    return equipment_data

@app.get("/api/products", response_model=List[Product])
async def get_products():
    """Get all products list"""
    products_data = [
        Product(id="500002", name="기넥신에프정 40mg 100T", code="GNX40-100"),
        Product(id="500005", name="기넥신에프정 40mg 300T", code="GNX40-300"),
        Product(id="500008", name="기넥신에프정 80mg 100T", code="GNX80-100"),
        Product(id="505227", name="기넥신에프정 80mg 500T", code="GNX80-500"),
        Product(id="500023", name="리넥신정", code="LNX"),
        Product(id="500041", name="조인스정", code="JNS"),
        Product(id="507123", name="페브릭정 40mg", code="FBR40"),
        Product(id="507242", name="신플랙스세이프정", code="SFS")
    ]
    return products_data

@app.get("/api/schedule", response_model=ScheduleResponse)
async def get_schedule():
    """Get current schedule"""
    # TODO: Load from database
    # For now, return sample data
    sample_batches = [
        BatchSchedule(
            id="BATCH001",
            product_id="500002",
            product_name="기넥신에프정 40mg 100T",
            equipment_id="EQ001",
            process_name="혼합",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=2),
            lot_number="LOT20240101001",
            quantity=1000
        )
    ]
    
    summary = {
        "total_batches": len(sample_batches),
        "total_products": 1,
        "total_equipment": 1
    }
    
    return ScheduleResponse(batches=sample_batches, summary=summary)

@app.post("/api/upload/sales-plan")
async def upload_sales_plan(file: UploadFile = File(...)):
    """Upload sales plan Excel file"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only Excel files are allowed")
    
    # Save file temporarily
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    try:
        # Read Excel file
        df = pd.read_excel(temp_path)
        
        # Process sales plan
        # TODO: Implement actual processing logic
        
        # Clean up
        os.remove(temp_path)
        
        return {"success": True, "message": "Sales plan uploaded successfully", "rows": len(df)}
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/schedule/generate")
async def generate_schedule(sales_data: Optional[dict] = None):
    """Generate production schedule from sales plan"""
    try:
        # TODO: Implement actual scheduling logic using the Scheduler class
        # For now, return success message
        return {
            "success": True,
            "message": "Schedule generated successfully",
            "batches_created": 10
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/batches/{batch_id}")
async def update_batch(batch_id: str, batch_data: dict):
    """Update batch schedule"""
    # TODO: Implement database update
    return {"success": True, "message": f"Batch {batch_id} updated successfully"}

@app.delete("/api/batches/{batch_id}")
async def delete_batch(batch_id: str):
    """Delete batch schedule"""
    # TODO: Implement database delete
    return {"success": True, "message": f"Batch {batch_id} deleted successfully"}

@app.get("/api/export/schedule")
async def export_schedule(format: str = "excel"):
    """Export schedule to Excel or CSV"""
    # TODO: Implement actual export logic
    # For now, create a sample file
    if format == "excel":
        filename = f"schedule_{datetime.now().strftime('%Y%m%d')}.xlsx"
        # Create sample Excel file
        df = pd.DataFrame({
            "Product": ["Sample Product"],
            "Equipment": ["Equipment 1"],
            "Start": [datetime.now()],
            "End": [datetime.now() + timedelta(hours=2)]
        })
        df.to_excel(filename, index=False)
    else:
        filename = f"schedule_{datetime.now().strftime('%Y%m%d')}.csv"
        df = pd.DataFrame({
            "Product": ["Sample Product"],
            "Equipment": ["Equipment 1"],
            "Start": [datetime.now()],
            "End": [datetime.now() + timedelta(hours=2)]
        })
        df.to_csv(filename, index=False)
    
    return FileResponse(filename, filename=filename)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)