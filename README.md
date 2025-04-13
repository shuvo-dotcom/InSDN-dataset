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
- Kaggle API credentials (for downloading the dataset)

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

4. Set up Kaggle API:
   - Create a Kaggle account if you don't have one
   - Go to your Kaggle account settings
   - Create a new API token
   - Place the kaggle.json file in ~/.kaggle/ directory

## Project Structure

```
InSDN-dataset/
├── app/                      # Web application components
├── api_integration/          # API integration modules
├── networkEnv/               # Network environment configuration
├── scripts/                  # Core processing scripts
│   ├── data_preprocess.py    # Data preprocessing utilities
│   ├── data_loader.py        # Data loading utilities
│   ├── train_gan.py          # GAN training implementation
│   ├── network_monitor.py    # Network monitoring and attack detection
│   ├── attack_simulator.py   # Attack simulation utilities
│   ├── anomaly_detector.py   # Anomaly detection implementation
│   ├── gan_model.py          # GAN model architecture
│   ├── validate_gan.py       # GAN validation utilities
│   ├── calculate_accuracy.py # Accuracy calculation utilities
│   ├── visualize_*.py        # Various visualization scripts
│   └── analyze_*.py          # Various analysis scripts
├── reports/                  # Generated reports and visualizations
├── logs/                     # Application and simulation logs
├── app.py                    # Main Streamlit application
├── mobile_app.py             # Mobile application implementation
├── main.py                   # Main entry point
├── requirements.txt          # Project dependencies
├── req.txt                   # Additional requirements
├── buildozer.spec            # Mobile app build configuration
└── pubspec.yaml              # Mobile app dependencies
```

## Usage

### Data Processing Pipeline

1. Download the dataset from Kaggle:
```bash
python scripts/data_loader.py --download
```
This will download the raw dataset files to `data/raw/`:
- `metasploitable.csv`
- `OVS.csv`
- `Normal_data.csv`

2. Preprocess the data:
```bash
python scripts/data_preprocess.py
```
This will generate processed data files in `data/processed/`:
- `train_data.csv`
- `test_data.csv`
- `validation_data.csv`
- `synthetic_data.csv`

3. Train the GAN model:
```bash
python scripts/train_gan.py
```

4. Validate the GAN model:
```bash
python scripts/validate_gan.py
```

5. Run anomaly detection:
```bash
python scripts/anomaly_detector.py
```

6. Generate visualizations:
```bash
python scripts/visualize_training.py
python scripts/visualize_accuracy.py
python scripts/visualize_accuracy_map.py
```

7. Analyze results:
```bash
python scripts/analyze_recent_results.py
python scripts/analyze_accuracy_ranges.py
```

### Running the Web Application

1. Start the application:
```bash
streamlit run app.py
```

2. Access the dashboard:
- Open your web browser and navigate to `http://localhost:8501`

### Running the Mobile Application

1. Build the mobile app:
```bash
buildozer android debug
```

2. Install and run the APK on your Android device

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
- kaggle==1.5.16

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
