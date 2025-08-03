# Initialize database with sample data
from database import get_db_context, init_database
from models import Product, Equipment, Process, ProductProcess
import json

def init_sample_data():
    """Initialize database with sample master data"""
    
    # Initialize database tables
    init_database()
    
    with get_db_context() as db:
        # Check if data already exists
        if db.query(Product).count() > 0:
            print("Database already contains data. Skipping initialization.")
            return
            
        # Products
        products = [
            Product(id="500002", code="GNX40-100", name="기넥신에프정 40mg 100T", category="tablet", unit="정"),
            Product(id="500005", code="GNX40-300", name="기넥신에프정 40mg 300T", category="tablet", unit="정"),
            Product(id="500008", code="GNX80-100", name="기넥신에프정 80mg 100T", category="tablet", unit="정"),
            Product(id="505227", code="GNX80-500", name="기넥신에프정 80mg 500T", category="tablet", unit="정"),
            Product(id="500023", code="LNX", name="리넥신정", category="tablet", unit="정"),
            Product(id="500041", code="JNS", name="조인스정", category="tablet", unit="정"),
            Product(id="507123", code="FBR40", name="페브릭정 40mg", category="tablet", unit="정"),
            Product(id="507242", code="SFS", name="신플랙스세이프정", category="tablet", unit="정")
        ]
        db.add_all(products)
        
        # Equipment
        equipment_list = [
            Equipment(id="EQ001", name="혼합기 1호", type="mixer", capacity=1000),
            Equipment(id="EQ002", name="혼합기 2호", type="mixer", capacity=1000),
            Equipment(id="EQ003", name="타정기 1호", type="tablet_press", capacity=5000),
            Equipment(id="EQ004", name="타정기 2호", type="tablet_press", capacity=5000),
            Equipment(id="EQ005", name="코팅기 1호", type="coating", capacity=3000),
            Equipment(id="EQ006", name="코팅기 2호", type="coating", capacity=3000),
            Equipment(id="EQ007", name="포장기 1호", type="packaging", capacity=2000),
            Equipment(id="EQ008", name="포장기 2호", type="packaging", capacity=2000)
        ]
        db.add_all(equipment_list)
        
        # Processes
        processes = [
            # Mixing processes
            Process(id="PROC001", name="혼합", type="mixing", equipment_id="EQ001", duration_hours=2.0, setup_time_hours=0.5),
            Process(id="PROC002", name="혼합", type="mixing", equipment_id="EQ002", duration_hours=2.0, setup_time_hours=0.5),
            # Tablet press processes
            Process(id="PROC003", name="타정", type="tablet_press", equipment_id="EQ003", duration_hours=4.0, setup_time_hours=1.0),
            Process(id="PROC004", name="타정", type="tablet_press", equipment_id="EQ004", duration_hours=4.0, setup_time_hours=1.0),
            # Coating processes
            Process(id="PROC005", name="코팅", type="coating", equipment_id="EQ005", duration_hours=3.0, setup_time_hours=0.5),
            Process(id="PROC006", name="코팅", type="coating", equipment_id="EQ006", duration_hours=3.0, setup_time_hours=0.5),
            # Packaging processes
            Process(id="PROC007", name="포장", type="packaging", equipment_id="EQ007", duration_hours=2.0, setup_time_hours=0.5),
            Process(id="PROC008", name="포장", type="packaging", equipment_id="EQ008", duration_hours=2.0, setup_time_hours=0.5)
        ]
        db.add_all(processes)
        
        # Product-Process mappings (standard tablet production flow)
        product_processes = []
        
        # For all tablet products: Mixing -> Tablet Press -> Coating -> Packaging
        for product in products:
            if product.category == "tablet":
                # Mixing (can use either mixer)
                product_processes.append(
                    ProductProcess(
                        product_id=product.id,
                        process_id="PROC001",  # Mixer 1
                        sequence=1,
                        quantity_per_batch=1000
                    )
                )
                # Tablet press (can use either press)
                product_processes.append(
                    ProductProcess(
                        product_id=product.id,
                        process_id="PROC003",  # Press 1
                        sequence=2,
                        quantity_per_batch=5000
                    )
                )
                # Coating (can use either coater)
                product_processes.append(
                    ProductProcess(
                        product_id=product.id,
                        process_id="PROC005",  # Coater 1
                        sequence=3,
                        quantity_per_batch=3000
                    )
                )
                # Packaging (can use either packager)
                product_processes.append(
                    ProductProcess(
                        product_id=product.id,
                        process_id="PROC007",  # Packager 1
                        sequence=4,
                        quantity_per_batch=2000
                    )
                )
        
        db.add_all(product_processes)
        
        # Commit all changes
        db.commit()
        
        print("Database initialized with sample data successfully!")
        print(f"- Products: {len(products)}")
        print(f"- Equipment: {len(equipment_list)}")
        print(f"- Processes: {len(processes)}")
        print(f"- Product-Process mappings: {len(product_processes)}")

if __name__ == "__main__":
    init_sample_data()