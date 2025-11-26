"""
LandGuard Network Analysis
Analyze ownership chains, relationships, and fraud networks
"""

import networkx as nx
from pyvis.network import Network
import pandas as pd
from typing import Dict, List, Tuple, Set, Optional
from pathlib import Path
import json
from collections import defaultdict, Counter
from datetime import datetime


class NetworkAnalyzer:
    """Analyze ownership networks and fraud relationships"""
    
    def __init__(self, output_dir: str = 'analytics/outputs/graphs'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.graph = nx.DiGraph()
        self.fraud_nodes = set()
        self.normal_nodes = set()
    
    def build_ownership_network(self, data_source: str = 'blockchain/storage'):
        """
        Build network graph from land records
        
        Args:
            data_source: Path to data directory
        """
        print("🕸️  Building ownership network...")
        
        evidence_dir = Path(data_source) / 'evidence'
        
        if not evidence_dir.exists():
            print("⚠️  No evidence data found")
            return
        
        edges_added = 0
        
        for file_path in evidence_dir.glob('*_complete.json'):
            try:
                with open(file_path, 'r') as f:
                    package = json.load(f)
                    evidence = package.get('evidence', {})
                    analysis = evidence.get('analysis_result', {})
                    
                    record_id = evidence.get('record_id')
                    is_fraud = analysis.get('is_fraudulent', False)
                    risk_score = analysis.get('risk_score', 0)
                    
                    # Extract ownership info (synthetic for demo)
                    # In production, extract from actual land records
                    owner = f"Owner_{hash(record_id) % 100}"
                    seller = f"Seller_{hash(record_id) % 50}"
                    property_id = f"Property_{hash(record_id) % 200}"
                    
                    # Add nodes
                    self.graph.add_node(
                        owner,
                        type='person',
                        is_fraud=is_fraud,
                        risk_score=risk_score
                    )
                    
                    self.graph.add_node(
                        seller,
                        type='person',
                        is_fraud=False
                    )
                    
                    self.graph.add_node(
                        property_id,
                        type='property',
                        record_id=record_id,
                        is_fraud=is_fraud,
                        risk_score=risk_score
                    )
                    
                    # Add edges
                    self.graph.add_edge(seller, property_id, relation='sold')
                    self.graph.add_edge(property_id, owner, relation='owned_by')
                    
                    edges_added += 2
                    
                    # Track fraud nodes
                    if is_fraud:
                        self.fraud_nodes.add(owner)
                        self.fraud_nodes.add(property_id)
                    else:
                        self.normal_nodes.add(owner)
                        self.normal_nodes.add(property_id)
            
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
        print(f"✅ Network built:")
        print(f"   Nodes: {self.graph.number_of_nodes()}")
        print(f"   Edges: {self.graph.number_of_edges()}")
        print(f"   Fraud nodes: {len(self.fraud_nodes)}")
    
    def find_fraud_clusters(self) -> List[Set]:
        """
        Identify clusters of connected fraud cases
        
        Returns:
            List of fraud clusters
        """
        print("\n🔍 Detecting fraud clusters...")
        
        # Create subgraph of fraud nodes
        fraud_subgraph = self.graph.subgraph(self.fraud_nodes)
        
        # Find connected components
        if fraud_subgraph.is_directed():
            components = list(nx.weakly_connected_components(fraud_subgraph))
        else:
            components = list(nx.connected_components(fraud_subgraph))
        
        # Filter significant clusters (size > 1)
        clusters = [c for c in components if len(c) > 1]
        
        print(f"✅ Found {len(clusters)} fraud clusters")
        
        for i, cluster in enumerate(clusters[:5], 1):
            print(f"   Cluster {i}: {len(cluster)} nodes")
        
        return clusters
    
    def calculate_centrality_metrics(self) -> Dict[str, Dict]:
        """
        Calculate network centrality metrics
        
        Returns:
            Dictionary of centrality scores
        """
        print("\n📊 Calculating centrality metrics...")
        
        metrics = {}
        
        # Degree centrality
        degree_cent = nx.degree_centrality(self.graph)
        top_degree = sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)[:5]
        metrics['degree_centrality'] = {
            'top_nodes': [{'node': n, 'score': float(s)} for n, s in top_degree],
            'description': 'Nodes with most connections'
        }
        
        # Betweenness centrality
        between_cent = nx.betweenness_centrality(self.graph)
        top_between = sorted(between_cent.items(), key=lambda x: x[1], reverse=True)[:5]
        metrics['betweenness_centrality'] = {
            'top_nodes': [{'node': n, 'score': float(s)} for n, s in top_between],
            'description': 'Nodes acting as bridges'
        }
        
        # PageRank
        pagerank = nx.pagerank(self.graph)
        top_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:5]
        metrics['pagerank'] = {
            'top_nodes': [{'node': n, 'score': float(s)} for n, s in top_pagerank],
            'description': 'Most influential nodes'
        }
        
        print("✅ Centrality metrics calculated")
        
        return metrics
    
    def detect_suspicious_patterns(self) -> Dict[str, List]:
        """
        Detect suspicious patterns in the network
        
        Returns:
            Dictionary of suspicious patterns
        """
        print("\n🚨 Detecting suspicious patterns...")
        
        patterns = {
            'circular_ownership': [],
            'rapid_transfers': [],
            'high_risk_connections': [],
            'isolated_fraud': []
        }
        
        # Pattern 1: Circular ownership (cycles)
        try:
            cycles = list(nx.simple_cycles(self.graph))
            for cycle in cycles[:10]:  # Limit to first 10
                if any(node in self.fraud_nodes for node in cycle):
                    patterns['circular_ownership'].append(cycle)
        except:
            pass
        
        # Pattern 2: High-risk connections
        for node in self.fraud_nodes:
            neighbors = list(self.graph.neighbors(node))
            fraud_neighbors = [n for n in neighbors if n in self.fraud_nodes]
            
            if len(fraud_neighbors) >= 2:
                patterns['high_risk_connections'].append({
                    'node': node,
                    'fraud_connections': len(fraud_neighbors),
                    'connected_to': fraud_neighbors[:3]
                })
        
        # Pattern 3: Isolated fraud (no connections to other fraud)
        for node in self.fraud_nodes:
            neighbors = set(self.graph.neighbors(node)) | set(self.graph.predecessors(node))
            if not neighbors.intersection(self.fraud_nodes):
                patterns['isolated_fraud'].append(node)
        
        print(f"✅ Patterns detected:")
        print(f"   Circular ownership: {len(patterns['circular_ownership'])}")
        print(f"   High-risk connections: {len(patterns['high_risk_connections'])}")
        print(f"   Isolated fraud: {len(patterns['isolated_fraud'])}")
        
        return patterns
    
    def visualize_network(self, 
                         output_name: str = 'ownership_network.html',
                         max_nodes: int = 100) -> str:
        """
        Create interactive network visualization
        
        Args:
            output_name: Output filename
            max_nodes: Maximum nodes to display
        
        Returns:
            Path to generated HTML
        """
        print(f"\n🎨 Creating network visualization...")
        
        if self.graph.number_of_nodes() == 0:
            print("⚠️  No network data to visualize")
            return None
        
        # Limit nodes for performance
        if self.graph.number_of_nodes() > max_nodes:
            # Sample most important nodes
            pagerank = nx.pagerank(self.graph)
            top_nodes = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:max_nodes]
            subgraph = self.graph.subgraph([n for n, _ in top_nodes])
        else:
            subgraph = self.graph
        
        # Create pyvis network
        net = Network(
            height='750px',
            width='100%',
            bgcolor='#222222',
            font_color='white',
            directed=True
        )
        
        net.barnes_hut()
        
        # Add nodes with colors
        for node in subgraph.nodes():
            node_data = subgraph.nodes[node]
            
            if node in self.fraud_nodes:
                color = '#ff4444'  # Red for fraud
                size = 25
            else:
                color = '#44ff44'  # Green for normal
                size = 15
            
            title = f"{node}<br>Type: {node_data.get('type', 'unknown')}"
            if 'risk_score' in node_data:
                title += f"<br>Risk: {node_data['risk_score']:.1f}"
            
            net.add_node(
                node,
                label=node,
                color=color,
                size=size,
                title=title
            )
        
        # Add edges
        for edge in subgraph.edges():
            edge_data = subgraph.edges[edge]
            net.add_edge(
                edge[0],
                edge[1],
                title=edge_data.get('relation', 'connected'),
                color='#999999'
            )
        
        # Save
        output_path = self.output_dir / output_name
        net.save_graph(str(output_path))
        
        print(f"✅ Network visualization saved: {output_path}")
        
        return str(output_path)
    
    def visualize_fraud_cluster(self,
                               cluster: Set,
                               output_name: str = 'fraud_cluster.html') -> str:
        """
        Visualize a specific fraud cluster
        
        Args:
            cluster: Set of nodes in cluster
            output_name: Output filename
        
        Returns:
            Path to generated HTML
        """
        if not cluster:
            return None
        
        print(f"\n🎨 Visualizing fraud cluster ({len(cluster)} nodes)...")
        
        # Create subgraph
        subgraph = self.graph.subgraph(cluster)
        
        # Create pyvis network
        net = Network(height='600px', width='100%', bgcolor='#222222', font_color='white')
        net.barnes_hut()
        
        # Add nodes
        for node in subgraph.nodes():
            node_data = subgraph.nodes[node]
            
            net.add_node(
                node,
                label=node,
                color='#ff4444',
                size=20,
                title=f"{node}<br>Risk: {node_data.get('risk_score', 0):.1f}"
            )
        
        # Add edges
        for edge in subgraph.edges():
            net.add_edge(edge[0], edge[1], color='#ff9999')
        
        # Save
        output_path = self.output_dir / output_name
        net.save_graph(str(output_path))
        
        print(f"✅ Cluster visualization saved: {output_path}")
        
        return str(output_path)
    
    def generate_network_report(self, data_source: str = 'blockchain/storage') -> Dict:
        """
        Generate comprehensive network analysis report
        
        Args:
            data_source: Path to data directory
        
        Returns:
            Network analysis report
        """
        print("🕸️  Generating Network Analysis Report...\n")
        
        # Build network
        self.build_ownership_network(data_source)
        
        if self.graph.number_of_nodes() == 0:
            return {'error': 'No network data available'}
        
        # Perform analyses
        clusters = self.find_fraud_clusters()
        centrality = self.calculate_centrality_metrics()
        patterns = self.detect_suspicious_patterns()
        
        # Generate visualizations
        self.visualize_network()
        
        if clusters:
            self.visualize_fraud_cluster(clusters[0], 'largest_fraud_cluster.html')
        
        # Compile report
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'network_statistics': {
                'total_nodes': self.graph.number_of_nodes(),
                'total_edges': self.graph.number_of_edges(),
                'fraud_nodes': len(self.fraud_nodes),
                'normal_nodes': len(self.normal_nodes),
                'avg_degree': sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes(),
                'density': nx.density(self.graph)
            },
            'fraud_clusters': {
                'num_clusters': len(clusters),
                'cluster_sizes': [len(c) for c in clusters]
            },
            'centrality_metrics': centrality,
            'suspicious_patterns': {
                k: len(v) if isinstance(v, list) else v 
                for k, v in patterns.items()
            }
        }
        
        # Save report
        report_path = self.output_dir / 'network_analysis_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✅ Network analysis complete!")
        print(f"📄 Report saved: {report_path}")
        
        return report


# Example usage
if __name__ == "__main__":
    print("🕸️ LandGuard Network Analysis Demo\n")
    
    # Initialize analyzer
    analyzer = NetworkAnalyzer()
    
    # Generate comprehensive report
    report = analyzer.generate_network_report('blockchain/storage')
    
    # Print summary
    print("\n" + "="*70)
    print("🕸️  NETWORK ANALYSIS SUMMARY")
    print("="*70)
    
    stats = report['network_statistics']
    print(f"\n📊 Network Statistics:")
    print(f"   Total Nodes: {stats['total_nodes']}")
    print(f"   Total Edges: {stats['total_edges']}")
    print(f"   Fraud Nodes: {stats['fraud_nodes']}")
    print(f"   Network Density: {stats['density']:.4f}")
    
    clusters = report['fraud_clusters']
    print(f"\n🔍 Fraud Clusters:")
    print(f"   Clusters Found: {clusters['num_clusters']}")
    if clusters['cluster_sizes']:
        print(f"   Largest Cluster: {max(clusters['cluster_sizes'])} nodes")
    
    patterns = report['suspicious_patterns']
    print(f"\n🚨 Suspicious Patterns:")
    for pattern_type, count in patterns.items():
        print(f"   {pattern_type}: {count}")
    
    print("\n" + "="*70)
    print("\n✅ Network Analysis Complete!")