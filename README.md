# Job Application Automation Bot

A machine learning-powered system for automating job applications on any website using computer vision and form detection.

---

## Features
- **Full-page screenshot capture** (Selenium)
- **Bounding box annotation** (LabelImg repository, YOLO format)
- **Object detection model** (YOLOv5) for form element localization
- **Automated form filling** (optional, via vision-based bot)
- **Modular, clean project structure**

---

## Tech Stack

**Languages & Frameworks:**
- Python 3.8+
- PyTorch 2.2.0
- YOLOv5 (Ultralytics)
- OpenCV
- Pillow
- NumPy
- Selenium
- LabelImg (cloned repository)
- pyautogui (for automation)

**Supporting Tools:**
- VS Code (recommended)
- Git (version control)
- Windows 10/11 (tested)

**ML/AI:**
- Object detection: YOLOv5 (custom-trained on annotated screenshots)
- Annotation: LabelImg repository (YOLO format)

---

## Project Structure

```
project_root/
│
├── src/
│   ├── ml/
│   │   ├── data/         # Data scripts
│   │   ├── models/       # Model architectures
│   │   ├── training/     # Training scripts
│   │   └── utils/        # Screenshot and helper scripts
│   └── core/             # Automation logic
│
├── data/
│   ├── images/           # Screenshots for training
│   ├── labels/           # YOLO-format label files
│   ├── classes.txt       # UI element classes for LabelImg
│   └── training_forms/   # HTML forms for screenshotting
│
├── labelImg/            # Cloned LabelImg repository
├── models/              # Saved model weights
├── yolov5/              # YOLOv5 repo (for training/inference)
├── requirements.txt
├── run_labelimg.bat     # Quick start script for LabelImg
├── README.md
└── state.txt           # Project status and progress
```

---

## Quickstart Instructions

1. **Set up the environment:**
   ```
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Take full-page screenshots:**
   ```
   python src/ml/utils/screenshot_fullpage.py --url "file:///C:/projects/ezjob/data/training_forms/job_application.html" --output data/images/form1.png
   ```

3. **Annotate with LabelImg:**
   ```
   # Using the provided batch file
   .\run_labelimg.bat
   
   # Or manually:
   cd labelImg
   pyrcc5 -o libs/resources.py resources.qrc
   python labelImg.py ..\data\images ..\data\classes.txt ..\data\labels
   ```

4. **Prepare data.yaml:**
   ```yaml
   train: ../data/images
   val: ../data/images
   nc: 80  # Number of classes
   names: [ 'firstname_label', 'lastname_label', 'email_label', ... ]  # See classes.txt for full list
   ```

5. **Train YOLOv5:**
   ```
   cd yolov5
   pip install -r requirements.txt
   python train.py --img 640 --batch 16 --epochs 20 --data ../data.yaml --weights yolov5s.pt
   ```

6. **Run inference:**
   ```
   python detect.py --weights runs/train/exp/weights/best.pt --source ../data/images
   ```

7. **(Optional) Use the automation bot:**
   - See `src/core/job_applicator.py` for vision-based form filling.

---

## Troubleshooting
- Ensure all paths in `data.yaml` are correct
- Use YOLO format for annotation
- If LabelImg crashes on scroll, use arrow keys for navigation
- Make sure to check "Auto Save" and "Save With YOLO Format" in LabelImg's View menu
- For help, see `state.txt` or ask your assistant

## Safety and Ethics

This bot is for educational purposes only. Please ensure you comply with website terms of service and rules regarding automation.

## License

MIT License 