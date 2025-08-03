"""
APS 시스템 자동 테스트 스크립트
로그를 생성하고 분석하여 시스템이 정상 작동하는지 확인
"""

import requests
import json
import time
import os
from datetime import datetime
from pathlib import Path

class APSSystemTester:
    def __init__(self, api_url="http://localhost:8000", log_dir="backend/logs"):
        self.api_url = api_url
        self.log_dir = Path(log_dir)
        self.test_results = []
        
    def log_test(self, test_name, result, details=""):
        """테스트 결과 로깅"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "test": test_name,
            "result": "PASS" if result else "FAIL",
            "details": details
        }
        self.test_results.append(log_entry)
        print(f"[{log_entry['result']}] {test_name}: {details}")
        
    def test_api_health(self):
        """API 서버 상태 확인"""
        try:
            response = requests.get(f"{self.api_url}/")
            success = response.status_code == 200
            self.log_test("API Health Check", success, 
                         f"Status: {response.status_code}, Response: {response.json()}")
            return success
        except Exception as e:
            self.log_test("API Health Check", False, f"Error: {str(e)}")
            return False
            
    def test_equipment_endpoint(self):
        """장비 목록 API 테스트"""
        try:
            response = requests.get(f"{self.api_url}/api/equipment")
            data = response.json()
            success = response.status_code == 200 and len(data) == 8
            self.log_test("Equipment API", success, 
                         f"Returned {len(data)} equipment items")
            return success
        except Exception as e:
            self.log_test("Equipment API", False, f"Error: {str(e)}")
            return False
            
    def test_products_endpoint(self):
        """제품 목록 API 테스트"""
        try:
            response = requests.get(f"{self.api_url}/api/products")
            data = response.json()
            success = response.status_code == 200 and len(data) == 8
            self.log_test("Products API", success, 
                         f"Returned {len(data)} product items")
            return success
        except Exception as e:
            self.log_test("Products API", False, f"Error: {str(e)}")
            return False
            
    def test_schedule_generation(self):
        """스케줄 생성 API 테스트"""
        try:
            # 스케줄 생성
            response = requests.post(f"{self.api_url}/api/schedule/generate")
            data = response.json()
            success = response.status_code == 200 and data.get("success") == True
            batches_created = data.get("batches_created", 0)
            
            self.log_test("Schedule Generation", success, 
                         f"Created {batches_created} batches")
            
            # 생성된 스케줄 조회
            if success:
                schedule_response = requests.get(f"{self.api_url}/api/schedule")
                schedule_data = schedule_response.json()
                batches = schedule_data.get("batches", [])
                
                self.log_test("Schedule Retrieval", len(batches) > 0, 
                             f"Retrieved {len(batches)} batches")
                
                # 스케줄 검증
                if len(batches) > 0:
                    self.validate_schedule(batches)
                    
            return success
        except Exception as e:
            self.log_test("Schedule Generation", False, f"Error: {str(e)}")
            return False
            
    def validate_schedule(self, batches):
        """생성된 스케줄 검증"""
        # 시간 순서 검증
        sorted_batches = sorted(batches, key=lambda x: x['start_time'])
        time_order_valid = sorted_batches == batches
        self.log_test("Schedule Time Order", time_order_valid, 
                     "Batches are in chronological order" if time_order_valid else "Time order issue detected")
        
        # 장비 중복 검증
        equipment_timeline = {}
        overlap_found = False
        
        for batch in batches:
            eq_id = batch['equipment_id']
            start = datetime.fromisoformat(batch['start_time'])
            end = datetime.fromisoformat(batch['end_time'])
            
            if eq_id not in equipment_timeline:
                equipment_timeline[eq_id] = []
                
            # 중복 체크
            for existing_start, existing_end in equipment_timeline[eq_id]:
                if start < existing_end and end > existing_start:
                    overlap_found = True
                    self.log_test("Equipment Overlap Check", False, 
                                 f"Overlap found for {eq_id}")
                    break
                    
            equipment_timeline[eq_id].append((start, end))
            
        if not overlap_found:
            self.log_test("Equipment Overlap Check", True, 
                         "No equipment scheduling conflicts")
            
    def check_logs(self):
        """로그 파일 확인"""
        if self.log_dir.exists():
            log_files = list(self.log_dir.glob("*.log"))
            self.log_test("Log Files Check", len(log_files) > 0, 
                         f"Found {len(log_files)} log files")
            
            # 최신 로그 내용 확인
            for log_file in log_files:
                if log_file.stat().st_size > 0:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        last_lines = lines[-5:] if len(lines) > 5 else lines
                        print(f"\nLast entries from {log_file.name}:")
                        for line in last_lines:
                            print(f"  {line.strip()}")
        else:
            self.log_test("Log Files Check", False, "Log directory not found")
            
    def generate_report(self):
        """테스트 리포트 생성"""
        print("\n" + "="*50)
        print("APS SYSTEM TEST REPORT")
        print("="*50)
        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Tests: {len(self.test_results)}")
        
        passed = sum(1 for r in self.test_results if r['result'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['result'] == 'FAIL')
        
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/len(self.test_results)*100):.1f}%")
        print("="*50)
        
        # 실패한 테스트 상세
        if failed > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if result['result'] == 'FAIL':
                    print(f"- {result['test']}: {result['details']}")
                    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("Starting APS System Tests...")
        print("="*50)
        
        # API 테스트
        if self.test_api_health():
            self.test_equipment_endpoint()
            self.test_products_endpoint()
            self.test_schedule_generation()
        else:
            print("API server not responding. Please check if the server is running.")
            
        # 로그 확인
        self.check_logs()
        
        # 리포트 생성
        self.generate_report()

if __name__ == "__main__":
    # 테스트 실행
    tester = APSSystemTester()
    tester.run_all_tests()
    
    # 테스트 결과를 로그 파일로 저장
    test_log_path = Path("backend/logs/test_results.json")
    test_log_path.parent.mkdir(exist_ok=True)
    
    with open(test_log_path, 'w', encoding='utf-8') as f:
        json.dump(tester.test_results, f, indent=2, ensure_ascii=False)