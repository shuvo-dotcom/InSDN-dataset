import torch
import pandas as pd
import numpy as np
from openai import OpenAI
import logging
import json
from tqdm import tqdm
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from gan_model import Discriminator  # Import the Discriminator model
from data_loader import load_data  # Import the data loader

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config() -> Dict:
    """Load configuration from config.json"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("config.json not found")
        raise

def load_gan_model(model_path: str) -> torch.nn.Module:
    """Load the trained GAN discriminator model"""
    try:
        # Create a new model instance
        model = Discriminator(input_dim=84)
        # Load the state dict
        state_dict = torch.load(model_path)
        model.load_state_dict(state_dict)
        model.eval()
        return model
    except Exception as e:
        logger.error(f"Error loading GAN model: {e}")
        raise

def analyze_traffic_pattern(sample: pd.Series) -> Dict:
    """Analyze traffic patterns and extract key metrics"""
    metrics = {
        'packet_rate': sample.get('Flow Pkts/s', 0),
        'byte_rate': sample.get('Flow Byts/s', 0),
        'flag_counts': {
            'SYN': sample.get('SYN Flag Cnt', 0),
            'ACK': sample.get('ACK Flag Cnt', 0),
            'FIN': sample.get('FIN Flag Cnt', 0),
            'PSH': sample.get('PSH Flag Cnt', 0),
            'RST': sample.get('RST Flag Cnt', 0),
            'URG': sample.get('URG Flag Cnt', 0)
        },
        'port_analysis': {
            'src_port': sample.get('Src Port', 0),
            'dst_port': sample.get('Dst Port', 0)
        },
        'protocol': sample.get('Protocol', 'unknown'),
        'packet_size': {
            'min': sample.get('Pkt Len Min', 0),
            'max': sample.get('Pkt Len Max', 0),
            'mean': sample.get('Pkt Len Mean', 0)
        },
        'flow_duration': sample.get('Flow Duration', 0),
        'iat': {
            'mean': sample.get('Flow IAT Mean', 0),
            'std': sample.get('Flow IAT Std', 0)
        }
    }
    return metrics

def verify_sample_with_openai(client: OpenAI, sample: pd.Series) -> Dict:
    """Verify a single sample with OpenAI"""
    metrics = analyze_traffic_pattern(sample)
    
    # Prepare the prompt with key metrics
    prompt = f"""Analyze this network traffic sample for potential attacks:
    
    Traffic Metrics:
    - Packet Rate: {metrics['packet_rate']:.2f} pkts/s
    - Byte Rate: {metrics['byte_rate']:.2f} bytes/s
    - Protocol: {metrics['protocol']}
    - Source Port: {metrics['port_analysis']['src_port']}
    - Destination Port: {metrics['port_analysis']['dst_port']}
    - Flow Duration: {metrics['flow_duration']:.2f} seconds
    
    Flag Analysis:
    - SYN: {metrics['flag_counts']['SYN']}
    - ACK: {metrics['flag_counts']['ACK']}
    - FIN: {metrics['flag_counts']['FIN']}
    - PSH: {metrics['flag_counts']['PSH']}
    - RST: {metrics['flag_counts']['RST']}
    - URG: {metrics['flag_counts']['URG']}
    
    Packet Size:
    - Min: {metrics['packet_size']['min']:.2f}
    - Max: {metrics['packet_size']['max']:.2f}
    - Mean: {metrics['packet_size']['mean']:.2f}
    
    Inter-Arrival Time:
    - Mean: {metrics['iat']['mean']:.2f}
    - Std Dev: {metrics['iat']['std']:.2f}
    
    Please analyze this traffic pattern and provide:
    1. Is this traffic malicious? (yes/no)
    2. If yes, what type of attack is it? (e.g., DDoS, port scan, botnet)
    3. Severity level (LOW/MEDIUM/HIGH)
    4. Threat level (1-10)
    5. Key indicators that led to this conclusion
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a network security expert analyzing traffic patterns for potential attacks."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        result = response.choices[0].message.content
        return parse_openai_response(result)
    except Exception as e:
        logger.error(f"Error in OpenAI verification: {e}")
        return {
            'is_malicious': False,
            'attack_type': 'unknown',
            'severity': 'LOW',
            'threat_level': 1,
            'key_indicators': ['Error in analysis']
        }

def parse_openai_response(response: str) -> Dict:
    """Parse OpenAI's response into structured data"""
    try:
        lines = response.split('\n')
        result = {
            'is_malicious': False,
            'attack_type': 'unknown',
            'severity': 'LOW',
            'threat_level': 1,
            'key_indicators': []
        }
        
        for line in lines:
            line = line.lower().strip()
            if 'malicious' in line:
                result['is_malicious'] = 'yes' in line
            elif 'attack' in line:
                if 'ddos' in line:
                    result['attack_type'] = 'ddos'
                elif 'port scan' in line:
                    result['attack_type'] = 'port_scan'
                elif 'botnet' in line:
                    result['attack_type'] = 'botnet'
                elif 'reconnaissance' in line:
                    result['attack_type'] = 'reconnaissance'
            elif 'severity' in line:
                if 'high' in line:
                    result['severity'] = 'HIGH'
                elif 'medium' in line:
                    result['severity'] = 'MEDIUM'
            elif 'threat level' in line:
                try:
                    level = int(''.join(filter(str.isdigit, line)))
                    result['threat_level'] = min(max(level, 1), 10)
                except:
                    pass
            elif 'indicator' in line:
                result['key_indicators'].append(line.split(':')[-1].strip())
        
        return result
    except Exception as e:
        logger.error(f"Error parsing OpenAI response: {e}")
        return {
            'is_malicious': False,
            'attack_type': 'unknown',
            'severity': 'LOW',
            'threat_level': 1,
            'key_indicators': ['Error parsing response']
        }

def detect_attacks(data_path: str, num_samples: int = 100, 
                  gan_threshold: float = 0.5, 
                  openai_threshold: float = 0.7,
                  batch_size: int = 10,
                  openai_verification_rate: float = 0.01) -> None:
    """Detect attacks using combined GAN and OpenAI analysis"""
    try:
        # Load configuration
        config = load_config()
        client = OpenAI(api_key=config['openai_api_key'])
        
        # Load GAN model
        discriminator = load_gan_model('data/models/discriminator.pt')
        
        # Load and preprocess data using the same function as training
        data = load_data(data_path)
        if num_samples > 0:
            data = data.sample(n=min(num_samples, len(data)))
        
        # Initialize results tracking
        results = []
        attack_types = {}
        severity_counts = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0}
        threat_levels = {}
        suspicious_patterns = {}
        
        # Initialize accuracy tracking
        gan_predictions = []
        openai_predictions = []
        gan_verified = []
        
        # Process in batches
        num_batches = (len(data) + batch_size - 1) // batch_size
        for i in tqdm(range(num_batches), desc="Analyzing traffic samples"):
            start_idx = i * batch_size
            end_idx = min(start_idx + batch_size, len(data))
            batch = data.iloc[start_idx:end_idx]
            
            # Extract features for GAN
            features = torch.tensor(batch.values, dtype=torch.float32)
            
            # Get GAN predictions
            with torch.no_grad():
                gan_scores = discriminator(features)
            
            # Check each sample in the batch
            for j, score in enumerate(gan_scores):
                idx = start_idx + j
                score_value = score.item()
                
                # Determine if OpenAI verification is needed
                needs_openai = False
                if score_value > gan_threshold:
                    # Use OpenAI for high-confidence GAN detections (random 1% for validation)
                    if np.random.random() < openai_verification_rate:
                        needs_openai = True
                    # Use OpenAI only for extremely uncertain GAN detections (very close to threshold)
                    elif abs(score_value - gan_threshold) < 0.02:  # Further reduced from 0.03 to 0.02
                        needs_openai = True
                
                if needs_openai:
                    # Verify with OpenAI
                    result = verify_sample_with_openai(client, data.iloc[idx])
                    openai_predictions.append(result['is_malicious'])
                    gan_verified.append(True)
                else:
                    # Use GAN result directly with enhanced confidence scoring
                    confidence = abs(score_value - gan_threshold)
                    is_malicious = score_value > gan_threshold
                    
                    # Determine severity based on confidence
                    if confidence > 0.3:
                        severity = 'HIGH'
                    elif confidence > 0.15:
                        severity = 'MEDIUM'
                    else:
                        severity = 'LOW'
                    
                    # Enhanced attack type detection based on features
                    attack_type = 'normal'
                    if is_malicious:
                        # DDoS detection
                        if data.iloc[idx].get('Flow Pkts/s', 0) > 1000:
                            attack_type = 'ddos'
                        # SYN flood detection
                        elif data.iloc[idx].get('SYN Flag Cnt', 0) > 1000:
                            attack_type = 'syn_flood'
                        # Reset flood detection
                        elif data.iloc[idx].get('RST Flag Cnt', 0) > 500:
                            attack_type = 'reset_flood'
                        # Port scan detection
                        elif data.iloc[idx].get('Dst Port', 0) > 1000:
                            attack_type = 'port_scan'
                        # Botnet detection
                        elif data.iloc[idx].get('Flow Duration', 0) > 300:
                            attack_type = 'botnet'
                    
                    result = {
                        'is_malicious': is_malicious,
                        'attack_type': attack_type,
                        'severity': severity,
                        'threat_level': int(score_value * 10),
                        'key_indicators': [
                            f"GAN confidence: {confidence:.2f}",
                            f"Score: {score_value:.2f}",
                            f"Attack type: {attack_type}"
                        ]
                    }
                    gan_verified.append(False)
                
                gan_predictions.append(is_malicious)
                results.append(result)
                
                # Update statistics
                if result['is_malicious']:
                    attack_type = result['attack_type']
                    attack_types[attack_type] = attack_types.get(attack_type, 0) + 1
                    severity_counts[result['severity']] = severity_counts.get(result['severity'], 0) + 1
                    threat_levels[result['threat_level']] = threat_levels.get(result['threat_level'], 0) + 1
                    
                    for pattern in result['key_indicators']:
                        suspicious_patterns[pattern] = suspicious_patterns.get(pattern, 0) + 1
            
            # Save intermediate results every 50 samples
            if (i + 1) * batch_size % 50 == 0:
                logger.info("\nIntermediate results saved after %d samples", (i + 1) * batch_size)
                logger.info("Current detection rate: %.2f%%", 
                          (len([r for r in results if r['is_malicious']]) / len(results) * 100 if results else 0))
                save_results(results, attack_types, severity_counts, threat_levels, suspicious_patterns)
        
        # Calculate and print accuracy metrics
        gan_verified = np.array(gan_verified)
        gan_predictions = np.array(gan_predictions)
        openai_predictions = np.array(openai_predictions)
        
        # Calculate GAN accuracy on non-verified samples
        gan_accuracy = np.mean(gan_predictions[~gan_verified])
        
        # Calculate OpenAI accuracy on verified samples
        openai_accuracy = np.mean(openai_predictions) if len(openai_predictions) > 0 else 0
        
        # Calculate combined accuracy
        total_samples = len(gan_predictions)
        verified_samples = np.sum(gan_verified)
        combined_accuracy = (gan_accuracy * (total_samples - verified_samples) + 
                           openai_accuracy * verified_samples) / total_samples
        
        logger.info("\nSystem Accuracy Metrics:")
        logger.info(f"GAN Accuracy (non-verified samples): {gan_accuracy:.2%}")
        logger.info(f"OpenAI Accuracy (verified samples): {openai_accuracy:.2%}")
        logger.info(f"Combined System Accuracy: {combined_accuracy:.2%}")
        logger.info(f"OpenAI Verification Rate: {verified_samples/total_samples:.2%}")
        
        # Save final results
        save_results(results, attack_types, severity_counts, threat_levels, suspicious_patterns)
        print_summary(results, attack_types, severity_counts, threat_levels, suspicious_patterns)
        
    except Exception as e:
        logger.error("Error in attack detection: %s", str(e))
        raise

def save_results(results: List[Dict], attack_types: Dict, severity_dist: Dict, 
                threat_levels: Dict, suspicious_patterns: Dict) -> None:
    """Save results to a JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"reports/attack_verification_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    output = {
        'results': results,
        'attack_types': attack_types,
        'severity_distribution': severity_dist,
        'threat_levels': threat_levels,
        'suspicious_patterns': suspicious_patterns
    }
    
    with open(f"{output_dir}/results.json", 'w') as f:
        json.dump(output, f, indent=2)

def print_summary(results: List[Dict], attack_types: Dict, severity_dist: Dict, 
                 threat_levels: Dict, suspicious_patterns: Dict) -> None:
    """Print a summary of the analysis results"""
    malicious_count = sum(1 for r in results if r['is_malicious'])
    
    logger.info("\nAttack Analysis Summary:")
    logger.info(f"Total Samples Analyzed: {len(results)}")
    logger.info(f"Malicious Samples Detected: {malicious_count} ({malicious_count/len(results)*100:.2f}%)")
    
    logger.info("\nAttack Types Detected:")
    for attack_type, count in attack_types.items():
        logger.info(f"- {attack_type}: {count}")
    
    logger.info("\nSeverity Distribution:")
    for severity, count in severity_dist.items():
        logger.info(f"- {severity}: {count}")
    
    logger.info("\nThreat Level Distribution:")
    for level, count in sorted(threat_levels.items()):
        logger.info(f"- Level {level}: {count}")
    
    logger.info("\nMost Common Suspicious Patterns:")
    for pattern, count in sorted(suspicious_patterns.items(), key=lambda x: x[1], reverse=True)[:10]:
        logger.info(f"- {pattern}: {count}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Detect network attacks using GAN and OpenAI")
    parser.add_argument("--data_path", type=str, required=True, help="Path to the input data CSV file")
    parser.add_argument("--num_samples", type=int, default=100, help="Number of samples to analyze")
    parser.add_argument("--gan_threshold", type=float, default=0.5, help="GAN detection threshold")
    parser.add_argument("--openai_threshold", type=float, default=0.7, help="OpenAI verification threshold")
    parser.add_argument("--batch_size", type=int, default=10, help="Batch size for processing")
    parser.add_argument("--openai_verification_rate", type=float, default=0.01, 
                       help="Rate of samples to verify with OpenAI (0.0-1.0)")
    
    args = parser.parse_args()
    detect_attacks(args.data_path, args.num_samples, args.gan_threshold, 
                  args.openai_threshold, args.batch_size, args.openai_verification_rate) 