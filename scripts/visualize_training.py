import matplotlib.pyplot as plt
import numpy as np
import re
import seaborn as sns
import os

def extract_losses_from_log(log_file):
    """Extract loss values from training log file."""
    d_losses = []
    g_losses = []
    epochs = []
    
    with open(log_file, 'r') as f:
        for line in f:
            if "completed. Avg Loss D:" in line:
                # Extract epoch number and losses
                match = re.search(r"Epoch \[(\d+)/\d+\] completed\. Avg Loss D: ([-\d\.]+), Avg Loss G: ([-\d\.]+)", line)
                if match:
                    epoch, d_loss, g_loss = match.groups()
                    epochs.append(int(epoch))
                    d_losses.append(float(d_loss))
                    g_losses.append(float(g_loss))
    
    return epochs, d_losses, g_losses

def plot_training_progress(epochs, d_losses, g_losses, save_dir):
    """Create and save detailed training progress visualizations."""
    # Set style
    plt.style.use('default')
    sns.set_theme()
    
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(20, 15))
    
    # 1. Loss Curves
    ax1 = plt.subplot(2, 2, 1)
    ax1.plot(epochs, d_losses, label='Discriminator Loss', linewidth=2)
    ax1.plot(epochs, g_losses, label='Generator Loss', linewidth=2)
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title('Training Losses Over Time')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Loss Ratio
    ax2 = plt.subplot(2, 2, 2)
    loss_ratio = [g/d if d != 0 else 1.0 for g, d in zip(g_losses, d_losses)]
    ax2.plot(epochs, loss_ratio, label='G/D Loss Ratio', color='green', linewidth=2)
    ax2.axhline(y=1.0, color='r', linestyle='--', alpha=0.3)
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('G/D Loss Ratio')
    ax2.set_title('Generator/Discriminator Loss Ratio')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Loss Distribution
    ax3 = plt.subplot(2, 2, 3)
    sns.kdeplot(data=d_losses, label='Discriminator Loss', ax=ax3)
    sns.kdeplot(data=g_losses, label='Generator Loss', ax=ax3)
    ax3.set_xlabel('Loss Value')
    ax3.set_ylabel('Density')
    ax3.set_title('Loss Distribution')
    ax3.legend()
    
    # 4. Loss Correlation
    ax4 = plt.subplot(2, 2, 4)
    ax4.scatter(d_losses, g_losses, alpha=0.5)
    ax4.set_xlabel('Discriminator Loss')
    ax4.set_ylabel('Generator Loss')
    ax4.set_title('Loss Correlation')
    
    # Add correlation coefficient
    corr = np.corrcoef(d_losses, g_losses)[0, 1]
    ax4.text(0.05, 0.95, f'Correlation: {corr:.2f}', 
             transform=ax4.transAxes, 
             bbox=dict(facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    # Save plots
    os.makedirs(save_dir, exist_ok=True)
    plt.savefig(os.path.join(save_dir, 'training_analysis.png'))
    plt.close()
    
    # Create additional plots
    
    # 1. Moving averages
    plt.figure(figsize=(12, 6))
    window = 5  # Window size for moving average
    d_losses_ma = np.convolve(d_losses, np.ones(window)/window, mode='valid')
    g_losses_ma = np.convolve(g_losses, np.ones(window)/window, mode='valid')
    epochs_ma = epochs[window-1:]
    
    plt.plot(epochs_ma, d_losses_ma, label='Discriminator Loss (MA)', linewidth=2)
    plt.plot(epochs_ma, g_losses_ma, label='Generator Loss (MA)', linewidth=2)
    plt.xlabel('Epoch')
    plt.ylabel('Loss (Moving Average)')
    plt.title(f'Training Losses - {window}-Epoch Moving Average')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(save_dir, 'training_ma.png'))
    plt.close()
    
    # 2. Loss changes between epochs
    plt.figure(figsize=(12, 6))
    d_loss_changes = np.diff(d_losses)
    g_loss_changes = np.diff(g_losses)
    
    plt.plot(epochs[1:], d_loss_changes, label='Discriminator Loss Change', linewidth=2)
    plt.plot(epochs[1:], g_loss_changes, label='Generator Loss Change', linewidth=2)
    plt.xlabel('Epoch')
    plt.ylabel('Loss Change')
    plt.title('Loss Changes Between Epochs')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(save_dir, 'loss_changes.png'))
    plt.close()

def main():
    # Set paths
    log_file = 'logs/training.log'
    save_dir = 'reports/training_visualization'
    
    # Extract losses from log
    epochs, d_losses, g_losses = extract_losses_from_log(log_file)
    
    # Create visualizations
    plot_training_progress(epochs, d_losses, g_losses, save_dir)
    
    print(f"Training visualizations have been saved to {save_dir}")
    print(f"Number of epochs processed: {len(epochs)}")
    print(f"Final Discriminator Loss: {d_losses[-1]:.4f}")
    print(f"Final Generator Loss: {g_losses[-1]:.4f}")

if __name__ == "__main__":
    main() 