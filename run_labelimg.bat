@echo off
REM Run LabelImg with the correct paths
REM Usage: Just double-click this file to start LabelImg

REM Change to the labelImg directory
cd labelImg

REM Run LabelImg with explicit paths
REM Format: python labelImg.py [image_dir] [class_file] [save_dir]
python labelImg.py ..\data\images ..\data\classes.txt ..\data\labels

REM If you want to keep the window open after LabelImg closes, uncomment the next line:
REM pause 