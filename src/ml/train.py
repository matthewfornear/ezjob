"""
Training script for Project1999 bot ML models.
"""

import argparse
import os
import sys
import torch
from torch.utils.data import DataLoader, TensorDataset
from torch.optim import Adam
from torch.nn import CrossEntropyLoss
from datetime import datetime
from ..utils.logger import logger
from .models.form_detector import FormElementDetector
from .data.form_data_collector import FormDataCollector

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.ml.training.trainer import ModelTrainer
from src.ml.data.data_collector import DataCollector
from src.ml.models.vision_model import GameElementDetector

def parse_args():
    parser = argparse.ArgumentParser(description='Train ML models for Project1999 bot')
    parser.add_argument('--num-samples', type=int, default=100,
                      help='Number of samples to collect for training')
    parser.add_argument('--num-epochs', type=int, default=10,
                      help='Number of epochs to train for')
    parser.add_argument('--batch-size', type=int, default=32,
                      help='Batch size for training')
    parser.add_argument('--learning-rate', type=float, default=0.001,
                      help='Learning rate for training')
    parser.add_argument('--data-dir', type=str, default='data',
                      help='Directory to store training data')
    parser.add_argument('--model-dir', type=str, default='models',
                      help='Directory to store trained models')
    parser.add_argument('--debug', action='store_true',
                      help='Enable debug logging')
    return parser.parse_args()

def train_model(data_dir, model_dir, num_epochs=10, batch_size=32, learning_rate=0.001):
    """
    Train the form element detector model.
    
    Args:
        data_dir: Directory containing training data
        model_dir: Directory to save trained model
        num_epochs: Number of training epochs
        batch_size: Batch size for training
        learning_rate: Learning rate for optimizer
    """
    try:
        # Create model directory
        os.makedirs(model_dir, exist_ok=True)
        
        # Initialize model
        model = FormElementDetector()
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = model.to(device)
        
        # Initialize data collector and create dataset
        collector = FormDataCollector(data_dir=data_dir)
        X_train, y_train = collector.create_dataset()
        
        if X_train is None or y_train is None:
            raise ValueError("Failed to create dataset")
        
        # Convert to PyTorch tensors
        X_train = torch.FloatTensor(X_train).to(device)
        y_train = torch.LongTensor(y_train).to(device)
        
        # Create data loader
        train_dataset = TensorDataset(X_train, y_train)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        
        # Initialize optimizer and loss function
        optimizer = Adam(model.parameters(), lr=learning_rate)
        criterion = CrossEntropyLoss()
        
        # Training loop
        logger.info("Starting training...")
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
            logger.info(f"Epoch {epoch+1}/{num_epochs}, Average Loss: {avg_loss:.4f}")
        
        # Save trained model
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = os.path.join(model_dir, f"form_detector_{timestamp}.pt")
        model.save_model(model_path)
        
        logger.info(f"Training completed. Model saved to {model_path}")
        return model
        
    except Exception as e:
        logger.error(f"Error during training: {str(e)}")
        raise

def main():
    args = parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level)
    logger = logging.getLogger(__name__)
    
    try:
        # Create necessary directories
        os.makedirs(args.data_dir, exist_ok=True)
        os.makedirs(args.model_dir, exist_ok=True)
        
        # Initialize data collector
        data_collector = DataCollector(args.data_dir)
        
        # Collect training data
        logger.info(f"Collecting {args.num_samples} training samples...")
        data_collector.collect_training_data(args.num_samples)
        
        # Initialize model trainer
        trainer = ModelTrainer(args.model_dir)
        
        # Train vision model
        logger.info("Training vision model...")
        trainer.train_vision_model(
            num_epochs=args.num_epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate
        )
        
        logger.info("Training completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during training: {str(e)}")
        raise

if __name__ == '__main__':
    main() 