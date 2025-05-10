"""
Interactive tool for labeling UI screenshots.
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
            data_dir: Directory containing images and labels
        """
        # Initialize zoom variables first
        self.zoom_level = 1.0
        self.original_image = None
        
        self.data_dir = data_dir
        self.images_dir = os.path.join(data_dir, "images")
        self.labels_dir = os.path.join(data_dir, "labels")
        
        # Create labels directory if it doesn't exist
        os.makedirs(self.labels_dir, exist_ok=True)
        
        # Get list of images
        self.images = [f for f in os.listdir(self.images_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
        self.current_image_idx = 0
        
        # Define classes from data.yaml
        self.classes = [
            'text_input', 'email_input', 'phone_input', 'dropdown', 'dropdown_option',
            'checkbox', 'radio_button', 'submit_button', 'error_message', 'success_message',
            'required_field', 'successful_indeed_button', 'unsuccessful_indeed_button',
            'salary', 'Full-time', 'Part-Time', 'Monday_to_Friday', 'Health_Insurance',
            'Life_Insurance', 'Dental_Insurance', '401k', 'Disability_Insurance',
            'Parental_Leave', 'Paid_Training', 'Referral_Program', 'Flexible_Schedule',
            'Work_from_Home', 'Pay_Information_not_provided', 'response_time',
            'Day_Shift', 'Night_Shift', 'applynow_button', 'bookmark_button',
            'thumbsdown_button', 'link_button', 'indeedwebsitelink',
            'skilltag_unclicked', 'skilltag_clicked'
        ]
        
        # Bounding box variables
        self.current_box = None
        self.boxes = []  # List of (class_idx, x, y, w, h) tuples
        self.start_x = None
        self.start_y = None
        
        # Setup GUI
        self.root = tk.Tk()
        self.root.title("UI Element Labeling Tool")
        self.root.state('zoomed')  # Start maximized
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the GUI components."""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)
        
        # Left panel for image
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Image display with scrollbars
        self.canvas_frame = ttk.Frame(left_panel)
        self.canvas_frame.pack(fill="both", expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame)
        self.scrollbar_y = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar_x = ttk.Scrollbar(self.canvas_frame, orient="horizontal", command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        
        self.scrollbar_y.pack(side="right", fill="y")
        self.scrollbar_x.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Right panel for controls
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side="right", fill="y", padx=10, pady=10)
        
        # Zoom controls
        zoom_frame = ttk.LabelFrame(right_panel, text="Zoom Controls")
        zoom_frame.pack(fill="x", pady=5)
        
        ttk.Button(zoom_frame, text="Zoom In (+)", command=lambda: self.zoom(1.2)).pack(fill="x", pady=2)
        ttk.Button(zoom_frame, text="Zoom Out (-)", command=lambda: self.zoom(0.8)).pack(fill="x", pady=2)
        ttk.Button(zoom_frame, text="Reset Zoom (1)", command=lambda: self.zoom(1.0)).pack(fill="x", pady=2)
        
        # Class selection with search
        class_frame = ttk.LabelFrame(right_panel, text="Select Class")
        class_frame.pack(fill="x", pady=5)
        
        # Search box
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_classes)
        ttk.Entry(class_frame, textvariable=self.search_var).pack(fill="x", pady=2)
        
        # Class listbox with scrollbar
        class_list_frame = ttk.Frame(class_frame)
        class_list_frame.pack(fill="both", expand=True)
        
        self.class_listbox = tk.Listbox(class_list_frame, selectmode="single", height=20)
        class_scrollbar = ttk.Scrollbar(class_list_frame, orient="vertical", command=self.class_listbox.yview)
        self.class_listbox.configure(yscrollcommand=class_scrollbar.set)
        
        class_scrollbar.pack(side="right", fill="y")
        self.class_listbox.pack(side="left", fill="both", expand=True)
        
        # Box controls
        box_frame = ttk.LabelFrame(right_panel, text="Box Controls")
        box_frame.pack(fill="x", pady=5)
        
        ttk.Button(box_frame, text="Delete Last Box (Backspace)", command=self.delete_last_box).pack(fill="x", pady=2)
        ttk.Button(box_frame, text="Clear All Boxes (C)", command=self.clear_boxes).pack(fill="x", pady=2)
        
        # Navigation buttons
        nav_frame = ttk.Frame(right_panel)
        nav_frame.pack(fill="x", pady=5)
        
        ttk.Button(nav_frame, text="Previous", command=self.previous_image).pack(side="left", padx=2)
        ttk.Button(nav_frame, text="Next", command=self.next_image).pack(side="left", padx=2)
        ttk.Button(nav_frame, text="Save", command=self.save_label).pack(side="left", padx=2)
        
        # Status label
        self.status_var = tk.StringVar()
        ttk.Label(right_panel, textvariable=self.status_var).pack(fill="x", pady=5)
        
        # Bind mouse events
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        
        # Bind keyboard shortcuts
        self.root.bind("<BackSpace>", lambda e: self.delete_last_box())
        self.root.bind("c", lambda e: self.clear_boxes())
        
        # Load first image
        self.load_current_image()
        
    def filter_classes(self, *args):
        """Filter classes based on search text."""
        search_text = self.search_var.get().lower()
        self.class_listbox.delete(0, tk.END)
        for class_name in self.classes:
            if search_text in class_name.lower():
                self.class_listbox.insert(tk.END, class_name)
    
    def zoom(self, factor):
        """Zoom the image by the given factor."""
        self.zoom_level *= factor
        self.load_current_image()
    
    def on_mousewheel(self, event):
        """Handle mouse wheel zoom."""
        if event.delta > 0:
            self.zoom(1.1)
        else:
            self.zoom(0.9)
    
    def on_mouse_down(self, event):
        """Handle mouse button press."""
        if not self.class_listbox.curselection():
            self.status_var.set("Please select a class first!")
            return
            
        # Get canvas coordinates
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        
        # Create new box
        self.current_box = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=2
        )
    
    def on_mouse_move(self, event):
        """Handle mouse movement."""
        if self.current_box:
            # Update box coordinates
            cur_x = self.canvas.canvasx(event.x)
            cur_y = self.canvas.canvasy(event.y)
            self.canvas.coords(self.current_box, self.start_x, self.start_y, cur_x, cur_y)
    
    def on_mouse_up(self, event):
        """Handle mouse button release."""
        if self.current_box:
            # Get final coordinates
            end_x = self.canvas.canvasx(event.x)
            end_y = self.canvas.canvasy(event.y)
            
            # Calculate normalized coordinates
            img_width = self.original_image.width
            img_height = self.original_image.height
            
            x1 = min(self.start_x, end_x) / img_width
            y1 = min(self.start_y, end_y) / img_height
            x2 = max(self.start_x, end_x) / img_width
            y2 = max(self.start_y, end_y) / img_height
            
            # Calculate center and size
            x_center = (x1 + x2) / 2
            y_center = (y1 + y2) / 2
            width = x2 - x1
            height = y2 - y1
            
            # Get selected class
            class_idx = self.classes.index(self.class_listbox.get(self.class_listbox.curselection()))
            
            # Add to boxes list
            self.boxes.append((class_idx, x_center, y_center, width, height))
            
            # Update status
            self.status_var.set(f"Added box for {self.classes[class_idx]}")
            
            # Reset current box
            self.current_box = None
    
    def delete_last_box(self):
        """Delete the last drawn box."""
        if self.boxes:
            self.boxes.pop()
            self.load_current_image()  # Reload to redraw boxes
            self.status_var.set("Deleted last box")
    
    def clear_boxes(self):
        """Clear all boxes."""
        self.boxes = []
        self.load_current_image()  # Reload to redraw boxes
        self.status_var.set("Cleared all boxes")
    
    def load_current_image(self):
        """Load and display the current image."""
        if not self.images:
            self.status_var.set("No images found!")
            return
            
        image_path = os.path.join(self.images_dir, self.images[self.current_image_idx])
        self.original_image = Image.open(image_path)
        
        # Apply zoom
        width = int(self.original_image.width * self.zoom_level)
        height = int(self.original_image.height * self.zoom_level)
        image = self.original_image.resize((width, height), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(image)
        
        # Update canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=photo)
        self.canvas.image = photo
        
        # Update scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Draw existing boxes
        self.draw_boxes()
        
        # Update status
        self.status_var.set(
            f"Image {self.current_image_idx + 1}/{len(self.images)}: {self.images[self.current_image_idx]}"
        )
        
        # Load existing label if any
        self.load_existing_label()
        
        # Update class list
        self.filter_classes()
    
    def draw_boxes(self):
        """Draw all boxes on the canvas."""
        if not self.original_image:
            return
            
        img_width = self.original_image.width
        img_height = self.original_image.height
        
        for class_idx, x_center, y_center, width, height in self.boxes:
            # Convert normalized coordinates to canvas coordinates
            x1 = (x_center - width/2) * img_width * self.zoom_level
            y1 = (y_center - height/2) * img_height * self.zoom_level
            x2 = (x_center + width/2) * img_width * self.zoom_level
            y2 = (y_center + height/2) * img_height * self.zoom_level
            
            # Draw box
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline='red', width=2
            )
            
            # Draw label
            self.canvas.create_text(
                x1, y1-10,
                text=self.classes[class_idx],
                fill='red',
                anchor='sw'
            )
    
    def load_existing_label(self):
        """Load existing label for current image if available."""
        label_path = os.path.join(
            self.labels_dir,
            f"{os.path.splitext(self.images[self.current_image_idx])[0]}.txt"
        )
        
        if os.path.exists(label_path):
            try:
                with open(label_path, 'r') as f:
                    self.boxes = []
                    for line in f:
                        class_idx, x_center, y_center, width, height = map(float, line.strip().split())
                        self.boxes.append((int(class_idx), x_center, y_center, width, height))
                self.status_var.set("Loaded existing labels")
            except Exception as e:
                print(f"Error loading label: {str(e)}")
    
    def save_label(self):
        """Save the current label."""
        if not self.images:
            return
            
        if not self.boxes:
            self.status_var.set("No boxes to save!")
            return
        
        # Save to YOLO format
        label_path = os.path.join(
            self.labels_dir,
            f"{os.path.splitext(self.images[self.current_image_idx])[0]}.txt"
        )
        
        try:
            with open(label_path, 'w') as f:
                for class_idx, x_center, y_center, width, height in self.boxes:
                    f.write(f"{class_idx} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
            self.status_var.set("Labels saved successfully!")
        except Exception as e:
            self.status_var.set(f"Error saving labels: {str(e)}")
    
    def next_image(self):
        """Move to next image."""
        if self.current_image_idx < len(self.images) - 1:
            self.current_image_idx += 1
            self.boxes = []  # Clear boxes for new image
            self.load_current_image()
    
    def previous_image(self):
        """Move to previous image."""
        if self.current_image_idx > 0:
            self.current_image_idx -= 1
            self.boxes = []  # Clear boxes for new image
            self.load_current_image()
    
    def run(self):
        """Run the labeling tool."""
        self.root.mainloop()

def main():
    parser = argparse.ArgumentParser(description="UI Element Labeling Tool")
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Directory containing images and labels"
    )
    args = parser.parse_args()
    
    tool = LabelingTool(args.data_dir)
    tool.run()

if __name__ == "__main__":
    main() 