@echo off
setlocal

call :runme call  app\omni.code.bat --ext-folder exts --enable robotica.io.spacemouse %* <NUL

goto :eof

:runme
%*
goto :eof
