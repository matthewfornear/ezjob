"""
Model training module for Project1999 bot.
"""

import os
import torch
import numpy as np
from torch.utils.data import DataLoader, TensorDataset
from torch.optim import Adam
from torch.nn import CrossEntropyLoss
from datetime import datetime
from ...utils.logger import logger
from ..models.vision_model import GameElementDetector
from ..data.data_collector import DataCollector

class ModelTrainer:
    def __init__(self, model_dir="models"):
        """
        Initialize the model trainer.
        
        Args:
            model_dir: Directory to store trained models
        """
        self.model_dir = model_dir
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.logger = logger
        self._setup_directories()
    
    def _setup_directories(self):
        """Create necessary directories for model storage."""
        try:
            os.makedirs(self.model_dir, exist_ok=True)
            self.logger.info(f"Created model directory at {self.model_dir}")
        except Exception as e:
            self.logger.error(f"Failed to create model directory: {str(e)}")
            raise
    
    def train_vision_model(self, num_epochs=10, batch_size=32, learning_rate=0.001):
        """
        Train the vision model for game element detection.
        
        Args:
            num_epochs: Number of training epochs
            batch_size: Batch size for training
            learning_rate: Learning rate for optimizer
            
        Returns:
            GameElementDetector: Trained model
        """
        try:
            # Initialize model with 27 classes (10 base classes + 16 spell status classes + 1 corpse class)
            model = GameElementDetector(num_classes=27)
            model = model.to(self.device)
            
            # Initialize data collector
            data_collector = DataCollector(os.path.join(os.path.dirname(self.model_dir), 'data'))
            
            # Collect and preprocess data
            X_train, y_train = data_collector.create_dataset()
            if X_train is None or y_train is None:
                raise ValueError("Failed to create dataset")
            
            # Convert to PyTorch tensors
            X_train = torch.FloatTensor(X_train).to(self.device)
            y_train = torch.LongTensor(y_train).to(self.device)
            
            # Create data loader
            train_dataset = TensorDataset(X_train, y_train)
            train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
            
            # Initialize optimizer and loss function
            optimizer = Adam(model.parameters(), lr=learning_rate)
            criterion = CrossEntropyLoss()
            
            # Training loop
            for epoch in range(num_epochs):
                model.train()
                total_loss = 0
                
                for batch_X, batch_y in train_loader:
                    # Forward pass
                    optimizer.zero_grad()
                    outputs = model(batch_X)
                    loss = criterion(outputs, batch_y)
                    
                    # Backward pass and optimize
                    loss.backward()
                    optimizer.step()
                    
                    total_loss += loss.item()
                
                # Log epoch statistics
                avg_loss = total_loss / len(train_loader)
                self.logger.info(f"Epoch {epoch+1}/{num_epochs}, Average Loss: {avg_loss:.4f}")
            
            # Save trained model
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_path = os.path.join(self.model_dir, f"vision_model_{timestamp}.pt")
            model.save_model(model_path)
            
            self.logger.info(f"Training completed. Model saved to {model_path}")
            return model
        except Exception as e:
            self.logger.error(f"Error during vision model training: {str(e)}")
            raise
    
    def evaluate_model(self, model, test_data):
        """
        Evaluate a trained model on test data.
        
        Args:
            model: Trained model to evaluate
            test_data: Tuple of (X_test, y_test)
            
        Returns:
            dict: Dictionary containing evaluation metrics
        """
        try:
            X_test, y_test = test_data
            
            # Convert to PyTorch tensors
            X_test = torch.FloatTensor(X_test).to(self.device)
            y_test = torch.LongTensor(y_test).to(self.device)
            
            # Set model to evaluation mode
            model.eval()
            
            # Get predictions
            with torch.no_grad():
                outputs = model(X_test)
                _, predicted = torch.max(outputs.data, 1)
            
            # Calculate accuracy
            correct = (predicted == y_test).sum().item()
            total = y_test.size(0)
            accuracy = correct / total
            
            # Calculate confusion matrix
            confusion_matrix = torch.zeros(model.num_classes, model.num_classes)
            for t, p in zip(y_test, predicted):
                confusion_matrix[t.long(), p.long()] += 1
            
            metrics = {
                'accuracy': accuracy,
                'confusion_matrix': confusion_matrix.cpu().numpy(),
                'total_samples': total,
                'correct_predictions': correct
            }
            
            self.logger.info(f"Model evaluation completed. Accuracy: {accuracy:.4f}")
            return metrics
        except Exception as e:
            self.logger.error(f"Error during model evaluation: {str(e)}")
            raise
    
    def load_model(self, model_path):
        """
        Load a trained model from disk.
        
        Args:
            model_path: Path to the saved model
            
        Returns:
            GameElementDetector: Loaded model
        """
        try:
            model = GameElementDetector()
            model.load_model(model_path)
            model = model.to(self.device)
            self.logger.info(f"Model loaded from {model_path}")
            return model
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            raise 