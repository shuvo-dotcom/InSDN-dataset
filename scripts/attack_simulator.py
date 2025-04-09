import socket
import threading
import time
import random
import struct
import sys
import logging
from scapy.all import *
from scapy.layers.inet import IP, TCP, UDP, ICMP

class SafeAttackSimulator:
    def __init__(self, target_ip, target_port=None):
        self.target_ip = target_ip
        self.target_port = target_port
        self.running = False
        self.setup_logging()
        self.safe_mode = True  # Enable safe mode by default
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/attack_simulator.log'),
                logging.StreamHandler()
            ]
        )
    
    def safe_ddos(self, duration=30, num_threads=5):
        """Simulate DDoS attack in safe mode"""
        logging.info(f"Starting SAFE DDoS simulation on {self.target_ip}")
        self.running = True
        
        def safe_flood():
            while self.running:
                try:
                    # Create a socket but don't actually connect
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.1)  # Very short timeout
                    # Just log the attempt instead of actually connecting
                    logging.info(f"Simulated connection attempt to {self.target_ip}")
                    s.close()
                except:
                    pass
                time.sleep(0.1)  # Longer delay to prevent system stress
        
        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=safe_flood)
            t.daemon = True
            threads.append(t)
            t.start()
        
        time.sleep(duration)
        self.running = False
        logging.info("Safe DDoS simulation completed")
    
    def safe_port_scan(self, start_port=1, end_port=100):
        """Simulate port scanning in safe mode"""
        logging.info(f"Starting SAFE port scan simulation on {self.target_ip}")
        simulated_open_ports = []
        
        def safe_scan(port):
            # Simulate port scanning without actually connecting
            if random.random() < 0.1:  # 10% chance of "finding" an open port
                simulated_open_ports.append(port)
                logging.info(f"Simulated open port found: {port}")
        
        for port in range(start_port, end_port + 1):
            safe_scan(port)
            time.sleep(0.01)  # Small delay between ports
        
        logging.info(f"Safe port scan completed. Simulated open ports: {simulated_open_ports}")
        return simulated_open_ports
    
    def safe_syn_flood(self, duration=20):
        """Simulate SYN flood in safe mode"""
        logging.info(f"Starting SAFE SYN flood simulation on {self.target_ip}")
        self.running = True
        
        def safe_flood():
            while self.running:
                try:
                    # Just log the SYN packet instead of sending it
                    source_port = random.randint(1024, 65535)
                    dest_port = self.target_port or random.randint(1, 65535)
                    logging.info(f"Simulated SYN packet: src_port={source_port}, dst_port={dest_port}")
                except:
                    pass
                time.sleep(0.1)  # Longer delay to prevent system stress
        
        t = threading.Thread(target=safe_flood)
        t.daemon = True
        t.start()
        
        time.sleep(duration)
        self.running = False
        logging.info("Safe SYN flood simulation completed")
    
    def safe_brute_force(self, duration=30):
        """Simulate brute force attack in safe mode"""
        logging.info(f"Starting SAFE brute force simulation on {self.target_ip}")
        self.running = True
        
        def safe_login_attempt():
            while self.running:
                try:
                    # Simulate login attempt without actually trying
                    username = random.choice(['admin', 'root', 'user', 'test'])
                    password = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz1234567890', k=8))
                    logging.info(f"Simulated login attempt: {username}:{password}")
                except:
                    pass
                time.sleep(0.5)  # Longer delay between attempts
        
        threads = []
        for _ in range(2):  # Reduced number of concurrent attempts
            t = threading.Thread(target=safe_login_attempt)
            t.daemon = True
            threads.append(t)
            t.start()
        
        time.sleep(duration)
        self.running = False
        logging.info("Safe brute force simulation completed")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python attack_simulator.py <target_ip> [target_port]")
        print("Note: This is a SAFE simulation that only generates logs and patterns")
        print("      No actual network connections or harmful activities are performed")
        sys.exit(1)
    
    target_ip = sys.argv[1]
    target_port = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    simulator = SafeAttackSimulator(target_ip, target_port)
    
    print("\n=== SAFE ATTACK SIMULATOR ===")
    print("This simulator only generates detectable patterns")
    print("No actual network connections or harmful activities are performed\n")
    
    print("Select simulation type:")
    print("1. DDoS Pattern Simulation")
    print("2. Port Scan Pattern Simulation")
    print("3. SYN Flood Pattern Simulation")
    print("4. Brute Force Pattern Simulation")
    
    choice = input("\nEnter your choice (1-4): ")
    
    if choice == "1":
        simulator.safe_ddos()
    elif choice == "2":
        simulator.safe_port_scan()
    elif choice == "3":
        simulator.safe_syn_flood()
    elif choice == "4":
        simulator.safe_brute_force()
    else:
        print("Invalid choice") 