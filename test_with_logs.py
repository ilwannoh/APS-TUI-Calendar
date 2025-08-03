"""
로그 기반 디버깅 테스트 스크립트
실제 시나리오를 시뮬레이션하고 로그를 분석
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path

class LogBasedTester:
    def __init__(self):
        self.api_url = "http://localhost:8000"
        self.log_file = Path("backend/logs/api_server.log")
        self.test_log = []
        
    def print_log(self, message, level="INFO"):
        """테스트 로그 출력"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{level}] {message}"
        print(log_msg)
        self.test_log.append(log_msg)
        
    def read_recent_logs(self, lines=10):
        """최근 서버 로그 읽기"""
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return all_lines[-lines:] if len(all_lines) > lines else all_lines
        return []
        
    def test_error_scenario(self):
        """에러 시나리오 테스트"""
        self.print_log("=== 에러 시나리오 테스트 시작 ===")
        
        # 1. 잘못된 엔드포인트 호출
        self.print_log("잘못된 엔드포인트 호출 테스트")
        try:
            r = requests.get(f"{self.api_url}/api/invalid-endpoint")
            self.print_log(f"응답 상태: {r.status_code}", "WARNING" if r.status_code != 200 else "INFO")
        except Exception as e:
            self.print_log(f"요청 실패: {str(e)}", "ERROR")
            
        # 2. 잘못된 메서드 호출
        self.print_log("잘못된 HTTP 메서드 테스트")
        try:
            r = requests.post(f"{self.api_url}/api/equipment")  # GET이어야 하는데 POST 호출
            self.print_log(f"응답 상태: {r.status_code}", "WARNING" if r.status_code != 200 else "INFO")
        except Exception as e:
            self.print_log(f"요청 실패: {str(e)}", "ERROR")
            
    def test_performance_scenario(self):
        """성능 테스트 시나리오"""
        self.print_log("=== 성능 테스트 시작 ===")
        
        # 연속 API 호출
        self.print_log("연속 10회 API 호출 테스트")
        response_times = []
        
        for i in range(10):
            start_time = time.time()
            try:
                r = requests.get(f"{self.api_url}/api/equipment")
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # ms
                response_times.append(response_time)
                self.print_log(f"호출 {i+1}: {response_time:.2f}ms")
            except Exception as e:
                self.print_log(f"호출 {i+1} 실패: {str(e)}", "ERROR")
                
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            self.print_log(f"평균 응답 시간: {avg_time:.2f}ms")
            
    def test_data_consistency(self):
        """데이터 일관성 테스트"""
        self.print_log("=== 데이터 일관성 테스트 ===")
        
        # 1. 스케줄 생성 전 상태 확인
        r1 = requests.get(f"{self.api_url}/api/schedule")
        before_count = len(r1.json().get("batches", []))
        self.print_log(f"스케줄 생성 전 배치 수: {before_count}")
        
        # 2. 스케줄 생성
        r2 = requests.post(f"{self.api_url}/api/schedule/generate")
        result = r2.json()
        self.print_log(f"스케줄 생성 결과: {result}")
        
        # 3. 스케줄 생성 후 상태 확인
        r3 = requests.get(f"{self.api_url}/api/schedule")
        after_count = len(r3.json().get("batches", []))
        self.print_log(f"스케줄 생성 후 배치 수: {after_count}")
        
        # 4. 데이터 검증
        if after_count == result.get("batches_created", 0):
            self.print_log("데이터 일관성 확인: PASS", "INFO")
        else:
            self.print_log(f"데이터 불일치! 생성: {result.get('batches_created')}, 실제: {after_count}", "ERROR")
            
    def test_batch_operations(self):
        """배치 작업 테스트"""
        self.print_log("=== 배치 작업 테스트 ===")
        
        # 1. 현재 배치 가져오기
        r = requests.get(f"{self.api_url}/api/schedule")
        batches = r.json().get("batches", [])
        
        if batches:
            first_batch = batches[0]
            batch_id = first_batch["id"]
            
            # 2. 배치 수정 테스트
            self.print_log(f"배치 {batch_id} 수정 테스트")
            update_data = {"quantity": 2000}
            r_update = requests.put(f"{self.api_url}/api/batches/{batch_id}", json=update_data)
            self.print_log(f"수정 결과: {r_update.json()}")
            
            # 3. 배치 삭제 테스트
            self.print_log(f"배치 {batch_id} 삭제 테스트")
            r_delete = requests.delete(f"{self.api_url}/api/batches/{batch_id}")
            self.print_log(f"삭제 결과: {r_delete.json()}")
            
    def analyze_logs(self):
        """로그 분석"""
        self.print_log("=== 서버 로그 분석 ===")
        recent_logs = self.read_recent_logs(20)
        
        error_count = 0
        warning_count = 0
        info_count = 0
        
        for log_line in recent_logs:
            if "[ERROR]" in log_line:
                error_count += 1
                self.print_log(f"에러 발견: {log_line.strip()}", "ERROR")
            elif "[WARNING]" in log_line:
                warning_count += 1
            elif "[INFO]" in log_line:
                info_count += 1
                
        self.print_log(f"로그 요약 - INFO: {info_count}, WARNING: {warning_count}, ERROR: {error_count}")
        
    def generate_test_report(self):
        """테스트 리포트 생성"""
        report_path = Path("backend/logs/detailed_test_report.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=== APS 시스템 상세 테스트 리포트 ===\n")
            f.write(f"테스트 일시: {datetime.now()}\n")
            f.write("="*50 + "\n\n")
            
            for log in self.test_log:
                f.write(log + "\n")
                
        self.print_log(f"테스트 리포트 생성 완료: {report_path}")
        
    def run_all_tests(self):
        """모든 테스트 실행"""
        self.print_log("APS 시스템 로그 기반 테스트 시작", "INFO")
        
        # API 서버 확인
        try:
            r = requests.get(f"{self.api_url}/")
            if r.status_code == 200:
                self.print_log("API 서버 정상 작동 확인", "INFO")
            else:
                self.print_log("API 서버 응답 이상", "ERROR")
                return
        except:
            self.print_log("API 서버에 연결할 수 없습니다", "ERROR")
            return
            
        # 각 테스트 시나리오 실행
        self.test_error_scenario()
        time.sleep(1)
        
        self.test_performance_scenario()
        time.sleep(1)
        
        self.test_data_consistency()
        time.sleep(1)
        
        self.test_batch_operations()
        time.sleep(1)
        
        self.analyze_logs()
        
        # 리포트 생성
        self.generate_test_report()
        
        self.print_log("모든 테스트 완료", "INFO")

if __name__ == "__main__":
    tester = LogBasedTester()
    tester.run_all_tests()