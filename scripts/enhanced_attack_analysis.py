import os
import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime
from tqdm import tqdm
import re

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/enhanced_attack_analysis.log'),
        logging.StreamHandler()
    ]
)

def calculate_network_metrics(sample):
    """Calculate additional network metrics for enhanced analysis."""
    try:
        metrics = {}
        
        # Calculate packet size statistics
        if 'Pkt Len Min' in sample and 'Pkt Len Max' in sample:
            min_len = float(sample['Pkt Len Min'])
            max_len = float(sample['Pkt Len Max'])
            if min_len > 0:  # Avoid division by zero
                metrics['packet_size_ratio'] = max_len / min_len
            metrics['packet_size_range'] = max_len - min_len
        
        # Calculate flag ratios and patterns
        flag_metrics = {}
        for flag in ['PSH', 'URG', 'SYN', 'RST', 'FIN', 'ACK']:
            flag_count = float(sample.get(f'{flag} Flag Cnt', 0))
            total_pkts = float(sample.get('Tot Fwd Pkts', 0))
            if total_pkts > 0:
                flag_metrics[f'{flag.lower()}_flag_ratio'] = flag_count / total_pkts
            flag_metrics[f'{flag.lower()}_flag_count'] = flag_count
        
        metrics['flag_metrics'] = flag_metrics
        
        # Calculate timing patterns
        timing_metrics = {}
        if 'Flow IAT Mean' in sample and 'Flow IAT Std' in sample:
            iat_mean = float(sample['Flow IAT Mean'])
            iat_std = float(sample['Flow IAT Std'])
            if iat_mean > 0:
                timing_metrics['iat_variability'] = iat_std / iat_mean
            timing_metrics['iat_mean'] = iat_mean
            timing_metrics['iat_std'] = iat_std
        
        if 'Active Mean' in sample and 'Idle Mean' in sample:
            timing_metrics['active_mean'] = float(sample['Active Mean'])
            timing_metrics['idle_mean'] = float(sample['Idle Mean'])
        
        metrics['timing_metrics'] = timing_metrics
        
        # Calculate flow characteristics
        flow_metrics = {}
        if 'Flow Duration' in sample and 'Tot Fwd Pkts' in sample:
            duration = float(sample['Flow Duration'])
            total_pkts = float(sample['Tot Fwd Pkts'])
            if duration > 0:
                flow_metrics['packet_rate'] = total_pkts / duration
        
        if 'Flow Byts/s' in sample and 'Flow Pkts/s' in sample:
            flow_metrics['bytes_per_second'] = float(sample['Flow Byts/s'])
            flow_metrics['packets_per_second'] = float(sample['Flow Pkts/s'])
        
        metrics['flow_metrics'] = flow_metrics
        
        # Calculate protocol-specific metrics
        protocol_metrics = {}
        if 'Protocol' in sample and 'Dst Port' in sample:
            protocol_metrics['protocol'] = str(sample['Protocol']).lower()
            protocol_metrics['dst_port'] = int(sample['Dst Port'])
            protocol_metrics['port_category'] = 'well_known' if 0 <= protocol_metrics['dst_port'] < 1024 else \
                                             'registered' if 1024 <= protocol_metrics['dst_port'] < 49152 else \
                                             'dynamic'
        
        metrics['protocol_metrics'] = protocol_metrics
        
        # Add raw values for reference
        metrics['raw_values'] = {
            'packet_length': {
                'min': sample.get('Pkt Len Min', 'N/A'),
                'max': sample.get('Pkt Len Max', 'N/A'),
                'mean': sample.get('Pkt Len Mean', 'N/A'),
                'std': sample.get('Pkt Len Std', 'N/A')
            },
            'flags': {
                'psh': sample.get('PSH Flag Cnt', 'N/A'),
                'urg': sample.get('URG Flag Cnt', 'N/A'),
                'syn': sample.get('SYN Flag Cnt', 'N/A'),
                'rst': sample.get('RST Flag Cnt', 'N/A'),
                'fin': sample.get('FIN Flag Cnt', 'N/A'),
                'ack': sample.get('ACK Flag Cnt', 'N/A'),
                'total_forward': sample.get('Tot Fwd Pkts', 'N/A')
            },
            'timing': {
                'iat_mean': sample.get('Flow IAT Mean', 'N/A'),
                'iat_std': sample.get('Flow IAT Std', 'N/A'),
                'active_mean': sample.get('Active Mean', 'N/A'),
                'idle_mean': sample.get('Idle Mean', 'N/A')
            },
            'flow': {
                'duration': sample.get('Flow Duration', 'N/A'),
                'total_packets': sample.get('Tot Fwd Pkts', 'N/A'),
                'bytes_per_second': sample.get('Flow Byts/s', 'N/A'),
                'packets_per_second': sample.get('Flow Pkts/s', 'N/A')
            }
        }
        
        return metrics
    except Exception as e:
        logging.error(f"Error calculating network metrics: {str(e)}")
        return {}

def analyze_suspicious_patterns(sample, metrics):
    """Analyze traffic patterns for suspicious behavior."""
    try:
        patterns = []
        
        # Check for unusual packet sizes
        if 'packet_size_ratio' in metrics and metrics['packet_size_ratio'] > 100:
            patterns.append(f"Unusual packet size ratio: {metrics['packet_size_ratio']:.2f}")
        
        if 'packet_size_range' in metrics and metrics['packet_size_range'] > 1000:
            patterns.append(f"Large packet size range: {metrics['packet_size_range']:.2f}")
        
        # Check for abnormal flag patterns
        if 'flag_metrics' in metrics:
            flag_metrics = metrics['flag_metrics']
            
            # Check individual flag ratios
            for flag, ratio in flag_metrics.items():
                if 'ratio' in flag and ratio > 0.8:
                    patterns.append(f"High {flag.replace('_flag_ratio', '')} flag ratio: {ratio:.2f}")
            
            # Check suspicious flag combinations
            if all(flag_metrics.get(f'{flag}_flag_count', 0) > 0 for flag in ['psh', 'urg', 'syn']):
                patterns.append("Suspicious flag combination: PSH+URG+SYN")
            
            if flag_metrics.get('syn_flag_count', 0) > 0 and flag_metrics.get('ack_flag_count', 0) == 0:
                patterns.append("Incomplete TCP handshake: SYN without ACK")
        
        # Check for irregular timing
        if 'timing_metrics' in metrics:
            timing_metrics = metrics['timing_metrics']
            
            if 'iat_variability' in timing_metrics and timing_metrics['iat_variability'] > 2.0:
                patterns.append(f"High IAT variability: {timing_metrics['iat_variability']:.2f}")
            
            if 'active_mean' in timing_metrics and 'idle_mean' in timing_metrics:
                if timing_metrics['active_mean'] > 1000 or timing_metrics['idle_mean'] > 1000:
                    patterns.append(f"Unusual timing pattern: Active={timing_metrics['active_mean']:.2f}, Idle={timing_metrics['idle_mean']:.2f}")
        
        # Check for unusual packet rates
        if 'flow_metrics' in metrics:
            flow_metrics = metrics['flow_metrics']
            
            if 'packet_rate' in flow_metrics and flow_metrics['packet_rate'] > 1000:
                patterns.append(f"High packet rate: {flow_metrics['packet_rate']:.2f}")
            
            if 'bytes_per_second' in flow_metrics and flow_metrics['bytes_per_second'] > 1000000:
                patterns.append(f"High data transfer rate: {flow_metrics['bytes_per_second']:.2f} bytes/s")
        
        # Check for protocol-specific anomalies
        if 'protocol_metrics' in metrics:
            protocol_metrics = metrics['protocol_metrics']
            
            if protocol_metrics.get('port_category') == 'dynamic':
                patterns.append(f"Non-standard port usage: {protocol_metrics['dst_port']}")
            
            if protocol_metrics.get('protocol') == 'tcp' and protocol_metrics.get('dst_port') in [53, 80, 443]:
                patterns.append(f"Unusual protocol-port combination: {protocol_metrics['protocol']}:{protocol_metrics['dst_port']}")
        
        return patterns
    except Exception as e:
        logging.error(f"Error analyzing suspicious patterns: {str(e)}")
        return []

def correlate_metrics_with_attacks(metrics, patterns):
    """Correlate network metrics with specific attack types."""
    try:
        correlations = []
        
        # DDoS detection
        if ('flow_metrics' in metrics and 
            metrics['flow_metrics'].get('packet_rate', 0) > 1000 and 
            metrics['flow_metrics'].get('bytes_per_second', 0) > 1000000):
            correlations.append({
                'attack_type': 'ddos',
                'confidence': 0.8,
                'indicators': ['High packet rate', 'High data transfer rate']
            })
        
        # Port scan detection
        if ('protocol_metrics' in metrics and 
            metrics['protocol_metrics'].get('port_category') == 'dynamic' and
            metrics['flag_metrics'].get('syn_flag_count', 0) > 0 and
            metrics['flag_metrics'].get('ack_flag_count', 0) == 0):
            correlations.append({
                'attack_type': 'port_scan',
                'confidence': 0.7,
                'indicators': ['Non-standard port', 'Incomplete TCP handshake']
            })
        
        # Reconnaissance detection
        if ('timing_metrics' in metrics and
            metrics['timing_metrics'].get('iat_variability', 0) > 2.0 and
            metrics['flag_metrics'].get('syn_flag_count', 0) > 0):
            correlations.append({
                'attack_type': 'reconnaissance',
                'confidence': 0.6,
                'indicators': ['High IAT variability', 'SYN flag presence']
            })
        
        # Data exfiltration detection
        if ('flow_metrics' in metrics and
            metrics['flow_metrics'].get('bytes_per_second', 0) > 500000 and
            metrics['packet_size_ratio'] > 50):
            correlations.append({
                'attack_type': 'data_exfiltration',
                'confidence': 0.7,
                'indicators': ['High data transfer rate', 'Unusual packet size ratio']
            })
        
        return correlations
    except Exception as e:
        logging.error(f"Error correlating metrics with attacks: {str(e)}")
        return []

def enhance_attack_analysis(results_dir):
    """Enhance attack analysis with additional metrics and patterns."""
    try:
        # Load verification results
        with open(f'{results_dir}/verification_summary.json', 'r') as f:
            summary = json.load(f)
        
        # Load original data
        data = pd.read_csv('data/processed/test_data.csv')
        
        # Initialize enhanced analysis
        enhanced_results = {
            'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
            'original_summary': summary,
            'enhanced_metrics': {},
            'suspicious_patterns': {},
            'attack_correlation': {},
            'metric_correlations': {}
        }
        
        # Process each sample
        for result in summary['detailed_results']:
            sample_idx = result['sample_index']
            if sample_idx < len(data):
                sample = data.iloc[sample_idx].to_dict()
                
                # Calculate additional metrics
                metrics = calculate_network_metrics(sample)
                enhanced_results['enhanced_metrics'][sample_idx] = metrics
                
                # Analyze suspicious patterns
                patterns = analyze_suspicious_patterns(sample, metrics)
                enhanced_results['suspicious_patterns'][sample_idx] = patterns
                
                # Correlate metrics with attacks
                correlations = correlate_metrics_with_attacks(metrics, patterns)
                enhanced_results['metric_correlations'][sample_idx] = correlations
                
                # Correlate with attack detection
                if result['metrics']['malicious_confidence'] and result['metrics']['malicious_confidence'] > 55:
                    enhanced_results['attack_correlation'][sample_idx] = {
                        'confidence': result['metrics']['malicious_confidence'],
                        'patterns': patterns,
                        'metrics': metrics,
                        'correlations': correlations
                    }
        
        # Calculate pattern statistics
        pattern_stats = {}
        for patterns in enhanced_results['suspicious_patterns'].values():
            for pattern in patterns:
                pattern_stats[pattern] = pattern_stats.get(pattern, 0) + 1
        
        enhanced_results['pattern_statistics'] = pattern_stats
        
        # Calculate correlation statistics
        correlation_stats = {}
        for correlations in enhanced_results['metric_correlations'].values():
            for correlation in correlations:
                attack_type = correlation['attack_type']
                if attack_type not in correlation_stats:
                    correlation_stats[attack_type] = {
                        'count': 0,
                        'total_confidence': 0,
                        'indicators': {}
                    }
                correlation_stats[attack_type]['count'] += 1
                correlation_stats[attack_type]['total_confidence'] += correlation['confidence']
                for indicator in correlation['indicators']:
                    correlation_stats[attack_type]['indicators'][indicator] = \
                        correlation_stats[attack_type]['indicators'].get(indicator, 0) + 1
        
        enhanced_results['correlation_statistics'] = correlation_stats
        
        # Save enhanced analysis
        output_file = f'{results_dir}/enhanced_analysis.json'
        with open(output_file, 'w') as f:
            json.dump(enhanced_results, f, indent=2)
        
        # Print enhanced summary
        logging.info("\nEnhanced Analysis Summary:")
        logging.info(f"Total Samples Analyzed: {len(enhanced_results['enhanced_metrics'])}")
        logging.info(f"Samples with Suspicious Patterns: {len(enhanced_results['suspicious_patterns'])}")
        logging.info("\nMost Common Suspicious Patterns:")
        for pattern, count in sorted(pattern_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
            logging.info(f"- {pattern}: {count}")
        logging.info("\nAttack Correlations:")
        for attack_type, stats in correlation_stats.items():
            avg_confidence = stats['total_confidence'] / stats['count']
            logging.info(f"- {attack_type}: {stats['count']} instances (avg confidence: {avg_confidence:.2f})")
            logging.info("  Common indicators:")
            for indicator, count in sorted(stats['indicators'].items(), key=lambda x: x[1], reverse=True)[:3]:
                logging.info(f"  * {indicator}: {count}")
        
        logging.info(f"\nEnhanced analysis saved to {output_file}")
        return enhanced_results
        
    except Exception as e:
        logging.error(f"Error in enhanced analysis: {str(e)}")
        raise

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--results_dir', type=str, required=True,
                      help='Directory containing verification results')
    args = parser.parse_args()
    
    enhance_attack_analysis(args.results_dir) 