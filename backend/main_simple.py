# Simplified FastAPI Backend for APS System (without heavy dependencies)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import uvicorn
import json
import logging
import os
from pathlib import Path

# 로그 디렉토리 설정
log_dir = Path(__file__).parent / 'logs'
log_dir.mkdir(exist_ok=True)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'api_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="APS Scheduling API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

# In-memory storage (for demo)
schedules = []

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "APS Scheduling API", "version": "1.0.0"}

@app.get("/api/equipment")
async def get_equipment():
    """Get all equipment list"""
    logger.info("Equipment list requested")
    equipment_data = [
        {"id": "EQ001", "name": "혼합기 1호", "type": "mixer"},
        {"id": "EQ002", "name": "혼합기 2호", "type": "mixer"},
        {"id": "EQ003", "name": "타정기 1호", "type": "tablet_press"},
        {"id": "EQ004", "name": "타정기 2호", "type": "tablet_press"},
        {"id": "EQ005", "name": "코팅기 1호", "type": "coating"},
        {"id": "EQ006", "name": "코팅기 2호", "type": "coating"},
        {"id": "EQ007", "name": "포장기 1호", "type": "packaging"},
        {"id": "EQ008", "name": "포장기 2호", "type": "packaging"}
    ]
    return equipment_data

@app.get("/api/products")
async def get_products():
    """Get all products list"""
    products_data = [
        {"id": "500002", "name": "기넥신에프정 40mg 100T", "code": "GNX40-100"},
        {"id": "500005", "name": "기넥신에프정 40mg 300T", "code": "GNX40-300"},
        {"id": "500008", "name": "기넥신에프정 80mg 100T", "code": "GNX80-100"},
        {"id": "505227", "name": "기넥신에프정 80mg 500T", "code": "GNX80-500"},
        {"id": "500023", "name": "리넥신정", "code": "LNX"},
        {"id": "500041", "name": "조인스정", "code": "JNS"},
        {"id": "507123", "name": "페브릭정 40mg", "code": "FBR40"},
        {"id": "507242", "name": "신플랙스세이프정", "code": "SFS"}
    ]
    return products_data

@app.get("/api/schedule")
async def get_schedule():
    """Get current schedule"""
    if not schedules:
        # Return sample data if no schedules exist
        sample_batches = [
            {
                "id": "BATCH001",
                "product_id": "500002",
                "product_name": "기넥신에프정 40mg 100T",
                "equipment_id": "EQ001",
                "process_name": "혼합",
                "start_time": datetime.now().isoformat(),
                "end_time": (datetime.now() + timedelta(hours=2)).isoformat(),
                "lot_number": "LOT20240101001",
                "quantity": 1000
            }
        ]
        summary = {
            "total_batches": 1,
            "total_products": 1,
            "total_equipment": 1
        }
    else:
        sample_batches = schedules
        summary = {
            "total_batches": len(schedules),
            "total_products": len(set(s["product_id"] for s in schedules)),
            "total_equipment": len(set(s["equipment_id"] for s in schedules))
        }
    
    return {"batches": sample_batches, "summary": summary}

@app.post("/api/upload/sales-plan")
async def upload_sales_plan():
    """Upload sales plan Excel file"""
    return {"success": True, "message": "Sales plan uploaded successfully", "rows": 10}

@app.post("/api/schedule/generate")
async def generate_schedule():
    """Generate production schedule from sales plan"""
    logger.info("Schedule generation requested")
    # Generate sample schedules
    global schedules
    schedules = []
    
    products = await get_products()
    equipment = await get_equipment()
    
    start_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
    batch_id = 1
    
    for i, product in enumerate(products[:4]):  # Generate for first 4 products
        for j, process in enumerate(["혼합", "타정", "코팅", "포장"]):
            eq_idx = j * 2 + (i % 2)  # Alternate between equipment
            eq = equipment[eq_idx]
            
            schedules.append({
                "id": f"BATCH{batch_id:03d}",
                "product_id": product["id"],
                "product_name": product["name"],
                "equipment_id": eq["id"],
                "process_name": process,
                "start_time": start_time.isoformat(),
                "end_time": (start_time + timedelta(hours=2)).isoformat(),
                "lot_number": f"LOT{start_time.strftime('%Y%m%d')}{batch_id:03d}",
                "quantity": 1000
            })
            
            batch_id += 1
            start_time += timedelta(hours=2)
            
            # Move to next day if past 10 PM
            if start_time.hour >= 22:
                start_time = start_time.replace(hour=8) + timedelta(days=1)
    
    logger.info(f"Schedule generated successfully with {len(schedules)} batches")
    return {
        "success": True,
        "message": "Schedule generated successfully",
        "batches_created": len(schedules)
    }

@app.put("/api/batches/{batch_id}")
async def update_batch(batch_id: str, batch_data: dict):
    """Update batch schedule"""
    global schedules
    for i, batch in enumerate(schedules):
        if batch["id"] == batch_id:
            schedules[i].update(batch_data)
            return {"success": True, "message": f"Batch {batch_id} updated successfully"}
    return {"success": False, "message": "Batch not found"}

@app.delete("/api/batches/{batch_id}")
async def delete_batch(batch_id: str):
    """Delete batch schedule"""
    global schedules
    schedules = [b for b in schedules if b["id"] != batch_id]
    return {"success": True, "message": f"Batch {batch_id} deleted successfully"}

@app.get("/api/export/schedule")
async def export_schedule(format: str = "excel"):
    """Export schedule to Excel or CSV"""
    return {"message": "Export functionality would generate a file here"}

if __name__ == "__main__":
    logger.info("Starting APS API Server")
    logger.info(f"Log directory: {log_dir}")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)