@echo off
echo ======================================
echo GitHub 푸시 스크립트
echo ======================================
echo.
echo 이 스크립트를 실행하기 전에:
echo 1. https://github.com/new 에서 새 리포지토리 생성
echo    - Repository name: APS-TUI-Calendar
echo    - Public 선택
echo.
echo 2. 리포지토리 생성 후 이 스크립트 실행
echo.
pause

echo.
echo GitHub에 푸시 중...
git push -u origin main

echo.
echo 완료!
echo GitHub URL: https://github.com/ilwannoh/APS-TUI-Calendar
pause