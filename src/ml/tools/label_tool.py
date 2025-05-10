"""
Interactive tool for labeling game screenshots.
"""

import os
import json
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import argparse
from datetime import datetime

class LabelingTool:
    def __init__(self, data_dir):
        """
        Initialize the labeling tool.
        
        Args:
            data_dir: Directory containing raw images and labels
        """
        self.data_dir = data_dir
        self.raw_dir = os.path.join(data_dir, "raw")
        self.labels_dir = os.path.join(data_dir, "labels")
        
        # Create labels directory if it doesn't exist
        os.makedirs(self.labels_dir, exist_ok=True)
        
        # Get list of images
        self.images = [f for f in os.listdir(self.raw_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
        self.current_image_idx = 0
        
        # Define classes
        self.classes = [
            'enemy', 'item', 'npc', 'player', 'ui_element',
            'hp_bar', 'mana_bar', 'stamina_bar', 'exp_bar',
            'spell_cooldown',
            'spell_1_usable', 'spell_1_unusable',
            'spell_2_usable', 'spell_2_unusable',
            'spell_3_usable', 'spell_3_unusable',
            'spell_4_usable', 'spell_4_unusable',
            'spell_5_usable', 'spell_5_unusable',
            'spell_6_usable', 'spell_6_unusable',
            'spell_7_usable', 'spell_7_unusable',
            'spell_8_usable', 'spell_8_unusable',
            'corpse'  # Added corpse class for looting
        ]
        
        # Setup GUI
        self.root = tk.Tk()
        self.root.title("Game Screenshot Labeling Tool")
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the GUI components."""
        # Image display
        self.image_label = ttk.Label(self.root)
        self.image_label.pack(padx=10, pady=10)
        
        # Class selection
        self.class_var = tk.StringVar()
        class_frame = ttk.LabelFrame(self.root, text="Select Class")
        class_frame.pack(padx=10, pady=5, fill="x")
        
        # Create radio buttons for each class
        for i, class_name in enumerate(self.classes):
            ttk.Radiobutton(
                class_frame,
                text=class_name,
                value=class_name,
                variable=self.class_var
            ).grid(row=i//2, column=i%2, sticky="w", padx=5, pady=2)
        
        # Navigation buttons
        nav_frame = ttk.Frame(self.root)
        nav_frame.pack(padx=10, pady=5)
        
        ttk.Button(
            nav_frame,
            text="Previous",
            command=self.previous_image
        ).pack(side="left", padx=5)
        
        ttk.Button(
            nav_frame,
            text="Next",
            command=self.next_image
        ).pack(side="left", padx=5)
        
        ttk.Button(
            nav_frame,
            text="Save",
            command=self.save_label
        ).pack(side="left", padx=5)
        
        # Status label
        self.status_var = tk.StringVar()
        ttk.Label(
            self.root,
            textvariable=self.status_var
        ).pack(padx=10, pady=5)
        
        # Load first image
        self.load_current_image()
    
    def load_current_image(self):
        """Load and display the current image."""
        if not self.images:
            self.status_var.set("No images found!")
            return
            
        image_path = os.path.join(self.raw_dir, self.images[self.current_image_idx])
        image = Image.open(image_path)
        
        # Resize image if too large
        max_size = (800, 600)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(image)
        self.image_label.configure(image=photo)
        self.image_label.image = photo
        
        # Update status
        self.status_var.set(
            f"Image {self.current_image_idx + 1}/{len(self.images)}: {self.images[self.current_image_idx]}"
        )
        
        # Load existing label if any
        self.load_existing_label()
    
    def load_existing_label(self):
        """Load existing label for current image if available."""
        label_path = os.path.join(
            self.labels_dir,
            f"{os.path.splitext(self.images[self.current_image_idx])[0]}.json"
        )
        
        if os.path.exists(label_path):
            try:
                with open(label_path, 'r') as f:
                    data = json.load(f)
                    if 'label' in data:
                        self.class_var.set(data['label'])
            except Exception as e:
                print(f"Error loading label: {str(e)}")
    
    def save_label(self):
        """Save the current label."""
        if not self.images:
            return
            
        label = self.class_var.get()
        if not label:
            self.status_var.set("Please select a class!")
            return
            
        # Create label data
        label_data = {
            'image': self.images[self.current_image_idx],
            'label': label,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save to JSON file
        label_path = os.path.join(
            self.labels_dir,
            f"{os.path.splitext(self.images[self.current_image_idx])[0]}.json"
        )
        
        try:
            with open(label_path, 'w') as f:
                json.dump(label_data, f, indent=2)
            self.status_var.set("Label saved successfully!")
        except Exception as e:
            self.status_var.set(f"Error saving label: {str(e)}")
    
    def next_image(self):
        """Move to next image."""
        if self.current_image_idx < len(self.images) - 1:
            self.current_image_idx += 1
            self.load_current_image()
    
    def previous_image(self):
        """Move to previous image."""
        if self.current_image_idx > 0:
            self.current_image_idx -= 1
            self.load_current_image()
    
    def run(self):
        """Run the labeling tool."""
        self.root.mainloop()

def main():
    parser = argparse.ArgumentParser(description="Game Screenshot Labeling Tool")
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Directory containing raw images and labels"
    )
    args = parser.parse_args()
    
    tool = LabelingTool(args.data_dir)
    tool.run()

if __name__ == "__main__":
    main() 