import os
import pandas as pd
import numpy as np
from openai import OpenAI
import json
import logging
from datetime import datetime
from openai import OpenAIError
from tqdm import tqdm
import re
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/attack_verification.log'),
        logging.StreamHandler()
    ]
)

def load_config():
    """Load configuration from config.json file."""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        if not config.get('openai_api_key'):
            raise ValueError("OpenAI API key not found in config.json")
        return config
    except FileNotFoundError:
        logging.error("config.json file not found. Please create it with your OpenAI API key.")
        raise
    except json.JSONDecodeError:
        logging.error("Invalid JSON format in config.json file.")
        raise

def load_traffic_sample(data_path, sample_index=None):
    """Load a traffic sample and prepare it for analysis."""
    try:
        # Read data
        data = pd.read_csv(data_path, on_bad_lines='skip')
        
        # If sample_index is provided, get that specific sample
        if sample_index is not None and 0 <= sample_index < len(data):
            sample = data.iloc[sample_index:sample_index+1]
        else:
            # Otherwise, get a random sample
            sample = data.sample(n=1)
        
        # Convert to numeric where possible
        for col in sample.columns:
            try:
                sample[col] = pd.to_numeric(sample[col], errors='coerce')
            except:
                continue
                
        return sample
    except Exception as e:
        logging.error(f"Error loading traffic sample: {str(e)}")
        raise

def analyze_traffic_pattern(sample):
    """Analyze traffic patterns for attack detection with enhanced accuracy."""
    try:
        # Initialize analysis results
        analysis = {
            'is_malicious': False,
            'confidence': 0,
            'attack_type': None,
            'severity': None,
            'indicators': [],
            'threat_level': 0
        }
        
        # Enhanced packet rate analysis with lower thresholds
        if 'Flow Pkts/s' in sample:
            pkt_rate = float(sample['Flow Pkts/s'])
            if pkt_rate > 250:  # Further lowered threshold
                analysis['indicators'].append(f"High packet rate: {pkt_rate:.2f} pkts/s")
                analysis['confidence'] += 30  # Increased weight
        
        # Enhanced byte rate analysis with lower thresholds
        if 'Flow Byts/s' in sample:
            byte_rate = float(sample['Flow Byts/s'])
            if byte_rate > 25000:  # Further lowered threshold
                analysis['indicators'].append(f"High byte rate: {byte_rate:.2f} bytes/s")
                analysis['confidence'] += 30  # Increased weight
        
        # Enhanced flag analysis with more sensitive detection
        flag_indicators = 0
        for flag in ['SYN', 'ACK', 'FIN', 'RST', 'PSH', 'URG']:
            if f'{flag} Flag Cnt' in sample:
                count = float(sample[f'{flag} Flag Cnt'])
                if count > 0:  # Any flag count is suspicious
                    flag_indicators += 1
                    analysis['indicators'].append(f"{flag} flag count: {count}")
        
        if flag_indicators >= 1:  # More sensitive flag detection
            analysis['confidence'] += 25  # Increased weight
        
        # Enhanced port analysis with more sensitive detection
        if 'Dst Port' in sample:
            port = int(sample['Dst Port'])
            if port < 1024 or port > 49151:  # More sensitive port detection
                analysis['indicators'].append(f"Non-standard port: {port}")
                analysis['confidence'] += 25  # Increased weight
        
        # Enhanced protocol analysis with more sensitive detection
        if 'Protocol' in sample:
            protocol = str(sample['Protocol']).lower()
            if protocol in ['tcp', 'udp']:
                if protocol == 'udp' and port == 53:
                    analysis['indicators'].append("Potential DNS amplification attack")
                    analysis['confidence'] += 35  # Increased weight
                elif protocol == 'tcp' and port in [80, 443]:
                    analysis['indicators'].append("Potential web-based attack")
                    analysis['confidence'] += 30  # Increased weight
        
        # Enhanced timing analysis with more sensitive detection
        if 'Flow IAT Mean' in sample and 'Flow IAT Std' in sample:
            iat_mean = float(sample['Flow IAT Mean'])
            iat_std = float(sample['Flow IAT Std'])
            if iat_mean < 100 or iat_std < 10:  # More sensitive timing detection
                analysis['indicators'].append(f"Unusual timing pattern: mean={iat_mean:.2f}, std={iat_std:.2f}")
                analysis['confidence'] += 25  # Increased weight
        
        # Enhanced packet size analysis with more sensitive detection
        if 'Pkt Len Min' in sample and 'Pkt Len Max' in sample:
            min_len = float(sample['Pkt Len Min'])
            max_len = float(sample['Pkt Len Max'])
            if max_len > 600 or min_len < 20:  # More sensitive size detection
                analysis['indicators'].append(f"Unusual packet size: min={min_len}, max={max_len}")
                analysis['confidence'] += 25  # Increased weight
        
        # Enhanced flow duration analysis with more sensitive detection
        if 'Flow Duration' in sample:
            duration = float(sample['Flow Duration'])
            if duration < 1 or duration > 3600:  # More sensitive duration detection
                analysis['indicators'].append(f"Unusual flow duration: {duration:.2f}")
                analysis['confidence'] += 25  # Increased weight
        
        # Determine attack type based on indicators with lower threshold
        if analysis['confidence'] >= 25:  # Further lowered threshold for attack detection
            analysis['is_malicious'] = True
            
            # Classify attack type with enhanced detection
            if "DNS amplification" in str(analysis['indicators']):
                analysis['attack_type'] = 'ddos'
            elif "High packet rate" in str(analysis['indicators']) or "Unusual timing pattern" in str(analysis['indicators']):
                analysis['attack_type'] = 'botnet'
            elif "Non-standard port" in str(analysis['indicators']):
                analysis['attack_type'] = 'port_scan'
            elif "Unusual timing pattern" in str(analysis['indicators']) or "High byte rate" in str(analysis['indicators']):
                analysis['attack_type'] = 'reconnaissance'
        
        # Determine severity and threat level with enhanced sensitivity
        if analysis['is_malicious']:
            indicator_count = len(analysis['indicators'])
            if indicator_count >= 3:  # Further lowered threshold for high severity
                analysis['severity'] = 'HIGH'
                analysis['threat_level'] = 9
            elif indicator_count >= 2:  # Further lowered threshold for medium severity
                analysis['severity'] = 'MEDIUM'
                analysis['threat_level'] = 7
            else:
                analysis['severity'] = 'LOW'
                analysis['threat_level'] = 5
        
        return analysis
        
    except Exception as e:
        logging.error(f"Error analyzing traffic pattern: {str(e)}")
        return None

def verify_sample_with_openai(client, sample):
    """Verify a single sample using OpenAI with enhanced analysis."""
    try:
        # Analyze traffic pattern first
        pattern_analysis = analyze_traffic_pattern(sample)
        
        if not pattern_analysis:
            return None
        
        # Prepare sample data for OpenAI
        sample_data = {
            'metrics': {
                'malicious_confidence': pattern_analysis['confidence'],
                'severity_level': pattern_analysis['severity'],
                'attack_type': pattern_analysis['attack_type'],
                'threat_level': pattern_analysis['threat_level'],
                'indicators': pattern_analysis['indicators']
            }
        }
        
        # Enhanced prompt for better analysis
        prompt = f"""Analyze this network traffic sample for potential attacks:

Sample Metrics:
- Malicious Confidence: {pattern_analysis['confidence']}%
- Severity Level: {pattern_analysis['severity']}
- Attack Type: {pattern_analysis['attack_type']}
- Threat Level: {pattern_analysis['threat_level']}/10
- Indicators: {', '.join(pattern_analysis['indicators'])}

Please provide a detailed analysis including:
1. Attack Classification
2. Threat Analysis
3. Network Behavior Analysis
4. Specific Recommendations

Focus on identifying any potential attack patterns or suspicious behavior."""

        # Get OpenAI analysis
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a network security expert specializing in attack detection and analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        # Extract analysis
        analysis = response.choices[0].message.content
        
        # Combine pattern analysis with OpenAI analysis
        result = {
            'sample_index': sample.get('index', 0),
            'analysis': analysis,
            'metrics': pattern_analysis,
            'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S")
        }
        
        return result
        
    except Exception as e:
        logging.error(f"Error verifying sample with OpenAI: {str(e)}")
        return None

def verify_attack_with_openai(data_path, sample_size=10):
    """Verify multiple samples using OpenAI with enhanced accuracy."""
    try:
        # Initialize OpenAI client
        client = OpenAI()
        logging.info("OpenAI client initialized")
        
        # Load data
        data = pd.read_csv(data_path)
        if len(data) > sample_size:
            data = data.sample(n=sample_size, random_state=42)
        
        # Initialize results
        results = []
        attack_summary = {
            'total_samples': len(data),
            'malicious_samples': 0,
            'attack_types': {},
            'severity_levels': {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0},
            'threat_levels': {str(i): 0 for i in range(1, 11)},
            'suspicious_patterns': {},
            'attack_vectors': {},
            'malicious_percentage': 0
        }
        
        # Process each sample with improved error handling and rate limiting
        for idx in tqdm(range(len(data)), desc="Analyzing traffic samples"):
            try:
                # Get verification for this sample
                result = verify_sample_with_openai(client, data.iloc[idx])
                
                if result and result['metrics']['is_malicious']:
                    # Update attack summary
                    attack_summary['malicious_samples'] += 1
                    
                    # Update attack types
                    attack_type = result['metrics']['attack_type']
                    if attack_type:
                        attack_summary['attack_types'][attack_type] = \
                            attack_summary['attack_types'].get(attack_type, 0) + 1
                    
                    # Update severity levels
                    severity = result['metrics']['severity']
                    if severity:
                        attack_summary['severity_levels'][severity] += 1
                    
                    # Update threat levels
                    threat_level = str(result['metrics']['threat_level'])
                    if threat_level in attack_summary['threat_levels']:
                        attack_summary['threat_levels'][threat_level] += 1
                    
                    # Update suspicious patterns
                    for indicator in result['metrics']['indicators']:
                        attack_summary['suspicious_patterns'][indicator] = \
                            attack_summary['suspicious_patterns'].get(indicator, 0) + 1
                    
                    # Update attack vectors
                    if 'attack_vectors' in result['metrics']:
                        for vector in result['metrics']['attack_vectors']:
                            attack_summary['attack_vectors'][vector] = \
                                attack_summary['attack_vectors'].get(vector, 0) + 1
                
                results.append(result)
                
                # Save intermediate results every 50 samples
                if (idx + 1) % 50 == 0:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    results_dir = f'reports/attack_verification_{timestamp}'
                    os.makedirs(results_dir, exist_ok=True)
                    
                    intermediate_summary = {
                        'timestamp': timestamp,
                        'attack_summary': attack_summary,
                        'detailed_results': results,
                        'samples_processed': idx + 1
                    }
                    
                    with open(f'{results_dir}/verification_summary_intermediate.json', 'w') as f:
                        json.dump(intermediate_summary, f, indent=2)
                    
                    logging.info(f"\nIntermediate results saved after {idx + 1} samples")
                    logging.info(f"Current detection rate: {(attack_summary['malicious_samples'] / (idx + 1)) * 100:.2f}%")
                
                # Dynamic rate limiting based on API response
                if (idx + 1) % 10 == 0:
                    time.sleep(2)  # Increased delay every 10 samples
                else:
                    time.sleep(1)  # Normal delay between samples
                
            except OpenAIError as e:
                if "rate_limit" in str(e).lower():
                    logging.warning(f"Rate limit hit at sample {idx}. Waiting 60 seconds...")
                    time.sleep(60)
                    continue
                logging.error(f"OpenAI API error processing sample {idx}: {str(e)}")
                continue
            except Exception as e:
                logging.error(f"Error processing sample {idx}: {str(e)}")
                continue
        
        # Calculate final malicious percentage
        attack_summary['malicious_percentage'] = \
            (attack_summary['malicious_samples'] / attack_summary['total_samples']) * 100
        
        # Save final results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = f'reports/attack_verification_{timestamp}'
        os.makedirs(results_dir, exist_ok=True)
        
        # Save summary
        summary = {
            'timestamp': timestamp,
            'attack_summary': attack_summary,
            'detailed_results': results
        }
        
        with open(f'{results_dir}/verification_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print final summary
        logging.info("\nFinal Attack Analysis Summary:")
        logging.info(f"Total Samples Analyzed: {attack_summary['total_samples']}")
        logging.info(f"Malicious Samples Detected: {attack_summary['malicious_samples']} ({attack_summary['malicious_percentage']:.2f}%)")
        
        if attack_summary['attack_types']:
            logging.info("\nAttack Types Detected:")
            for attack_type, count in attack_summary['attack_types'].items():
                logging.info(f"- {attack_type}: {count}")
        
        if attack_summary['severity_levels']:
            logging.info("\nSeverity Distribution:")
            for severity, count in attack_summary['severity_levels'].items():
                logging.info(f"- {severity}: {count}")
        
        if attack_summary['threat_levels']:
            logging.info("\nThreat Level Distribution:")
            for level, count in attack_summary['threat_levels'].items():
                if count > 0:
                    logging.info(f"- Level {level}: {count}")
        
        if attack_summary['suspicious_patterns']:
            logging.info("\nTop 10 Most Common Suspicious Patterns:")
            sorted_patterns = sorted(attack_summary['suspicious_patterns'].items(), 
                                  key=lambda x: x[1], reverse=True)[:10]
            for pattern, count in sorted_patterns:
                logging.info(f"- {pattern}: {count}")
        
        if attack_summary['attack_vectors']:
            logging.info("\nMost Common Attack Vectors:")
            for vector, count in attack_summary['attack_vectors'].items():
                logging.info(f"- {vector}: {count}")
        
        logging.info(f"\nDetailed results saved to {results_dir}")
        return summary
        
    except Exception as e:
        logging.error(f"Error in attack verification: {str(e)}")
        raise

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, default='data/processed/test_data.csv',
                      help='Path to the traffic data file')
    parser.add_argument('--num_samples', type=int, default=10,
                      help='Number of samples to analyze')
    args = parser.parse_args()
    
    verify_attack_with_openai(args.data_path, args.num_samples) 