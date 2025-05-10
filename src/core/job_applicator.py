import time
import pyautogui
from ..utils.logger import logger
from .window_manager import WindowManager
from ..ml.models.form_detector import FormElementDetector

class JobApplicator:
    def __init__(self, model_path=None):
        self.window_manager = WindowManager()
        self.model = FormElementDetector()
        if model_path:
            self.model.load_model(model_path)
        self.model.eval()
        
        # Default application data
        self.application_data = {
            'name': '',
            'email': '',
            'phone': '',
            'address': '',
            'city': '',
            'state': '',
            'zip': '',
            'experience': '',
            'education': '',
            'skills': ''
        }

    def set_application_data(self, data):
        """Update the application data with user-provided information."""
        self.application_data.update(data)

    def detect_form_elements(self, screenshot):
        """Detect form elements in the current view."""
        predictions = self.model.predict(screenshot)
        return predictions

    def fill_text_field(self, field_type, value):
        """Fill a text input field with the appropriate value."""
        # Click the field
        pyautogui.click()
        time.sleep(0.5)
        
        # Clear existing text
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        
        # Type the value
        pyautogui.write(value)
        time.sleep(0.5)

    def select_dropdown(self, option):
        """Select an option from a dropdown menu."""
        pyautogui.click()
        time.sleep(0.5)
        pyautogui.write(option)
        pyautogui.press('enter')
        time.sleep(0.5)

    def check_checkbox(self):
        """Check a checkbox."""
        pyautogui.click()
        time.sleep(0.5)

    def submit_application(self):
        """Submit the job application."""
        # Look for submit button
        screenshot = self.window_manager.take_screenshot()
        predictions = self.detect_form_elements(screenshot)
        
        if predictions['submit_button'] > 0.5:
            pyautogui.click()
            time.sleep(2)  # Wait for submission
            
            # Check for success message
            screenshot = self.window_manager.take_screenshot()
            predictions = self.detect_form_elements(screenshot)
            
            if predictions['success_message'] > 0.5:
                logger.info("Application submitted successfully!")
                return True
            elif predictions['error_message'] > 0.5:
                logger.error("Error submitting application. Please check the form.")
                return False
        
        return False

    def process_application_page(self):
        """Process the current application page."""
        screenshot = self.window_manager.take_screenshot()
        predictions = self.detect_form_elements(screenshot)
        
        # Process each detected element
        for element_type, confidence in predictions.items():
            if confidence > 0.5:  # Confidence threshold
                if element_type in ['text_input', 'email_input', 'phone_input']:
                    value = self.application_data.get(element_type.split('_')[0], '')
                    if value:
                        self.fill_text_field(element_type, value)
                
                elif element_type == 'dropdown':
                    # Handle dropdown selection
                    pass
                
                elif element_type == 'checkbox':
                    self.check_checkbox()
                
                elif element_type == 'required_field':
                    logger.warning("Required field detected. Please ensure it's filled.")

    def apply_to_job(self, url):
        """Main method to apply to a job posting."""
        try:
            # Navigate to the job posting
            pyautogui.hotkey('ctrl', 'l')  # Focus address bar
            time.sleep(0.5)
            pyautogui.write(url)
            pyautogui.press('enter')
            time.sleep(3)  # Wait for page load
            
            # Process the application
            self.process_application_page()
            
            # Submit if ready
            if self.submit_application():
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error applying to job: {str(e)}")
            return False 