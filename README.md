# SDN Anomaly Detection Dashboard

A real-time network monitoring and anomaly detection system for Software-Defined Networks (SDN).

## Features

- Real-time network monitoring
- Anomaly detection using GAN-based models
- Network topology visualization
- Vulnerability detection
- Protocol analysis
- Performance metrics tracking

## Setup

1. Clone the repository:
```bash
git clone <your-repository-url>
cd InSDN-dataset
```

2. Create and activate a virtual environment:
```bash
python -m venv networkEnv
source networkEnv/bin/activate  # On Windows: networkEnv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
streamlit run app.py
```

## Project Structure

```
InSDN-dataset/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Project dependencies
├── scripts/
│   ├── data_preprocess.py # Data preprocessing utilities
│   ├── network_monitor.py # Network monitoring functionality
│   └── train_gan.py      # GAN model training
└── logs/                 # Application logs
```

## Usage

1. Access the dashboard at http://localhost:8501
2. Use the sidebar to configure monitoring settings
3. View real-time network metrics and topology
4. Monitor for potential vulnerabilities
5. Analyze network traffic patterns

## Security Features

- Real-time connection monitoring
- Vulnerability detection for common ports
- Anomaly scoring based on multiple metrics
- Protocol analysis and traffic pattern detection

## Requirements

- Python 3.8+
- Network access for monitoring
- Sufficient system resources for real-time monitoring

## License

MIT License
