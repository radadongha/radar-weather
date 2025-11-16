@echo off
:: --- Bật UTF-8 để tránh lỗi Unicode ---
chcp 65001 >nul
set PYTHONIOENCODING=utf-8

:: --- Ghi log để kiểm tra lịch sử chạy ---
set LOGFILE=D:\WinSCP\RADA\zalo_log.txt
echo === Run at %date% %time% === >> %LOGFILE%

:: --- Di chuyển tới thư mục chứa script ---
cd /d "C:\Users\kttv\Desktop\radar-weather"

:: --- Chạy script Python ---
"C:\Users\kttv\AppData\Local\Programs\Python\Python313\python.exe" "auto_send_zalo.py" >> %LOGFILE% 2>&1

:: --- Ghi trạng thái kết thúc ---
echo [OK] Finished at %time% >> %LOGFILE%
exit /b
