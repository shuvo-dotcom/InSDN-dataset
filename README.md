# SDN Anomaly Detection System

A comprehensive Software-Defined Network (SDN) monitoring and anomaly detection system that provides real-time network security monitoring, attack detection, and visualization capabilities.

## Features

### 1. Real-time Network Monitoring
- Live network traffic monitoring
- Active connection tracking
- Network topology visualization
- Resource usage monitoring (CPU, Memory)
- Protocol distribution analysis

### 2. Anomaly Detection
- Real-time attack detection
- Multiple attack type detection:
  - DDoS attacks
  - Port scanning
  - SYN flood attacks
  - Brute force attempts
- Anomaly score calculation
- Historical attack tracking

### 3. Interactive Dashboard
- Real-time metrics display
- Network topology visualization
- Attack warning system
- Historical data analysis
- Customizable detection thresholds

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd InSDN-dataset
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
InSDN-dataset/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Project dependencies
├── scripts/
│   ├── data_preprocess.py # Data preprocessing utilities
│   ├── train_gan.py      # GAN training implementation
│   └── network_monitor.py # Network monitoring and attack detection
├── models/
│   └── gan_model.pth     # Trained GAN model
├── data/
│   └── processed/        # Processed network data
└── logs/
    ├── app.log          # Application logs
    └── attack_simulator.log # Attack simulation logs
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Access the dashboard:
- Open your web browser and navigate to `http://localhost:8501`

### Dashboard Features

#### Live Monitoring Tab
- Real-time network metrics
- Active connections display
- Network topology visualization
- Attack warnings (when detected)
- Resource usage monitoring

#### Anomaly Detection Tab
- Anomaly score history
- Current anomaly status
- Attack history
- Detected anomaly types
- Customizable thresholds

#### Network Statistics Tab
- Network traffic trends
- Connection statistics
- Protocol distribution
- Historical data analysis

## Configuration

### Network Settings
- Monitoring interval (1-60 seconds)
- Anomaly detection threshold (0.0-1.0)
- Training epochs (10-200)

### Model Settings
- GAN training parameters
- Detection sensitivity
- Alert thresholds

## Attack Detection

The system detects various types of network attacks:

1. DDoS Attacks
   - High traffic volume detection
   - Multiple source IP analysis
   - Traffic pattern recognition

2. Port Scanning
   - Unusual port access patterns
   - Sequential port scanning detection
   - Multiple connection attempts

3. SYN Flood Attacks
   - Half-open connection monitoring
   - SYN packet analysis
   - Connection timeout tracking

4. Brute Force Attempts
   - Multiple failed login attempts
   - Password guessing patterns
   - Authentication failure monitoring

## Visualization Features

1. Network Topology
   - Interactive node-link diagram
   - Real-time connection updates
   - Node status indicators
   - Connection strength visualization

2. Metrics Display
   - Real-time charts
   - Historical trends
   - Statistical analysis
   - Customizable views

3. Attack Warnings
   - Flashing alert system
   - Attack type identification
   - Severity indicators
   - Historical tracking

## Logging and Monitoring

1. Application Logs
   - System events
   - Error tracking
   - Performance metrics
   - User actions

2. Attack Logs
   - Detected attacks
   - Attack patterns
   - Timestamps
   - Severity levels

## Dependencies

- streamlit==1.32.0
- pandas==2.2.0
- plotly==5.18.0
- networkx==3.2.1
- torch==2.2.0
- numpy==1.26.3
- scikit-learn==1.4.0
- matplotlib==3.8.2
- seaborn==0.13.2
- psutil==5.9.8
- python-dateutil==2.8.2
- pytz==2024.1
- tqdm==4.66.1
- requests==2.31.0
- pyyaml==6.0.1
- scipy==1.12.0

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Network security research community
- Open-source contributors
- SDN development teams

## Support

For support, please open an issue in the GitHub repository or contact the development team.

## Roadmap

- [ ] Enhanced attack detection algorithms
- [ ] Machine learning model improvements
- [ ] Additional visualization features
- [ ] Performance optimizations
- [ ] Mobile-responsive dashboard
- [ ] API integration capabilities
