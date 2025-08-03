"""
로그 파일 뷰어 - 최근 로그를 확인하고 분석
"""

from pathlib import Path
import sys

def view_log_file(log_path, lines=50):
    """로그 파일의 마지막 N줄을 출력"""
    try:
        # 다양한 인코딩 시도
        encodings = ['utf-8', 'cp949', 'euc-kr', 'latin1']
        
        for encoding in encodings:
            try:
                with open(log_path, 'r', encoding=encoding) as f:
                    all_lines = f.readlines()
                    recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                    
                    print(f"\n=== {log_path.name} (인코딩: {encoding}) ===")
                    print(f"총 {len(all_lines)}줄, 최근 {len(recent_lines)}줄 표시\n")
                    
                    for line in recent_lines:
                        print(line.rstrip())
                    
                    # 로그 분석
                    error_count = sum(1 for line in all_lines if '[ERROR]' in line)
                    warning_count = sum(1 for line in all_lines if '[WARNING]' in line)
                    info_count = sum(1 for line in all_lines if '[INFO]' in line)
                    
                    print(f"\n로그 통계:")
                    print(f"- INFO: {info_count}개")
                    print(f"- WARNING: {warning_count}개")
                    print(f"- ERROR: {error_count}개")
                    
                    return True
                    
            except UnicodeDecodeError:
                continue
                
        print(f"로그 파일을 읽을 수 없습니다: {log_path}")
        return False
        
    except FileNotFoundError:
        print(f"로그 파일이 없습니다: {log_path}")
        return False

def main():
    # 로그 디렉토리
    log_dir = Path("backend/logs")
    
    if not log_dir.exists():
        print(f"로그 디렉토리가 없습니다: {log_dir}")
        return
        
    # 모든 로그 파일 찾기
    log_files = list(log_dir.glob("*.log"))
    
    if not log_files:
        print("로그 파일이 없습니다.")
        return
        
    print(f"발견된 로그 파일: {len(log_files)}개")
    
    # 각 로그 파일 보기
    for log_file in log_files:
        view_log_file(log_file, lines=30)
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()