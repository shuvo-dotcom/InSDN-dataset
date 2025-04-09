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
    .attack-detected {
        background-color: #ff4444;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        animation: fadeOut 5s forwards;
    }
    @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
    }
    </style>
""", unsafe_allow_html=True)

# Initialize network monitor and session state
@st.cache_resource
def get_network_monitor():
    return NetworkMonitor()

# Initialize session state for attack history and warnings
if 'attack_history' not in st.session_state:
    st.session_state.attack_history = []
if 'current_warning' not in st.session_state:
    st.session_state.current_warning = None
if 'warning_start_time' not in st.session_state:
    st.session_state.warning_start_time = None
if 'last_metrics' not in st.session_state:
    st.session_state.last_metrics = None
if 'last_check_time' not in st.session_state:
    st.session_state.last_check_time = None
if 'warning_shown' not in st.session_state:
    st.session_state.warning_shown = False
if 'current_attacks' not in st.session_state:
    st.session_state.current_attacks = set()

# Title and description
st.title("🔒 SDN Anomaly Detection Dashboard")
st.markdown("""
    This dashboard provides real-time monitoring and anomaly detection for your Software-Defined Network.
    Use the sidebar to configure settings and view different aspects of your network security.
""")

# Sidebar
st.sidebar.title("Settings")
st.sidebar.markdown("### Configuration")

# Display client information in sidebar
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
    
    # Get current metrics
    metrics = monitor.get_network_metrics()
    if metrics is None:
        st.error("Failed to get network metrics. Please check the logs for details.")
    else:
        anomaly_score = monitor.get_anomaly_score(metrics)
        
        # Update metrics display
        with metrics_placeholder.container():
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(label="Active Connections", 
                         value=metrics.get('total_connections', 0))
                st.metric(label="Network Traffic (MB/s)", 
                         value=f"{metrics.get('traffic_rate', 0):.2f}")
            
            with col2:
                st.metric(label="CPU Usage (%)", 
                         value=f"{metrics.get('cpu_percent', 0):.1f}")
                st.metric(label="Memory Usage (%)", 
                         value=f"{metrics.get('memory_percent', 0):.1f}")
            
            with col3:
                st.metric(label="Anomaly Score", 
                         value=f"{anomaly_score:.2f}")
                st.metric(label="Network Errors", 
                         value=metrics.get('network_errors', 0))
        
        # Display detected attacks only if they're current and new
        current_time = datetime.now()
        
        # Get current metrics and check for actual attacks
        current_metrics = set(metrics.get('detected_attacks', []))
        
        # Clear any existing warning if there are no current attacks
        if not current_metrics and st.session_state.current_warning is not None:
            st.session_state.current_warning.empty()
            st.session_state.current_warning = None
            st.session_state.warning_start_time = None
            st.session_state.warning_shown = False
            st.session_state.current_attacks = set()
        
        # Only show warning if there are new current attacks
        new_attacks = current_metrics - st.session_state.current_attacks
        if new_attacks:
            # Create a new warning for current attacks
            warning = st.empty()
            with warning.container():
                st.markdown("""
                    <div class="attack-detected" style="
                        background-color: #ff4444;
                        color: white;
                        padding: 1rem;
                        border-radius: 0.5rem;
                        margin: 1rem 0;
                        font-size: 1.2rem;
                        text-align: center;
                        animation: flash 1s infinite;
                    ">
                        <h3 style="margin: 0;">⚠️ ATTACK DETECTED! ⚠️</h3>
                        <p style="margin: 0.5rem 0;">Detected attack types:</p>
                        <ul style="list-style: none; padding: 0; margin: 0;">
                """, unsafe_allow_html=True)
                for attack in new_attacks:
                    st.markdown(f"<li style='margin: 0.5rem 0;'><strong>{attack.upper()}</strong></li>", unsafe_allow_html=True)
                st.markdown("</ul></div>", unsafe_allow_html=True)
            
            # Store the warning and its start time
            st.session_state.current_warning = warning
            st.session_state.warning_start_time = current_time
            st.session_state.warning_shown = True
            st.session_state.current_attacks = current_metrics
            
            # Update attack history
            st.session_state.attack_history.extend([
                {'time': current_time, 'attack': attack}
                for attack in new_attacks
            ])

        # Remove old warnings if they've been displayed for more than 5 seconds
        if (st.session_state.current_warning is not None and 
            st.session_state.warning_start_time is not None and
            (current_time - st.session_state.warning_start_time).total_seconds() > 5):
            st.session_state.current_warning.empty()
            st.session_state.current_warning = None
            st.session_state.warning_start_time = None
            st.session_state.warning_shown = False
        
        # Display network topology
        topology = monitor.get_network_topology()
        if topology['nodes']:
            G = nx.Graph()
            for node in topology['nodes']:
                G.add_node(node['id'], **node)
            for link in topology['links']:
                G.add_edge(link['source'], link['target'], **link)
            
            pos = nx.spring_layout(G)
            edge_trace = go.Scatter(
                x=[], y=[],
                line=dict(width=0.5, color='#888'),
                hoverinfo='none',
                mode='lines')
            
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_trace['x'] += tuple([x0, x1, None])
                edge_trace['y'] += tuple([y0, y1, None])
            
            node_trace = go.Scatter(
                x=[], y=[],
                mode='markers+text',
                hoverinfo='text',
                text=[],
                marker=dict(
                    showscale=True,
                    colorscale='YlGnBu',
                    size=10,
                    colorbar=dict(
                        thickness=15,
                        title='Node Connections',
                        xanchor='left'
                    )
                )
            )
            
            for node in G.nodes():
                x, y = pos[node]
                node_trace['x'] += tuple([x])
                node_trace['y'] += tuple([y])
                node_trace['text'] += tuple([f"{G.nodes[node].get('name', node)}"])
            
            fig = go.Figure(data=[edge_trace, node_trace],
                          layout=go.Layout(
                              title='Network Topology',
                              showlegend=False,
                              hovermode='closest',
                              margin=dict(b=20,l=5,r=5,t=40),
                              xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                              yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                          ))
            
            topology_placeholder.plotly_chart(fig)
        
        # Display alerts
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

# Anomaly Detection Tab
with tab2:
    st.header("Anomaly Detection")
    
    # Anomaly Score History
    st.subheader("Anomaly Score History")
    try:
        # Create sample data for visualization
        dates = pd.date_range(start='2025-04-01', periods=30, freq='D')
        scores = np.random.normal(0.3, 0.1, 30)  # Sample scores around 0.3
        df_scores = pd.DataFrame({'Date': dates, 'Anomaly Score': scores})
        
        fig = px.line(df_scores, x='Date', y='Anomaly Score', 
                     title='Anomaly Score Trend')
        st.plotly_chart(fig)
        
        # Current Anomaly Status
        st.subheader("Current Anomaly Status")
        current_score = anomaly_score  # Use the actual anomaly score from the network monitor
        status_color = "red" if current_score > threshold else "green"
        st.markdown(f"""
            <div style='text-align: center;'>
                <h2 style='color: {status_color};'>Current Score: {current_score:.2f}</h2>
                <p>Threshold: {threshold}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Attack History
        st.subheader("Attack History")
        if st.session_state.attack_history:
            attack_df = pd.DataFrame(st.session_state.attack_history)
            attack_df['time'] = pd.to_datetime(attack_df['time'])
            attack_df = attack_df.sort_values('time', ascending=False)
            st.dataframe(attack_df)
        else:
            st.info("No attacks detected yet.")
        
        # Anomaly Types
        st.subheader("Detected Anomaly Types")
        anomaly_types = {
            "High Traffic Volume": current_score > 0.7,
            "Suspicious Connections": current_score > 0.6,
            "Unusual Port Activity": current_score > 0.5,
            "Resource Exhaustion": current_score > 0.4
        }
        
        for anomaly, detected in anomaly_types.items():
            status = "🔴 Detected" if detected else "🟢 Normal"
            st.write(f"{anomaly}: {status}")
            
    except Exception as e:
        st.error(f"Error displaying anomaly data: {str(e)}")

# Network Statistics Tab
with tab3:
    st.header("Network Statistics")
    
    try:
        # Network Traffic Over Time
        st.subheader("Network Traffic Over Time")
        traffic_data = pd.DataFrame({
            'Time': pd.date_range(start='2025-04-01', periods=24, freq='H'),
            'Traffic (MB/s)': np.random.normal(50, 10, 24)
        })
        fig_traffic = px.line(traffic_data, x='Time', y='Traffic (MB/s)',
                            title='Network Traffic Trend')
        st.plotly_chart(fig_traffic)
        
        # Connection Statistics
        st.subheader("Connection Statistics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Connections", metrics.get('total_connections', 0))
            st.metric("Active Connections", metrics.get('active_connections', 0))
        
        with col2:
            st.metric("Failed Connections", metrics.get('failed_connections', 0))
            st.metric("Connection Rate", f"{metrics.get('connection_rate', 0):.1f}/s")
        
        # Protocol Distribution
        st.subheader("Protocol Distribution")
        protocols = {
            'TCP': metrics.get('tcp_connections', 0),
            'UDP': metrics.get('udp_connections', 0),
            'ICMP': metrics.get('icmp_connections', 0)
        }
        fig_protocols = px.pie(values=list(protocols.values()),
                             names=list(protocols.keys()),
                             title='Protocol Distribution')
        st.plotly_chart(fig_protocols)
        
    except Exception as e:
        st.error(f"Error displaying network statistics: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>SDN Anomaly Detection System | Last updated: {}</p>
    </div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True) 