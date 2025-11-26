"""
LandGuard Geographic Analysis
Create interactive maps and heatmaps of fraud patterns
"""

import folium
from folium.plugins import HeatMap, MarkerCluster
import pandas as pd
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import json
from datetime import datetime


class GeoMapper:
    """Create geographic visualizations of fraud patterns"""
    
    def __init__(self, output_dir: str = 'analytics/outputs/maps'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Default center (India)
        self.default_center = [20.5937, 78.9629]
        self.default_zoom = 5
    
    def load_geo_data(self, data_source: str = 'blockchain/storage') -> pd.DataFrame:
        """
        Load fraud cases with geographic coordinates
        
        Args:
            data_source: Path to data directory
        
        Returns:
            DataFrame with geographic data
        """
        # For demo purposes, generate synthetic coordinates
        # In production, extract from land records
        
        evidence_dir = Path(data_source) / 'evidence'
        
        if not evidence_dir.exists():
            return pd.DataFrame()
        
        cases = []
        
        for file_path in evidence_dir.glob('*_complete.json'):
            try:
                with open(file_path, 'r') as f:
                    package = json.load(f)
                    evidence = package.get('evidence', {})
                    analysis = evidence.get('analysis_result', {})
                    
                    # Generate synthetic coordinates (replace with actual data)
                    # India lat: 8-35, lon: 68-97
                    import random
                    lat = random.uniform(8, 35)
                    lon = random.uniform(68, 97)
                    
                    case = {
                        'record_id': evidence.get('record_id'),
                        'latitude': lat,
                        'longitude': lon,
                        'is_fraudulent': analysis.get('is_fraudulent', False),
                        'risk_score': analysis.get('risk_score', 0),
                        'timestamp': evidence.get('timestamp'),
                        # Add location info if available
                        'city': 'Unknown',  # Extract from records
                        'state': 'Unknown',  # Extract from records
                        'district': 'Unknown'  # Extract from records
                    }
                    
                    cases.append(case)
            
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                continue
        
        return pd.DataFrame(cases)
    
    def create_fraud_heatmap(self, 
                            df: pd.DataFrame,
                            output_name: str = 'fraud_heatmap.html') -> str:
        """
        Create heatmap showing fraud concentration
        
        Args:
            df: DataFrame with latitude, longitude, risk_score
            output_name: Output filename
        
        Returns:
            Path to generated HTML map
        """
        if df.empty or 'latitude' not in df.columns:
            print("⚠️  No geographic data available")
            return None
        
        print(f"🗺️  Creating fraud heatmap...")
        
        # Filter fraud cases
        fraud_df = df[df['is_fraudulent'] == True].copy()
        
        if fraud_df.empty:
            print("⚠️  No fraud cases with coordinates")
            return None
        
        # Create base map
        center_lat = fraud_df['latitude'].mean()
        center_lon = fraud_df['longitude'].mean()
        
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=6,
            tiles='OpenStreetMap'
        )
        
        # Prepare heatmap data
        heat_data = [
            [row['latitude'], row['longitude'], row['risk_score']/100] 
            for _, row in fraud_df.iterrows()
        ]
        
        # Add heatmap layer
        HeatMap(
            heat_data,
            radius=15,
            blur=25,
            max_zoom=13,
            gradient={
                0.0: 'blue',
                0.5: 'yellow',
                0.75: 'orange',
                1.0: 'red'
            }
        ).add_to(m)
        
        # Add title
        title_html = '''
        <div style="position: fixed; 
                    top: 10px; left: 50px; width: 300px; height: 90px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:16px; padding: 10px">
        <b>🗺️ LandGuard Fraud Heatmap</b><br>
        Fraud Cases: {}<br>
        Avg Risk Score: {:.1f}
        </div>
        '''.format(len(fraud_df), fraud_df['risk_score'].mean())
        
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Save map
        output_path = self.output_dir / output_name
        m.save(str(output_path))
        
        print(f"✅ Heatmap saved: {output_path}")
        
        return str(output_path)
    
    def create_cluster_map(self,
                          df: pd.DataFrame,
                          output_name: str = 'fraud_clusters.html') -> str:
        """
        Create clustered marker map
        
        Args:
            df: DataFrame with geographic data
            output_name: Output filename
        
        Returns:
            Path to generated HTML map
        """
        if df.empty or 'latitude' not in df.columns:
            print("⚠️  No geographic data available")
            return None
        
        print(f"🗺️  Creating cluster map...")
        
        # Create base map
        center_lat = df['latitude'].mean()
        center_lon = df['longitude'].mean()
        
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=6,
            tiles='CartoDB positron'
        )
        
        # Create marker cluster
        marker_cluster = MarkerCluster().add_to(m)
        
        # Add markers
        for _, row in df.iterrows():
            # Determine marker color
            if row['is_fraudulent']:
                color = 'red' if row['risk_score'] > 70 else 'orange'
                icon = 'exclamation-triangle'
            else:
                color = 'green'
                icon = 'check'
            
            # Create popup
            popup_html = f"""
            <div style="font-family: Arial; font-size: 12px;">
                <b>Record:</b> {row['record_id']}<br>
                <b>Status:</b> {'🚨 FRAUD' if row['is_fraudulent'] else '✅ Normal'}<br>
                <b>Risk Score:</b> {row['risk_score']:.1f}/100<br>
                <b>Location:</b> {row.get('city', 'Unknown')}<br>
                <b>Date:</b> {row.get('timestamp', 'Unknown')[:10]}
            </div>
            """
            
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_html, max_width=250),
                icon=folium.Icon(color=color, icon=icon, prefix='fa')
            ).add_to(marker_cluster)
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 130px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <b>Legend</b><br>
        🔴 Critical Fraud (>70)<br>
        🟠 High Risk (50-70)<br>
        🟢 Normal<br>
        <br>
        <b>Total Cases:</b> {}
        </div>
        '''.format(len(df))
        
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Save map
        output_path = self.output_dir / output_name
        m.save(str(output_path))
        
        print(f"✅ Cluster map saved: {output_path}")
        
        return str(output_path)
    
    def create_state_choropleth(self,
                               df: pd.DataFrame,
                               output_name: str = 'state_fraud_rates.html') -> str:
        """
        Create choropleth map showing fraud rates by state
        
        Args:
            df: DataFrame with state information
            output_name: Output filename
        
        Returns:
            Path to generated HTML map
        """
        if df.empty or 'state' not in df.columns:
            print("⚠️  No state data available")
            return None
        
        print(f"🗺️  Creating state choropleth...")
        
        # Calculate fraud rate by state
        state_stats = df.groupby('state').agg({
            'is_fraudulent': ['sum', 'count', 'mean']
        }).reset_index()
        
        state_stats.columns = ['state', 'fraud_count', 'total_count', 'fraud_rate']
        state_stats['fraud_rate_pct'] = state_stats['fraud_rate'] * 100
        
        # Create map
        m = folium.Map(
            location=self.default_center,
            zoom_start=5,
            tiles='CartoDB positron'
        )
        
        # Add state markers (simplified - in production use GeoJSON)
        for _, row in state_stats.iterrows():
            # This is simplified - use actual state boundaries in production
            popup_html = f"""
            <b>{row['state']}</b><br>
            Fraud Rate: {row['fraud_rate_pct']:.1f}%<br>
            Fraud Cases: {row['fraud_count']:.0f}<br>
            Total Cases: {row['total_count']:.0f}
            """
            
            # Add circle marker sized by fraud rate
            folium.CircleMarker(
                location=self.default_center,  # Replace with state center
                radius=row['fraud_rate_pct'],
                popup=popup_html,
                color='red',
                fill=True,
                fillColor='red',
                fillOpacity=0.6
            ).add_to(m)
        
        # Save map
        output_path = self.output_dir / output_name
        m.save(str(output_path))
        
        print(f"✅ State choropleth saved: {output_path}")
        
        return str(output_path)
    
    def create_time_animation_map(self,
                                  df: pd.DataFrame,
                                  output_name: str = 'fraud_timeline.html') -> str:
        """
        Create map showing fraud cases over time
        
        Args:
            df: DataFrame with timestamp data
            output_name: Output filename
        
        Returns:
            Path to generated HTML map
        """
        if df.empty or 'timestamp' not in df.columns:
            print("⚠️  No temporal data available")
            return None
        
        print(f"🗺️  Creating timeline map...")
        
        # Sort by timestamp
        df_sorted = df.sort_values('timestamp')
        
        # Create map
        m = folium.Map(
            location=[df['latitude'].mean(), df['longitude'].mean()],
            zoom_start=6,
            tiles='OpenStreetMap'
        )
        
        # Group by month
        df_sorted['year_month'] = pd.to_datetime(df_sorted['timestamp']).dt.to_period('M')
        
        for period in df_sorted['year_month'].unique():
            period_df = df_sorted[df_sorted['year_month'] == period]
            fraud_period = period_df[period_df['is_fraudulent'] == True]
            
            if not fraud_period.empty:
                # Add markers for this period
                for _, row in fraud_period.iterrows():
                    folium.CircleMarker(
                        location=[row['latitude'], row['longitude']],
                        radius=5,
                        popup=f"{row['record_id']}<br>{period}",
                        color='red',
                        fill=True
                    ).add_to(m)
        
        # Save map
        output_path = self.output_dir / output_name
        m.save(str(output_path))
        
        print(f"✅ Timeline map saved: {output_path}")
        
        return str(output_path)
    
    def generate_geo_report(self, data_source: str = 'blockchain/storage') -> Dict[str, str]:
        """
        Generate all geographic visualizations
        
        Args:
            data_source: Path to data directory
        
        Returns:
            Dictionary with paths to generated maps
        """
        print("🗺️  Generating Geographic Analysis...\n")
        
        # Load data
        df = self.load_geo_data(data_source)
        
        if df.empty:
            print("⚠️  No data available for geographic analysis")
            return {}
        
        print(f"✅ Loaded {len(df)} cases with coordinates\n")
        
        # Generate all maps
        maps = {}
        
        maps['heatmap'] = self.create_fraud_heatmap(df)
        maps['clusters'] = self.create_cluster_map(df)
        maps['states'] = self.create_state_choropleth(df)
        maps['timeline'] = self.create_time_animation_map(df)
        
        print(f"\n✅ Generated {len([v for v in maps.values() if v])} maps")
        
        return maps


# Example usage
if __name__ == "__main__":
    print("🗺️ LandGuard Geographic Analysis Demo\n")
    
    # Initialize mapper
    mapper = GeoMapper()
    
    # Generate all maps
    maps = mapper.generate_geo_report('blockchain/storage')
    
    print("\n📁 Generated Maps:")
    for map_type, path in maps.items():
        if path:
            print(f"   {map_type}: {path}")
    
    print("\n✅ Geographic Analysis Complete!")
    print("💡 Open the HTML files in a web browser to view interactive maps")