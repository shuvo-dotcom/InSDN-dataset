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

def prepare_attack_verification_prompt(traffic_sample):
    """Prepare a prompt for attack verification with enhanced feature analysis."""
    try:
        # Convert sample to dictionary
        sample_dict = traffic_sample.iloc[0].to_dict()
        
        # Extract key network features with enhanced analysis
        network_features = {
            'Flow Characteristics': {
                'Duration': sample_dict.get('Flow Duration', 'N/A'),
                'Bytes/s': sample_dict.get('Flow Byts/s', 'N/A'),
                'Packets/s': sample_dict.get('Flow Pkts/s', 'N/A'),
                'Forward/Backward Ratio': sample_dict.get('Down/Up Ratio', 'N/A'),
                'Flow Rate': sample_dict.get('Flow Rate', 'N/A'),
                'Flow PPS': sample_dict.get('Flow PPS', 'N/A')
            },
            'Packet Analysis': {
                'Total Forward Packets': sample_dict.get('Tot Fwd Pkts', 'N/A'),
                'Total Backward Packets': sample_dict.get('Tot Bwd Pkts', 'N/A'),
                'Packet Length Stats': {
                    'Min': sample_dict.get('Pkt Len Min', 'N/A'),
                    'Max': sample_dict.get('Pkt Len Max', 'N/A'),
                    'Mean': sample_dict.get('Pkt Len Mean', 'N/A'),
                    'Std Dev': sample_dict.get('Pkt Len Std', 'N/A')
                },
                'Window Size': {
                    'Forward': sample_dict.get('Fwd Win Byts', 'N/A'),
                    'Backward': sample_dict.get('Bwd Win Byts', 'N/A')
                }
            },
            'Timing Patterns': {
                'Flow IAT Mean': sample_dict.get('Flow IAT Mean', 'N/A'),
                'Flow IAT Std': sample_dict.get('Flow IAT Std', 'N/A'),
                'Forward IAT Mean': sample_dict.get('Fwd IAT Mean', 'N/A'),
                'Backward IAT Mean': sample_dict.get('Bwd IAT Mean', 'N/A'),
                'Active Mean': sample_dict.get('Active Mean', 'N/A'),
                'Idle Mean': sample_dict.get('Idle Mean', 'N/A')
            },
            'Flag Analysis': {
                'PSH Flags': sample_dict.get('PSH Flag Cnt', 'N/A'),
                'URG Flags': sample_dict.get('URG Flag Cnt', 'N/A'),
                'SYN Flags': sample_dict.get('SYN Flag Cnt', 'N/A'),
                'RST Flags': sample_dict.get('RST Flag Cnt', 'N/A'),
                'FIN Flags': sample_dict.get('FIN Flag Cnt', 'N/A'),
                'ACK Flags': sample_dict.get('ACK Flag Cnt', 'N/A')
            },
            'Protocol Behavior': {
                'Protocol': sample_dict.get('Protocol', 'N/A'),
                'Source Port': sample_dict.get('Src Port', 'N/A'),
                'Destination Port': sample_dict.get('Dst Port', 'N/A'),
                'Service': sample_dict.get('Service', 'N/A')
            }
        }
        
        # Calculate additional metrics
        try:
            # Calculate packet size ratio
            if sample_dict.get('Pkt Len Max') and sample_dict.get('Pkt Len Min'):
                pkt_size_ratio = float(sample_dict['Pkt Len Max']) / float(sample_dict['Pkt Len Min'])
                network_features['Packet Analysis']['Packet Size Ratio'] = pkt_size_ratio
        except:
            network_features['Packet Analysis']['Packet Size Ratio'] = 'N/A'
        
        try:
            # Calculate flag ratio
            if sample_dict.get('PSH Flag Cnt') and sample_dict.get('Tot Fwd Pkts'):
                flag_ratio = float(sample_dict['PSH Flag Cnt']) / float(sample_dict['Tot Fwd Pkts'])
                network_features['Flag Analysis']['PSH Flag Ratio'] = flag_ratio
        except:
            network_features['Flag Analysis']['PSH Flag Ratio'] = 'N/A'
        
        prompt = f"""As a cybersecurity expert, analyze this network traffic sample for potential attacks or malicious behavior.

Detailed Network Features:
{json.dumps(network_features, indent=2)}

Full Traffic Sample Details:
{json.dumps(sample_dict, indent=2)}

Please provide a detailed security analysis including:

1. Attack Classification
- Is this traffic sample likely to be malicious? (0-100% confidence)
- What type of attack or normal traffic does this pattern suggest?
- What are the key indicators supporting this classification?
- Provide specific numerical evidence for your assessment
- Compare the metrics against known attack patterns

2. Threat Analysis
- What are the potential security implications?
- What is the estimated severity level (Low/Medium/High)?
- What are the possible attack vectors being used?
- Rate the threat level (1-10) with justification
- Consider both immediate and potential future impacts

3. Network Behavior Analysis
- Are there any suspicious patterns in:
  * Packet flow characteristics (unusual rates, ratios, or patterns)
  * Timing patterns (irregular intervals, bursts, or gaps)
  * Flag usage (unusual combinations or frequencies)
  * Protocol behavior (non-standard ports, services, or protocols)
- How does this compare to normal traffic patterns?
- Provide specific metrics that deviate from normal
- Consider both absolute values and relative ratios

4. Recommendations
- What security measures would be effective against this type of traffic?
- What monitoring or detection rules would you recommend?
- What immediate actions should be taken if this pattern is detected?
- Suggest specific firewall rules or IDS signatures
- Include both preventive and detective controls

Please provide specific evidence and numerical metrics where possible. Focus on concrete indicators rather than general observations. Pay special attention to:
- Unusual packet size distributions
- Abnormal flag patterns
- Non-standard port usage
- Irregular timing patterns
- Suspicious protocol behavior"""
        
        return prompt
    except Exception as e:
        logging.error(f"Error preparing attack verification prompt: {str(e)}")
        raise

def verify_attack_with_openai(client, traffic_sample):
    """Verify a traffic sample for attacks using OpenAI."""
    try:
        # Prepare prompt
        prompt = prepare_attack_verification_prompt(traffic_sample)
        
        # Get OpenAI analysis
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an expert in cybersecurity and network traffic analysis. Focus on identifying potential attacks and security threats."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    except OpenAIError as e:
        logging.error(f"OpenAI API error: {str(e)}")
        raise

def extract_attack_metrics(analysis_text):
    """Extract attack-related metrics with enhanced analysis."""
    try:
        metrics = {
            'malicious_confidence': None,
            'severity_level': None,
            'attack_type': None,
            'threat_level': None,
            'key_indicators': [],
            'recommendations': [],
            'attack_vectors': [],
            'suspicious_patterns': []
        }
        
        # Extract confidence score with more precise pattern
        confidence_pattern = r"(\d+)%\s*confidence"
        confidence_match = re.search(confidence_pattern, analysis_text.lower())
        if confidence_match:
            metrics['malicious_confidence'] = int(confidence_match.group(1))
        
        # Extract severity level with more context
        severity_pattern = r"severity\s*level[:\s]*(low|medium|high)"
        severity_match = re.search(severity_pattern, analysis_text.lower())
        if severity_match:
            metrics['severity_level'] = severity_match.group(1).upper()
        
        # Extract threat level
        threat_pattern = r"threat\s*level[:\s]*(\d+)"
        threat_match = re.search(threat_pattern, analysis_text.lower())
        if threat_match:
            metrics['threat_level'] = int(threat_match.group(1))
        
        # Extract attack type with more comprehensive list
        attack_types = [
            'ddos', 'botnet', 'port scan', 'brute force', 'sql injection', 'xss',
            'malware', 'data exfiltration', 'reconnaissance', 'man-in-the-middle',
            'password attack', 'ransomware', 'zero-day exploit', 'backdoor',
            'cross-site scripting', 'file inclusion', 'command injection',
            'network sweep', 'service scan', 'vulnerability scan', 'exploit attempt',
            'traffic analysis', 'protocol manipulation', 'packet manipulation'
        ]
        
        for attack in attack_types:
            if attack in analysis_text.lower():
                metrics['attack_type'] = attack
                break
        
        # Extract key indicators with enhanced patterns
        indicator_patterns = [
            r"key\s*indicators?[:\s]+(.*?)(?=\n|$)",
            r"suspicious\s*patterns?[:\s]+(.*?)(?=\n|$)",
            r"unusual\s*patterns?[:\s]+(.*?)(?=\n|$)",
            r"anomalous\s*behavior[:\s]+(.*?)(?=\n|$)"
        ]
        
        for pattern in indicator_patterns:
            matches = re.finditer(pattern, analysis_text.lower())
            metrics['key_indicators'].extend([m.group(1).strip() for m in matches])
        
        # Extract attack vectors
        vector_pattern = r"attack\s*vectors?[:\s]+(.*?)(?=\n|$)"
        vector_matches = re.finditer(vector_pattern, analysis_text.lower())
        metrics['attack_vectors'] = [m.group(1).strip() for m in vector_matches]
        
        # Extract suspicious patterns
        suspicious_patterns = [
            r"unusual\s*packet\s*sizes?[:\s]+(.*?)(?=\n|$)",
            r"abnormal\s*flag\s*patterns?[:\s]+(.*?)(?=\n|$)",
            r"non-standard\s*ports?[:\s]+(.*?)(?=\n|$)",
            r"irregular\s*timing[:\s]+(.*?)(?=\n|$)"
        ]
        
        for pattern in suspicious_patterns:
            matches = re.finditer(pattern, analysis_text.lower())
            metrics['suspicious_patterns'].extend([m.group(1).strip() for m in matches])
        
        # Extract recommendations
        rec_patterns = [
            r"recommendations?[:\s]+(.*?)(?=\n|$)",
            r"suggested\s*actions?[:\s]+(.*?)(?=\n|$)",
            r"security\s*measures?[:\s]+(.*?)(?=\n|$)"
        ]
        
        for pattern in rec_patterns:
            matches = re.finditer(pattern, analysis_text.lower())
            metrics['recommendations'].extend([m.group(1).strip() for m in matches])
        
        return metrics
    except Exception as e:
        logging.error(f"Error extracting attack metrics: {str(e)}")
        return None

def verify_traffic_samples(data_path, num_samples=10):
    """Verify multiple traffic samples for attacks with enhanced analysis."""
    try:
        # Load configuration
        config = load_config()
        client = OpenAI(api_key=config['openai_api_key'])
        logging.info("OpenAI client initialized")
        
        # Create results directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = f'reports/attack_verification_{timestamp}'
        os.makedirs(results_dir, exist_ok=True)
        
        # Initialize results storage
        all_results = []
        attack_summary = {
            'total_samples': num_samples,
            'malicious_samples': 0,
            'attack_types': {},
            'severity_levels': {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0},
            'threat_levels': {str(i): 0 for i in range(1, 11)},
            'suspicious_patterns': {},
            'attack_vectors': {}
        }
        
        # Process samples
        for i in tqdm(range(num_samples), desc="Analyzing traffic samples"):
            try:
                # Load and verify sample
                sample = load_traffic_sample(data_path)
                analysis = verify_attack_with_openai(client, sample)
                metrics = extract_attack_metrics(analysis)
                
                # Update summary with enhanced metrics
                if metrics['malicious_confidence'] and metrics['malicious_confidence'] > 55:  # Adjusted threshold
                    attack_summary['malicious_samples'] += 1
                
                if metrics['attack_type']:
                    attack_summary['attack_types'][metrics['attack_type']] = \
                        attack_summary['attack_types'].get(metrics['attack_type'], 0) + 1
                
                if metrics['severity_level']:
                    attack_summary['severity_levels'][metrics['severity_level']] += 1
                
                if metrics['threat_level']:
                    level = str(min(max(metrics['threat_level'], 1), 10))
                    attack_summary['threat_levels'][level] += 1
                
                # Track suspicious patterns
                for pattern in metrics['suspicious_patterns']:
                    attack_summary['suspicious_patterns'][pattern] = \
                        attack_summary['suspicious_patterns'].get(pattern, 0) + 1
                
                # Track attack vectors
                for vector in metrics['attack_vectors']:
                    attack_summary['attack_vectors'][vector] = \
                        attack_summary['attack_vectors'].get(vector, 0) + 1
                
                # Save individual analysis
                result = {
                    'sample_index': i,
                    'analysis': analysis,
                    'metrics': metrics,
                    'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S")
                }
                all_results.append(result)
                
                with open(f'{results_dir}/sample_{i}_analysis.txt', 'w') as f:
                    f.write(analysis)
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"Error processing sample {i}: {str(e)}")
                continue
        
        # Calculate summary statistics
        attack_summary['malicious_percentage'] = \
            (attack_summary['malicious_samples'] / num_samples) * 100 if num_samples > 0 else 0
        
        # Save full results
        summary = {
            'timestamp': timestamp,
            'attack_summary': attack_summary,
            'detailed_results': all_results
        }
        
        with open(f'{results_dir}/verification_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print enhanced summary
        logging.info("\nAttack Analysis Summary:")
        logging.info(f"Total Samples Analyzed: {num_samples}")
        logging.info(f"Malicious Samples Detected: {attack_summary['malicious_samples']} ({attack_summary['malicious_percentage']:.2f}%)")
        logging.info("\nAttack Types Detected:")
        for attack_type, count in attack_summary['attack_types'].items():
            logging.info(f"- {attack_type}: {count}")
        logging.info("\nSeverity Distribution:")
        for level, count in attack_summary['severity_levels'].items():
            logging.info(f"- {level}: {count}")
        logging.info("\nThreat Level Distribution:")
        for level, count in attack_summary['threat_levels'].items():
            if count > 0:
                logging.info(f"- Level {level}: {count}")
        logging.info("\nMost Common Suspicious Patterns:")
        for pattern, count in sorted(attack_summary['suspicious_patterns'].items(), key=lambda x: x[1], reverse=True)[:5]:
            logging.info(f"- {pattern}: {count}")
        logging.info("\nMost Common Attack Vectors:")
        for vector, count in sorted(attack_summary['attack_vectors'].items(), key=lambda x: x[1], reverse=True)[:5]:
            logging.info(f"- {vector}: {count}")
        
        logging.info(f"\nDetailed results saved to {results_dir}")
        return summary
        
    except Exception as e:
        logging.error(f"Error in traffic verification: {str(e)}")
        raise

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, default='data/processed/test_data.csv',
                      help='Path to the traffic data file')
    parser.add_argument('--num_samples', type=int, default=10,
                      help='Number of samples to analyze')
    args = parser.parse_args()
    
    verify_traffic_samples(args.data_path, args.num_samples) 