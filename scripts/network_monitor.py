import psutil
import time
import numpy as np
from datetime import datetime
import json
import os
import logging
import socket
import netifaces
import subprocess
from collections import defaultdict

class NetworkMonitor:
    def __init__(self):
        self.metrics_history = []
        self.connection_history = set()  # Track unique connections
        self.vulnerable_ports = {
            21: "FTP",
            23: "Telnet",
            25: "SMTP",
            80: "HTTP",
            443: "HTTPS",
            3306: "MySQL",
            3389: "RDP",
            5432: "PostgreSQL",
            27017: "MongoDB"
        }
        self.setup_logging()
        self.max_history = 1000
        self.last_bytes_sent = 0
        self.last_bytes_recv = 0
        self.last_time = time.time()
        self.network_interfaces = {}
        self.connections = defaultdict(list)
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/network_monitor.log'),
                logging.StreamHandler()
            ]
        )
    
    def get_network_interfaces(self):
        """Get all network interfaces and their details"""
        interfaces = {}
        for interface in netifaces.interfaces():
            try:
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    interfaces[interface] = {
                        'ip': addrs[netifaces.AF_INET][0]['addr'],
                        'netmask': addrs[netifaces.AF_INET][0]['netmask'],
                        'mac': addrs[netifaces.AF_LINK][0]['addr'] if netifaces.AF_LINK in addrs else None
                    }
            except Exception as e:
                logging.warning(f"Error getting interface {interface} details: {str(e)}")
        return interfaces
    
    def get_active_connections(self):
        """Get active network connections"""
        try:
            # Use netstat to get active connections
            netstat_output = subprocess.check_output(['netstat', '-an']).decode()
            connections = defaultdict(list)
            
            for line in netstat_output.split('\n'):
                if 'ESTABLISHED' in line or 'LISTEN' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        protocol = parts[0]
                        local = parts[3]
                        remote = parts[4] if len(parts) > 4 else '*'
                        state = parts[-1]
                        
                        connections[protocol].append({
                            'local': local,
                            'remote': remote,
                            'state': state
                        })
            
            return connections
        except Exception as e:
            logging.error(f"Error getting active connections: {str(e)}")
            return defaultdict(list)
    
    def get_network_metrics(self):
        """Collect current network metrics"""
        try:
            # Get basic system metrics
            metrics = {
                'timestamp': datetime.now(),
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'connections': self.get_active_connections(),
                'total_connections': 0,
                'new_connections': [],
                'vulnerable_connections': [],
                'traffic_rate': 0,
                'network_errors': 0
            }

            # Calculate total connections and identify new ones
            for protocol, connections in metrics['connections'].items():
                metrics['total_connections'] += len(connections)
                for conn in connections:
                    conn_key = f"{conn['local']}-{conn['remote']}-{conn['state']}"
                    if conn_key not in self.connection_history:
                        self.connection_history.add(conn_key)
                        metrics['new_connections'].append(conn)
                        
                        # Check if connection is potentially vulnerable
                        try:
                            port = int(conn['local'].split(':')[-1])
                            if port in self.vulnerable_ports:
                                metrics['vulnerable_connections'].append({
                                    'connection': conn,
                                    'vulnerability': f"Potentially vulnerable {self.vulnerable_ports[port]} port",
                                    'severity': 'High' if port in [21, 23, 25] else 'Medium'
                                })
                        except (ValueError, IndexError):
                            pass

            # Get network I/O statistics
            net_io = psutil.net_io_counters()
            metrics['traffic_rate'] = (net_io.bytes_sent + net_io.bytes_recv) / (1024 * 1024)  # MB/s
            metrics['network_errors'] = net_io.errin + net_io.errout

            self.metrics_history.append(metrics)
            return metrics

        except psutil.AccessDenied:
            logging.warning("Access denied to network metrics. Running with limited functionality.")
            return {
                'timestamp': datetime.now(),
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'connections': {},
                'total_connections': 0,
                'new_connections': [],
                'vulnerable_connections': [],
                'traffic_rate': 0,
                'network_errors': 0
            }
        except Exception as e:
            logging.error(f"Error getting network metrics: {str(e)}")
            return {
                'timestamp': datetime.now(),
                'cpu_percent': 0,
                'memory_percent': 0,
                'connections': {},
                'total_connections': 0,
                'new_connections': [],
                'vulnerable_connections': [],
                'traffic_rate': 0,
                'network_errors': 0
            }
    
    def get_anomaly_score(self, metrics):
        """Calculate anomaly score based on network metrics"""
        try:
            # Calculate anomaly score based on multiple factors
            score = 0.0
            
            # CPU usage factor (0-0.3)
            cpu_factor = min(metrics['cpu_percent'] / 100, 1.0) * 0.3
            score += cpu_factor
            
            # Memory usage factor (0-0.3)
            memory_factor = min(metrics['memory_percent'] / 100, 1.0) * 0.3
            score += memory_factor
            
            # Network traffic factor (0-0.2)
            traffic_factor = min(metrics['traffic_rate'] / 1000, 1.0) * 0.2
            score += traffic_factor
            
            # Connection count factor (0-0.2)
            connection_factor = min(metrics['total_connections'] / 100, 1.0) * 0.2
            score += connection_factor
            
            return min(score, 1.0)
        except Exception as e:
            logging.error(f"Error calculating anomaly score: {str(e)}")
            return 0.0
    
    def get_network_topology(self):
        """Get current network topology information"""
        try:
            # Get current network interfaces
            interfaces = {}
            for interface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    interfaces[interface] = {
                        'ip': addrs[netifaces.AF_INET][0]['addr'],
                        'netmask': addrs[netifaces.AF_INET][0]['netmask'],
                        'mac': addrs.get(netifaces.AF_LINK, [{'addr': None}])[0]['addr']
                    }

            # Get active connections
            connections = self.get_active_connections()
            
            # Create topology
            nodes = []
            links = []
            
            # Add host node
            hostname = socket.gethostname()
            nodes.append({
                'id': 'host',
                'name': hostname,
                'type': 'host',
                'ip': socket.gethostbyname(hostname)
            })
            
            # Add interface nodes and links
            for interface, details in interfaces.items():
                node_id = f"interface_{interface}"
                nodes.append({
                    'id': node_id,
                    'name': interface,
                    'type': 'interface',
                    'ip': details['ip'],
                    'mac': details['mac']
                })
                links.append({
                    'source': 'host',
                    'target': node_id,
                    'type': 'physical'
                })
            
            # Add connection nodes and links
            for protocol, conns in connections.items():
                for conn in conns:
                    if conn['remote'] != '*':
                        remote_ip = conn['remote'].split(':')[0]
                        node_id = f"remote_{remote_ip}"
                        
                        # Add remote node if not exists
                        if not any(n['id'] == node_id for n in nodes):
                            nodes.append({
                                'id': node_id,
                                'name': remote_ip,
                                'type': 'remote',
                                'ip': remote_ip
                            })
                        
                        # Add connection link
                        links.append({
                            'source': 'host',
                            'target': node_id,
                            'type': 'connection',
                            'protocol': protocol,
                            'state': conn['state']
                        })
            
            return {
                'nodes': nodes,
                'links': links
            }
        except Exception as e:
            logging.error(f"Error getting network topology: {str(e)}")
            return {'nodes': [], 'links': []}
    
    def save_metrics(self, filepath):
        """Save collected metrics to a file"""
        with open(filepath, 'w') as f:
            json.dump(self.metrics_history, f)
    
    def load_metrics(self, filepath):
        """Load metrics from a file"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                self.metrics_history = json.load(f) 