# Scheduling Service - Adapts original APS scheduling logic for web API
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
from models import Product, Equipment, Process, ProductProcess, Batch, SalesPlan
from sqlalchemy.orm import Session
import uuid

class SchedulerService:
    """
    스케줄링 서비스 - 레고 블록 방식의 스케줄링 로직 구현
    하루를 4개 구간(2시간씩)으로 나누어 스케줄링
    """
    
    SLOTS_PER_DAY = 4  # 하루 4개 구간
    HOURS_PER_SLOT = 2  # 구간당 2시간
    
    def __init__(self, db_session: Session):
        self.db = db_session
        
    def generate_schedule_from_sales(self, sales_plans: List[SalesPlan]) -> List[Batch]:
        """판매계획으로부터 생산 스케줄 생성"""
        batches = []
        
        # 장비별 구간별 할당 관리
        equipment_slots = {}  # {(equipment_id, date, slot): is_occupied}
        
        # 우선순위에 따라 판매계획 정렬
        sorted_plans = sorted(sales_plans, key=lambda x: x.priority)
        
        for plan in sorted_plans:
            # 제품의 공정 정보 조회
            product_processes = self.db.query(ProductProcess).filter_by(
                product_id=plan.product_id
            ).order_by(ProductProcess.sequence).all()
            
            if not product_processes:
                continue
                
            # 각 공정별로 배치 생성
            for pp in product_processes:
                process = pp.process
                equipment = process.equipment
                
                # 필요한 슬롯 수 계산
                required_slots = self._calculate_required_slots(
                    pp.quantity_per_batch,
                    process.duration_hours + process.setup_time_hours
                )
                
                # 사용 가능한 슬롯 찾기
                start_date = datetime(plan.year, plan.month, 1)
                slot_info = self._find_available_slots(
                    equipment.id,
                    start_date,
                    required_slots,
                    equipment_slots
                )
                
                if slot_info:
                    # 배치 생성
                    batch = self._create_batch(
                        plan.product,
                        equipment,
                        process.name,
                        pp.quantity_per_batch,
                        slot_info['start_time'],
                        slot_info['end_time']
                    )
                    batches.append(batch)
                    
                    # 슬롯 할당 업데이트
                    for slot in slot_info['slots']:
                        equipment_slots[slot] = True
                        
        return batches
    
    def _calculate_required_slots(self, quantity: int, duration_hours: float) -> int:
        """필요한 슬롯 수 계산"""
        return max(1, int((duration_hours + self.HOURS_PER_SLOT - 1) // self.HOURS_PER_SLOT))
    
    def _find_available_slots(self, equipment_id: str, start_date: datetime, 
                            required_slots: int, equipment_slots: Dict) -> Optional[Dict]:
        """사용 가능한 연속 슬롯 찾기"""
        current_date = start_date
        consecutive_slots = []
        
        for day in range(30):  # 최대 30일까지 검색
            for slot in range(self.SLOTS_PER_DAY):
                slot_key = (equipment_id, current_date.date(), slot)
                
                if slot_key not in equipment_slots or not equipment_slots[slot_key]:
                    consecutive_slots.append(slot_key)
                    
                    if len(consecutive_slots) >= required_slots:
                        # 시작 시간과 종료 시간 계산
                        first_slot = consecutive_slots[0]
                        last_slot = consecutive_slots[-1]
                        
                        start_time = datetime.combine(
                            first_slot[1], 
                            datetime.min.time()
                        ) + timedelta(hours=first_slot[2] * self.HOURS_PER_SLOT)
                        
                        end_time = datetime.combine(
                            last_slot[1],
                            datetime.min.time()
                        ) + timedelta(hours=(last_slot[2] + 1) * self.HOURS_PER_SLOT)
                        
                        return {
                            'slots': consecutive_slots[:required_slots],
                            'start_time': start_time,
                            'end_time': end_time
                        }
                else:
                    consecutive_slots = []
                    
            current_date += timedelta(days=1)
            
        return None
    
    def _create_batch(self, product: Product, equipment: Equipment, 
                     process_name: str, quantity: int, 
                     start_time: datetime, end_time: datetime) -> Batch:
        """배치 생성"""
        lot_number = self._generate_lot_number(product.code, start_time)
        
        batch = Batch(
            id=str(uuid.uuid4()),
            lot_number=lot_number,
            product_id=product.id,
            equipment_id=equipment.id,
            process_name=process_name,
            quantity=quantity,
            start_time=start_time,
            end_time=end_time,
            status='planned'
        )
        
        return batch
    
    def _generate_lot_number(self, product_code: str, date: datetime) -> str:
        """로트 번호 생성"""
        date_str = date.strftime('%Y%m%d')
        # 실제로는 데이터베이스에서 당일 순번을 조회해야 함
        sequence = 1
        return f"LOT-{product_code}-{date_str}-{sequence:03d}"
    
    def optimize_schedule(self, batches: List[Batch]) -> List[Batch]:
        """스케줄 최적화 - 장비 활용률 향상"""
        # TODO: 구현 필요
        # 1. 유사 제품 그룹화
        # 2. 셋업 시간 최소화
        # 3. 장비 가동률 최대화
        return batches
    
    def validate_schedule(self, batches: List[Batch]) -> Dict[str, any]:
        """스케줄 검증"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }
        
        # 장비별 중복 검사
        equipment_timeline = {}
        for batch in batches:
            if batch.equipment_id not in equipment_timeline:
                equipment_timeline[batch.equipment_id] = []
            equipment_timeline[batch.equipment_id].append((batch.start_time, batch.end_time))
        
        # 시간 중복 검사
        for equipment_id, timeline in equipment_timeline.items():
            timeline.sort()
            for i in range(1, len(timeline)):
                if timeline[i][0] < timeline[i-1][1]:
                    validation_result['is_valid'] = False
                    validation_result['errors'].append(
                        f"Equipment {equipment_id} has overlapping schedules"
                    )
        
        # 통계 계산
        validation_result['statistics']['total_batches'] = len(batches)
        validation_result['statistics']['equipment_utilization'] = self._calculate_utilization(equipment_timeline)
        
        return validation_result
    
    def _calculate_utilization(self, equipment_timeline: Dict) -> Dict[str, float]:
        """장비 활용률 계산"""
        utilization = {}
        
        for equipment_id, timeline in equipment_timeline.items():
            if not timeline:
                utilization[equipment_id] = 0.0
                continue
                
            # 전체 작업 시간 계산
            total_hours = sum((end - start).total_seconds() / 3600 
                            for start, end in timeline)
            
            # 전체 기간 계산
            min_start = min(start for start, _ in timeline)
            max_end = max(end for _, end in timeline)
            total_period_hours = (max_end - min_start).total_seconds() / 3600
            
            utilization[equipment_id] = (total_hours / total_period_hours * 100) if total_period_hours > 0 else 0
            
        return utilization