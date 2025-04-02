from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.core.window import Window
import psutil
import socket
import netifaces
import requests
import json
from datetime import datetime
import threading
import time

class NetworkMonitorApp(App):
    def build(self):
        # Set window size for testing
        Window.size = (400, 700)
        
        # Main layout
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title = Label(
            text='SDN Network Monitor',
            size_hint_y=None,
            height=50,
            font_size='20sp',
            bold=True
        )
        self.main_layout.add_widget(title)
        
        # Client Info Section
        self.client_info = GridLayout(
            cols=2,
            size_hint_y=None,
            height=200,
            spacing=5,
            padding=5
        )
        self.client_info.add_widget(Label(text='Hostname:'))
        self.hostname_label = Label(text='Loading...')
        self.client_info.add_widget(self.hostname_label)
        
        self.client_info.add_widget(Label(text='Local IP:'))
        self.local_ip_label = Label(text='Loading...')
        self.client_info.add_widget(self.local_ip_label)
        
        self.client_info.add_widget(Label(text='Public IP:'))
        self.public_ip_label = Label(text='Loading...')
        self.client_info.add_widget(self.public_ip_label)
        
        self.main_layout.add_widget(self.client_info)
        
        # Network Metrics Section
        metrics_title = Label(
            text='Network Metrics',
            size_hint_y=None,
            height=30,
            font_size='16sp',
            bold=True
        )
        self.main_layout.add_widget(metrics_title)
        
        self.metrics_layout = GridLayout(
            cols=2,
            size_hint_y=None,
            height=200,
            spacing=5,
            padding=5
        )
        
        # Add metric labels
        metrics = [
            ('CPU Usage:', 'cpu_usage'),
            ('Memory Usage:', 'memory_usage'),
            ('Network Traffic:', 'network_traffic'),
            ('Active Connections:', 'active_connections'),
            ('Network Errors:', 'network_errors')
        ]
        
        for label_text, metric_id in metrics:
            self.metrics_layout.add_widget(Label(text=label_text))
            label = Label(text='0%')
            setattr(self, f'{metric_id}_label', label)
            self.metrics_layout.add_widget(label)
        
        self.main_layout.add_widget(self.metrics_layout)
        
        # Network Interfaces Section
        interfaces_title = Label(
            text='Network Interfaces',
            size_hint_y=None,
            height=30,
            font_size='16sp',
            bold=True
        )
        self.main_layout.add_widget(interfaces_title)
        
        # Scrollable area for interfaces
        scroll = ScrollView(size_hint=(1, 1))
        self.interfaces_layout = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=5,
            padding=5
        )
        self.interfaces_layout.bind(minimum_height=self.interfaces_layout.setter('height'))
        scroll.add_widget(self.interfaces_layout)
        self.main_layout.add_widget(scroll)
        
        # Control buttons
        button_layout = BoxLayout(
            size_hint_y=None,
            height=50,
            spacing=10
        )
        
        start_button = Button(
            text='Start Monitoring',
            on_press=self.start_monitoring
        )
        stop_button = Button(
            text='Stop Monitoring',
            on_press=self.stop_monitoring
        )
        
        button_layout.add_widget(start_button)
        button_layout.add_widget(stop_button)
        self.main_layout.add_widget(button_layout)
        
        # Initialize monitoring state
        self.monitoring = False
        self.monitor_thread = None
        
        # Start initial data collection
        self.update_client_info()
        
        return self.main_layout
    
    def update_client_info(self):
        try:
            # Get hostname
            hostname = socket.gethostname()
            self.hostname_label.text = hostname
            
            # Get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            self.local_ip_label.text = local_ip
            
            # Get public IP
            try:
                response = requests.get('https://api.ipify.org?format=json', timeout=5)
                if response.status_code == 200:
                    public_ip = response.json()['ip']
                    self.public_ip_label.text = public_ip
            except:
                self.public_ip_label.text = 'Unable to fetch'
            
            # Update network interfaces
            self.interfaces_layout.clear_widgets()
            for interface in netifaces.interfaces():
                interface_info = f"{interface}: "
                addrs = netifaces.ifaddresses(interface)
                
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        interface_info += f"IP: {addr['addr']}, "
                
                if netifaces.AF_LINK in addrs:
                    interface_info += f"MAC: {addrs[netifaces.AF_LINK][0]['addr']}"
                
                self.interfaces_layout.add_widget(Label(
                    text=interface_info,
                    size_hint_y=None,
                    height=30
                ))
                
        except Exception as e:
            print(f"Error updating client info: {str(e)}")
    
    def update_metrics(self):
        try:
            # CPU Usage
            cpu_percent = psutil.cpu_percent()
            self.cpu_usage_label.text = f"{cpu_percent}%"
            
            # Memory Usage
            memory = psutil.virtual_memory()
            self.memory_usage_label.text = f"{memory.percent}%"
            
            # Network Traffic
            net_io = psutil.net_io_counters()
            self.network_traffic_label.text = f"↑{net_io.bytes_sent/1024/1024:.1f}MB ↓{net_io.bytes_recv/1024/1024:.1f}MB"
            
            # Active Connections
            connections = len(psutil.net_connections())
            self.active_connections_label.text = str(connections)
            
            # Network Errors
            net_io = psutil.net_io_counters()
            self.network_errors_label.text = str(net_io.errin + net_io.errout)
            
        except Exception as e:
            print(f"Error updating metrics: {str(e)}")
    
    def monitoring_loop(self):
        while self.monitoring:
            self.update_metrics()
            time.sleep(1)
    
    def start_monitoring(self, instance):
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitoring_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
    
    def stop_monitoring(self, instance):
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()

if __name__ == '__main__':
    NetworkMonitorApp().run() 