# Database Models for APS System
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import uuid

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(String(50), primary_key=True)
    code = Column(String(100), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    category = Column(String(100))
    unit = Column(String(50))
    description = Column(String(500))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    processes = relationship("ProductProcess", back_populates="product")
    batches = relationship("Batch", back_populates="product")

class Equipment(Base):
    __tablename__ = 'equipment'
    
    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    type = Column(String(100), nullable=False)
    capacity = Column(Integer)
    efficiency = Column(Float, default=0.85)
    status = Column(String(50), default='available')
    maintenance_schedule = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    processes = relationship("Process", back_populates="equipment")
    batches = relationship("Batch", back_populates="equipment")

class Process(Base):
    __tablename__ = 'processes'
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    type = Column(String(100), nullable=False)
    equipment_id = Column(String(50), ForeignKey('equipment.id'))
    duration_hours = Column(Float, nullable=False)
    setup_time_hours = Column(Float, default=0.5)
    
    # Relationships
    equipment = relationship("Equipment", back_populates="processes")
    product_processes = relationship("ProductProcess", back_populates="process")

class ProductProcess(Base):
    __tablename__ = 'product_processes'
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(50), ForeignKey('products.id'))
    process_id = Column(String(50), ForeignKey('processes.id'))
    sequence = Column(Integer, nullable=False)
    quantity_per_batch = Column(Integer)
    
    # Relationships
    product = relationship("Product", back_populates="processes")
    process = relationship("Process", back_populates="product_processes")

class SalesPlan(Base):
    __tablename__ = 'sales_plans'
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(50), ForeignKey('products.id'))
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    priority = Column(Integer, default=1)
    status = Column(String(50), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = relationship("Product")

class Batch(Base):
    __tablename__ = 'batches'
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    lot_number = Column(String(100), unique=True, nullable=False)
    product_id = Column(String(50), ForeignKey('products.id'))
    equipment_id = Column(String(50), ForeignKey('equipment.id'))
    process_name = Column(String(200))
    quantity = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String(50), default='planned')
    actual_start = Column(DateTime)
    actual_end = Column(DateTime)
    notes = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="batches")
    equipment = relationship("Equipment", back_populates="batches")

class Schedule(Base):
    __tablename__ = 'schedules'
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200))
    version = Column(Integer, default=1)
    status = Column(String(50), default='draft')
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    created_by = Column(String(100))
    approved_by = Column(String(100))
    approved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database setup
def init_db(database_url="sqlite:///aps.db"):
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    return engine

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()