import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from datetime import datetime
import time
import os
import logging
import sys
from scripts.data_preprocess import preprocess_data
from scripts.train_gan import train_gan
from scripts.network_monitor import NetworkMonitor
import torch
import numpy as np

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Set page config
st.set_page_config(
    page_title="SDN Anomaly Detection Dashboard",
    page_icon="🔒",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        margin-top: 1rem;
    }
    .vulnerability-high {
        color: #ff4444;
    }
    .vulnerability-medium {
        color: #ffbb33;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize network monitor
@st.cache_resource
def get_network_monitor():
    return NetworkMonitor()

# Title and description
st.title("🔒 SDN Anomaly Detection Dashboard")
st.markdown("""
    This dashboard provides real-time monitoring and anomaly detection for your Software-Defined Network.
    Use the sidebar to configure settings and view different aspects of your network security.
""")

# Sidebar
st.sidebar.title("Settings")
st.sidebar.markdown("### Configuration")

# Display client information in sidebar (moved outside the loop)
st.sidebar.header("Client Information")
monitor = get_network_monitor()
client_info = monitor.get_client_info()

if client_info['public_ip']:
    st.sidebar.metric("Public IP", client_info['public_ip'])
if client_info['local_ip']:
    st.sidebar.metric("Local IP", client_info['local_ip'])
st.sidebar.metric("Hostname", client_info['hostname'])

# Display network interfaces
st.sidebar.subheader("Network Interfaces")
for interface in client_info['interfaces']:
    with st.sidebar.expander(interface['name']):
        st.write(f"Status: {interface['status']}")
        if interface['mac_address']:
            st.write(f"MAC: {interface['mac_address']}")
        for ip_info in interface['ip_addresses']:
            st.write(f"IP: {ip_info['ip']}")
            st.write(f"Netmask: {ip_info['netmask']}")

# Model settings
st.sidebar.subheader("Model Settings")
epochs = st.sidebar.slider("Training Epochs", min_value=10, max_value=200, value=50)
threshold = st.sidebar.slider("Anomaly Detection Threshold", min_value=0.0, max_value=1.0, value=0.5)

# Network settings
st.sidebar.subheader("Network Settings")
monitoring_interval = st.sidebar.slider("Monitoring Interval (seconds)", min_value=1, max_value=60, value=5)

# Main content
tab1, tab2, tab3 = st.tabs(["Live Monitoring", "Anomaly Detection", "Network Statistics"])

# Live Monitoring Tab
with tab1:
    st.header("Live Network Monitoring")
    
    # Create placeholders for metrics and alerts
    metrics_placeholder = st.empty()
    alerts_placeholder = st.empty()
    topology_placeholder = st.empty()
    
    # Start monitoring
    while True:
        try:
            # Get current metrics
            metrics = monitor.get_network_metrics()
            if metrics is None:
                st.error("Failed to get network metrics. Please check the logs for details.")
                time.sleep(monitoring_interval)
                continue
                
            anomaly_score = monitor.get_anomaly_score(metrics)
            
            # Update metrics display
            with metrics_placeholder.container():
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(label="Active Connections", 
                             value=metrics.get('total_connections', 0),
                             delta=f"{metrics.get('total_connections', 0) - metrics.get('prev_connections', metrics.get('total_connections', 0))}")
                    st.metric(label="Network Traffic (MB/s)", 
                             value=f"{metrics.get('traffic_rate', 0):.2f}",
                             delta=f"{metrics.get('traffic_rate', 0) - metrics.get('prev_traffic_rate', metrics.get('traffic_rate', 0)):.2f}")
                
                with col2:
                    st.metric(label="CPU Usage (%)", 
                             value=f"{metrics.get('cpu_percent', 0):.1f}",
                             delta=f"{metrics.get('cpu_percent', 0) - metrics.get('prev_cpu_percent', metrics.get('cpu_percent', 0)):.1f}")
                    st.metric(label="Memory Usage (%)", 
                             value=f"{metrics.get('memory_percent', 0):.1f}",
                             delta=f"{metrics.get('memory_percent', 0) - metrics.get('prev_memory_percent', metrics.get('memory_percent', 0)):.1f}")
                
                with col3:
                    st.metric(label="Anomaly Score", 
                             value=f"{anomaly_score:.2f}",
                             delta=f"{anomaly_score - metrics.get('prev_anomaly_score', anomaly_score):.2f}")
                    st.metric(label="Network Errors", 
                             value=metrics.get('network_errors', 0),
                             delta=f"{metrics.get('network_errors', 0) - metrics.get('prev_network_errors', metrics.get('network_errors', 0))}")
            
            # Display new connections and vulnerabilities
            with alerts_placeholder.container():
                if metrics.get('new_connections'):
                    st.subheader("New Connections")
                    new_conn_data = []
                    for conn in metrics['new_connections']:
                        new_conn_data.append({
                            'Protocol': conn.get('protocol', 'Unknown'),
                            'Local Address': conn.get('local', 'Unknown'),
                            'Remote Address': conn.get('remote', 'Unknown'),
                            'State': conn.get('state', 'Unknown'),
                            'Time': metrics['timestamp'].strftime('%H:%M:%S')
                        })
                    st.dataframe(pd.DataFrame(new_conn_data))
                
                if metrics.get('vulnerable_connections'):
                    st.subheader("⚠️ Potentially Vulnerable Connections")
                    vuln_data = []
                    for vuln in metrics['vulnerable_connections']:
                        conn = vuln.get('connection', {})
                        vuln_data.append({
                            'Protocol': conn.get('protocol', 'Unknown'),
                            'Local Address': conn.get('local', 'Unknown'),
                            'Remote Address': conn.get('remote', 'Unknown'),
                            'State': conn.get('state', 'Unknown'),
                            'Vulnerability': vuln.get('vulnerability', 'Unknown'),
                            'Severity': vuln.get('severity', 'Unknown'),
                            'Time': metrics['timestamp'].strftime('%H:%M:%S')
                        })
                    df = pd.DataFrame(vuln_data)
                    for _, row in df.iterrows():
                        severity_class = 'vulnerability-high' if row['Severity'] == 'High' else 'vulnerability-medium'
                        st.markdown(f"""
                            <div class="{severity_class}">
                                <strong>{row['Vulnerability']}</strong> ({row['Severity']} Severity)<br>
                                Protocol: {row['Protocol']} | Local: {row['Local Address']} | Remote: {row['Remote Address']}<br>
                                Time: {row['Time']}
                            </div>
                        """, unsafe_allow_html=True)
            
            # Update network topology
            with topology_placeholder.container():
                st.subheader("Network Topology")
                topology = monitor.get_network_topology()
                
                if topology and topology.get('nodes'):
                    G = nx.Graph()
                    
                    # Add nodes with different colors based on type
                    for node in topology['nodes']:
                        color = 'red' if node.get('type') == 'host' else \
                                'blue' if node.get('type') == 'interface' else \
                                'green' if node.get('type') == 'internet' else 'gray'
                        G.add_node(node.get('id', ''), 
                                  name=node.get('name', 'Unknown'),
                                  type=node.get('type', 'unknown'),
                                  color=color,
                                  ip=node.get('ip', 'N/A'),
                                  public_ip=node.get('public_ip', 'N/A'))
                    
                    # Add edges with different styles based on type
                    for link in topology.get('links', []):
                        G.add_edge(link.get('source', ''), 
                                  link.get('target', ''),
                                  type=link.get('type', ''),
                                  protocol=link.get('protocol', ''),
                                  state=link.get('state', ''))
                    
                    pos = nx.spring_layout(G)
                    
                    fig = go.Figure()
                    
                    # Add edges
                    for edge in G.edges():
                        x0, y0 = pos[edge[0]]
                        x1, y1 = pos[edge[1]]
                        edge_data = G.edges[edge]
                        fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], 
                                               mode='lines+markers',
                                               line=dict(color='gray', width=1),
                                               marker=dict(size=8, color='gray')))
                    
                    # Add nodes
                    for node in G.nodes():
                        x, y = pos[node]
                        node_data = G.nodes[node]
                        fig.add_trace(go.Scatter(x=[x], y=[y], 
                                               mode='markers+text',
                                               text=[f"{node_data.get('name', 'Unknown')}<br>{node_data.get('ip', 'N/A')}"],
                                               textposition="top center",
                                               marker=dict(size=20, color=node_data.get('color', 'gray'))))
                    
                    fig.update_layout(title="Network Topology", 
                                    showlegend=False,
                                    hovermode='closest')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No network topology information available.")
            
            # Store previous values for delta calculations
            metrics['prev_connections'] = metrics.get('total_connections', 0)
            metrics['prev_traffic_rate'] = metrics.get('traffic_rate', 0)
            metrics['prev_cpu_percent'] = metrics.get('cpu_percent', 0)
            metrics['prev_memory_percent'] = metrics.get('memory_percent', 0)
            metrics['prev_anomaly_score'] = anomaly_score
            metrics['prev_network_errors'] = metrics.get('network_errors', 0)
            
            time.sleep(monitoring_interval)
            
        except Exception as e:
            st.error(f"An error occurred while updating the dashboard: {str(e)}")
            logging.error(f"Dashboard update error: {str(e)}")
            time.sleep(monitoring_interval)

# Anomaly Detection Tab
with tab2:
    st.header("Anomaly Detection")
    
    # Training section
    st.subheader("Model Training")
    if st.button("Train Model"):
        with st.spinner("Training in progress..."):
            try:
                logging.info("Starting model training process")
                preprocess_data()
                train_gan(epochs=epochs)
                st.success("Model training completed successfully!")
                logging.info("Model training completed successfully")
            except Exception as e:
                error_msg = f"Error during training: {str(e)}"
                st.error(error_msg)
                logging.error(error_msg)
    
    # Anomaly detection results
    st.subheader("Detection Results")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(label="Detected Anomalies", value="0", delta="0")
        st.metric(label="False Positives", value="0", delta="0")
    
    with col2:
        st.metric(label="Detection Rate", value="0%", delta="0%")
        st.metric(label="Average Response Time", value="0ms", delta="0ms")

# Network Statistics Tab
with tab3:
    st.header("Network Statistics")
    
    # Traffic patterns
    st.subheader("Traffic Patterns")
    monitor = get_network_monitor()
    metrics_history = monitor.metrics_history
    
    if metrics_history:
        df = pd.DataFrame(metrics_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        fig = px.line(df, x='timestamp', y='traffic_rate',
                     title='Network Traffic Over Time')
        st.plotly_chart(fig, use_container_width=True)
        
        # Protocol distribution
        st.subheader("Protocol Distribution")
        protocol_counts = {}
        for metrics in metrics_history:
            for protocol, connections in metrics['connections'].items():
                protocol_counts[protocol] = protocol_counts.get(protocol, 0) + len(connections)
        
        if protocol_counts:
            fig = px.pie(values=list(protocol_counts.values()),
                        names=list(protocol_counts.keys()),
                        title='Traffic Protocol Distribution')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No historical data available yet. Start monitoring to see statistics.")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>SDN Anomaly Detection System | Last updated: {}</p>
    </div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True) 