Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\kttv\Desktop\radar-weather"
WshShell.Run """C:\Users\kttv\Desktop\radar-weather\run_auto_send_zalo.bat""", 1, False
