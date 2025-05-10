import os
import time
import cv2
import numpy as np
from PIL import Image
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class FormDataCollector:
    def __init__(self, data_dir="data"):
        """
        Initialize the form data collector.
        
        Args:
            data_dir: Directory to store collected data
        """
        self.data_dir = data_dir
        self._setup_directories()
        self._setup_browser()
    
    def _setup_directories(self):
        """Create necessary directories for data storage."""
        try:
            # Create main data directory
            os.makedirs(self.data_dir, exist_ok=True)
            
            # Create subdirectories for different form elements
            self.element_dirs = {
                'text_input': os.path.join(self.data_dir, 'raw', 'text_input'),
                'email_input': os.path.join(self.data_dir, 'raw', 'email_input'),
                'phone_input': os.path.join(self.data_dir, 'raw', 'phone_input'),
                'dropdown': os.path.join(self.data_dir, 'raw', 'dropdown'),
                'checkbox': os.path.join(self.data_dir, 'raw', 'checkbox'),
                'radio_button': os.path.join(self.data_dir, 'raw', 'radio_button'),
                'submit_button': os.path.join(self.data_dir, 'raw', 'submit_button'),
                'error_message': os.path.join(self.data_dir, 'raw', 'error_message'),
                'success_message': os.path.join(self.data_dir, 'raw', 'success_message'),
                'required_field': os.path.join(self.data_dir, 'raw', 'required_field')
            }
            
            for dir_path in self.element_dirs.values():
                os.makedirs(dir_path, exist_ok=True)
                
            print(f"Created data directories at {self.data_dir}")
        except Exception as e:
            print(f"Failed to create data directories: {str(e)}")
            raise

    def _setup_browser(self):
        """Set up Chrome browser for form interaction."""
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def collect_form_elements(self, html_path, num_samples=100, delay=1.0):
        """
        Collect screenshots of form elements from the HTML form.
        
        Args:
            html_path: Path to the HTML form file
            num_samples: Number of samples to collect per element type
            delay: Delay between captures in seconds
        """
        try:
            print("Starting form element data collection...")
            
            # Load the HTML form
            self.driver.get(f"file:///{os.path.abspath(html_path)}")
            time.sleep(2)  # Wait for page to load
            
            # Create a window to display instructions
            cv2.namedWindow('Instructions', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Instructions', 600, 400)
            
            instructions = """
            Form Element Collection
            ======================
            
            Form Elements (1-0):
            1: Text Input
            2: Email Input
            3: Phone Input
            4: Dropdown
            5: Checkbox
            6: Radio Button
            7: Submit Button
            8: Error Message
            9: Success Message
            0: Required Field
            
            Press 'q' to quit
            """
            
            # Convert instructions to image
            img = np.zeros((400, 600, 3), dtype=np.uint8)
            y = 30
            for line in instructions.split('\n'):
                cv2.putText(img, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                y += 20
            
            cv2.imshow('Instructions', img)
            
            while True:
                # Take screenshot
                screenshot = self.driver.get_screenshot_as_png()
                screenshot = Image.open(BytesIO(screenshot))
                
                # Convert to OpenCV format for display
                cv_image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                # Display the screenshot
                cv2.imshow('Form Element Collection', cv_image)
                
                # Wait for key press
                key = cv2.waitKey(int(delay * 1000))
                
                # If 'q' is pressed, quit
                if key == ord('q'):
                    break
                
                # If a number key (1-0) is pressed, save the screenshot
                if key in [ord(str(i)) for i in range(10)]:
                    element_type = list(self.element_dirs.keys())[key - ord('1')]
                    self._save_screenshot(screenshot, element_type)
                
            cv2.destroyAllWindows()
            print("Data collection completed.")
            
        except KeyboardInterrupt:
            print("Data collection interrupted by user.")
            cv2.destroyAllWindows()
        except Exception as e:
            print(f"Error during data collection: {str(e)}")
            cv2.destroyAllWindows()
            raise
        finally:
            self.driver.quit()

    def _save_screenshot(self, screenshot, element_type):
        """Save a screenshot with the given element type."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{element_type}_{timestamp}.png"
        filepath = os.path.join(self.element_dirs[element_type], filename)
        screenshot.save(filepath)
        print(f"Saved {element_type} screenshot to {filepath}")

if __name__ == "__main__":
    import argparse
    from io import BytesIO
    
    parser = argparse.ArgumentParser(description='Collect form element training data')
    parser.add_argument('--html-path', type=str, required=True, help='Path to the HTML form file')
    parser.add_argument('--num-samples', type=int, default=100, help='Number of samples to collect per element type')
    parser.add_argument('--data-dir', type=str, default='data', help='Directory to store collected data')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between captures in seconds')
    
    args = parser.parse_args()
    
    collector = FormDataCollector(data_dir=args.data_dir)
    collector.collect_form_elements(args.html_path, args.num_samples, args.delay) 