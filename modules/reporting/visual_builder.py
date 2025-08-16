#!/usr/bin/env python3
"""
Visual Builder Module - Pentest USB Toolkit

This module implements comprehensive visualization capabilities including
chart and graph generation, network topology visualization, attack path mapping,
and interactive dashboards.

Author: Pentest USB Team
Version: 1.0.0
"""

import os
import sys
import json
import logging
import base64
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import time

# Internal imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from core.utils.logging_handler import setup_logger
from core.utils.error_handler import handle_error


class ChartType(Enum):
    """Supported chart types."""
    PIE = "pie"
    BAR = "bar"
    LINE = "line"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"
    HEATMAP = "heatmap"
    NETWORK_GRAPH = "network_graph"
    TREEMAP = "treemap"


class ColorScheme(Enum):
    """Color schemes for visualizations."""
    SECURITY = "security"  # Red/Yellow/Green
    CORPORATE = "corporate"  # Blue/Gray theme
    DARK = "dark"  # Dark theme
    ACCESSIBILITY = "accessibility"  # High contrast
    RAINBOW = "rainbow"  # Multiple colors


@dataclass
class ChartConfiguration:
    """Configuration for chart generation."""
    chart_type: ChartType
    title: str
    width: int = 800
    height: int = 600
    color_scheme: ColorScheme = ColorScheme.SECURITY
    show_legend: bool = True
    show_labels: bool = True
    interactive: bool = True


@dataclass
class VisualizationResult:
    """Result of visualization generation."""
    chart_id: str
    chart_type: str
    output_path: str
    html_embed: str
    success: bool
    error: Optional[str] = None
    generation_time: float = 0.0


class VisualBuilder:
    """Main class for visualization generation."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = setup_logger(__name__)
        
        # Output directory for generated visualizations
        self.output_dir = Path(self.config.get('output_dir', 
                                              Path(__file__).parent.parent.parent / "reports" / "visualizations"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Color schemes
        self.color_schemes = self._load_color_schemes()
        
        # Chart templates
        self.chart_templates = self._load_chart_templates()
        
        self.logger.info("Initialized VisualBuilder")

    def _load_color_schemes(self) -> Dict[str, Dict[str, Any]]:
        """Load color schemes for different visualization types."""
        return {
            ColorScheme.SECURITY.value: {
                'critical': '#8B0000',    # Dark Red
                'high': '#FF4500',        # Orange Red
                'medium': '#FFD700',      # Gold
                'low': '#90EE90',         # Light Green
                'info': '#87CEEB',        # Sky Blue
                'background': '#F8F9FA',  # Light Gray
                'text': '#212529'         # Dark Gray
            },
            ColorScheme.CORPORATE.value: {
                'primary': '#0066CC',     # Corporate Blue
                'secondary': '#6C757D',   # Gray
                'success': '#28A745',     # Green
                'warning': '#FFC107',     # Yellow
                'danger': '#DC3545',      # Red
                'background': '#FFFFFF',  # White
                'text': '#343A40'         # Dark
            },
            ColorScheme.DARK.value: {
                'primary': '#007BFF',     # Bright Blue
                'secondary': '#6C757D',   # Gray
                'success': '#28A745',     # Green
                'warning': '#FFC107',     # Yellow
                'danger': '#DC3545',      # Red
                'background': '#343A40',  # Dark Gray
                'text': '#F8F9FA'         # Light Gray
            }
        }

    def _load_chart_templates(self) -> Dict[str, str]:
        """Load HTML/CSS/JS templates for different chart types."""
        return {
            'base_html': '''
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: {bg_color}; color: {text_color}; }}
        .chart-container {{ width: 100%; height: {height}px; }}
        .chart-title {{ text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="chart-title">{title}</div>
    <div id="{chart_id}" class="chart-container"></div>
    <script>
        {chart_script}
    </script>
</body>
</html>
            ''',
            'pie_chart': '''
var data = [{
    values: {values},
    labels: {labels},
    type: 'pie',
    marker: {{
        colors: {colors}
    }},
    textinfo: 'label+percent',
    textposition: 'outside'
}];

var layout = {{
    title: '',
    showlegend: {show_legend},
    paper_bgcolor: '{bg_color}',
    plot_bgcolor: '{bg_color}',
    font: {{ color: '{text_color}' }}
}};

Plotly.newPlot('{chart_id}', data, layout, {{responsive: true}});
            ''',
            'bar_chart': '''
var data = [{
    x: {labels},
    y: {values},
    type: 'bar',
    marker: {{
        color: {colors}
    }}
}];

var layout = {{
    title: '',
    xaxis: {{ title: '{x_title}' }},
    yaxis: {{ title: '{y_title}' }},
    paper_bgcolor: '{bg_color}',
    plot_bgcolor: '{bg_color}',
    font: {{ color: '{text_color}' }}
}};

Plotly.newPlot('{chart_id}', data, layout, {{responsive: true}});
            '''
        }

    @handle_error
    def create_vulnerability_severity_chart(self, vulnerability_data: Dict[str, Any],
                                           config: ChartConfiguration = None) -> VisualizationResult:
        """Create a chart showing vulnerability severity distribution."""
        if config is None:
            config = ChartConfiguration(
                chart_type=ChartType.PIE,
                title="Vulnerability Severity Distribution"
            )
        
        start_time = time.time()
        chart_id = f"vuln_severity_{int(time.time())}"
        
        try:
            # Extract severity data
            severity_dist = vulnerability_data.get('severity_distribution', {})
            counts = severity_dist.get('counts', {})
            
            if not counts:
                return VisualizationResult(
                    chart_id=chart_id,
                    chart_type=config.chart_type.value,
                    output_path="",
                    html_embed="",
                    success=False,
                    error="No vulnerability data available"
                )
            
            # Prepare data for chart
            labels = list(counts.keys())
            values = list(counts.values())
            colors = [self._get_severity_color(label, config.color_scheme) for label in labels]
            
            # Generate chart
            if config.chart_type == ChartType.PIE:
                result = self._create_pie_chart(chart_id, config, labels, values, colors)
            elif config.chart_type == ChartType.BAR:
                result = self._create_bar_chart(chart_id, config, labels, values, colors)
            else:
                return VisualizationResult(
                    chart_id=chart_id,
                    chart_type=config.chart_type.value,
                    output_path="",
                    html_embed="",
                    success=False,
                    error=f"Chart type {config.chart_type.value} not supported for severity distribution"
                )
            
            result.generation_time = time.time() - start_time
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating vulnerability severity chart: {e}")
            return VisualizationResult(
                chart_id=chart_id,
                chart_type=config.chart_type.value,
                output_path="",
                html_embed="",
                success=False,
                error=str(e),
                generation_time=time.time() - start_time
            )

    @handle_error
    def create_risk_score_timeline(self, timeline_data: List[Dict[str, Any]],
                                 config: ChartConfiguration = None) -> VisualizationResult:
        """Create a timeline chart showing risk score evolution."""
        if config is None:
            config = ChartConfiguration(
                chart_type=ChartType.LINE,
                title="Risk Score Timeline"
            )
        
        start_time = time.time()
        chart_id = f"risk_timeline_{int(time.time())}"
        
        try:
            if not timeline_data:
                return VisualizationResult(
                    chart_id=chart_id,
                    chart_type=config.chart_type.value,
                    output_path="",
                    html_embed="",
                    success=False,
                    error="No timeline data available"
                )
            
            # Extract timeline data
            dates = [item['date'] for item in timeline_data]
            scores = [item['risk_score'] for item in timeline_data]
            
            # Create line chart
            result = self._create_line_chart(chart_id, config, dates, scores)
            result.generation_time = time.time() - start_time
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating risk timeline chart: {e}")
            return VisualizationResult(
                chart_id=chart_id,
                chart_type=config.chart_type.value,
                output_path="",
                html_embed="",
                success=False,
                error=str(e),
                generation_time=time.time() - start_time
            )

    @handle_error
    def create_network_topology_map(self, network_data: Dict[str, Any],
                                  config: ChartConfiguration = None) -> VisualizationResult:
        """Create a network topology visualization."""
        if config is None:
            config = ChartConfiguration(
                chart_type=ChartType.NETWORK_GRAPH,
                title="Network Topology",
                width=1000,
                height=800
            )
        
        start_time = time.time()
        chart_id = f"network_topology_{int(time.time())}"
        
        try:
            hosts = network_data.get('hosts', [])
            connections = network_data.get('connections', [])
            
            if not hosts:
                return VisualizationResult(
                    chart_id=chart_id,
                    chart_type=config.chart_type.value,
                    output_path="",
                    html_embed="",
                    success=False,
                    error="No network topology data available"
                )
            
            # Create network graph
            result = self._create_network_graph(chart_id, config, hosts, connections)
            result.generation_time = time.time() - start_time
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating network topology map: {e}")
            return VisualizationResult(
                chart_id=chart_id,
                chart_type=config.chart_type.value,
                output_path="",
                html_embed="",
                success=False,
                error=str(e),
                generation_time=time.time() - start_time
            )

    @handle_error
    def create_attack_path_visualization(self, attack_data: Dict[str, Any],
                                       config: ChartConfiguration = None) -> VisualizationResult:
        """Create an attack path visualization."""
        if config is None:
            config = ChartConfiguration(
                chart_type=ChartType.NETWORK_GRAPH,
                title="Attack Path Analysis",
                width=1200,
                height=800
            )
        
        start_time = time.time()
        chart_id = f"attack_path_{int(time.time())}"
        
        try:
            # Extract attack path data
            attack_steps = attack_data.get('attack_steps', [])
            
            if not attack_steps:
                return VisualizationResult(
                    chart_id=chart_id,
                    chart_type=config.chart_type.value,
                    output_path="",
                    html_embed="",
                    success=False,
                    error="No attack path data available"
                )
            
            # Create attack path visualization
            result = self._create_attack_path_graph(chart_id, config, attack_steps)
            result.generation_time = time.time() - start_time
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating attack path visualization: {e}")
            return VisualizationResult(
                chart_id=chart_id,
                chart_type=config.chart_type.value,
                output_path="",
                html_embed="",
                success=False,
                error=str(e),
                generation_time=time.time() - start_time
            )

    def _get_severity_color(self, severity: str, color_scheme: ColorScheme) -> str:
        """Get color for a specific severity level."""
        scheme = self.color_schemes.get(color_scheme.value, self.color_schemes[ColorScheme.SECURITY.value])
        return scheme.get(severity.lower(), scheme.get('info', '#87CEEB'))

    def _create_pie_chart(self, chart_id: str, config: ChartConfiguration,
                         labels: List[str], values: List[int], colors: List[str]) -> VisualizationResult:
        """Create a pie chart."""
        color_scheme = self.color_schemes.get(config.color_scheme.value, 
                                            self.color_schemes[ColorScheme.SECURITY.value])
        
        chart_script = self.chart_templates['pie_chart'].format(
            chart_id=chart_id,
            values=json.dumps(values),
            labels=json.dumps(labels),
            colors=json.dumps(colors),
            show_legend='true' if config.show_legend else 'false',
            bg_color=color_scheme['background'],
            text_color=color_scheme['text']
        )
        
        html_content = self.chart_templates['base_html'].format(
            title=config.title,
            chart_id=chart_id,
            height=config.height,
            bg_color=color_scheme['background'],
            text_color=color_scheme['text'],
            chart_script=chart_script
        )
        
        # Save HTML file
        output_file = self.output_dir / f"{chart_id}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return VisualizationResult(
            chart_id=chart_id,
            chart_type=config.chart_type.value,
            output_path=str(output_file),
            html_embed=html_content,
            success=True
        )

    def _create_bar_chart(self, chart_id: str, config: ChartConfiguration,
                         labels: List[str], values: List[int], colors: List[str]) -> VisualizationResult:
        """Create a bar chart."""
        color_scheme = self.color_schemes.get(config.color_scheme.value, 
                                            self.color_schemes[ColorScheme.SECURITY.value])
        
        chart_script = self.chart_templates['bar_chart'].format(
            chart_id=chart_id,
            labels=json.dumps(labels),
            values=json.dumps(values),
            colors=json.dumps(colors),
            x_title="Severity",
            y_title="Count",
            bg_color=color_scheme['background'],
            text_color=color_scheme['text']
        )
        
        html_content = self.chart_templates['base_html'].format(
            title=config.title,
            chart_id=chart_id,
            height=config.height,
            bg_color=color_scheme['background'],
            text_color=color_scheme['text'],
            chart_script=chart_script
        )
        
        # Save HTML file
        output_file = self.output_dir / f"{chart_id}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return VisualizationResult(
            chart_id=chart_id,
            chart_type=config.chart_type.value,
            output_path=str(output_file),
            html_embed=html_content,
            success=True
        )

    def _create_line_chart(self, chart_id: str, config: ChartConfiguration,
                          x_data: List[Any], y_data: List[Any]) -> VisualizationResult:
        """Create a line chart."""
        color_scheme = self.color_schemes.get(config.color_scheme.value, 
                                            self.color_schemes[ColorScheme.SECURITY.value])
        
        chart_script = f'''
var data = [{{
    x: {json.dumps(x_data)},
    y: {json.dumps(y_data)},
    type: 'scatter',
    mode: 'lines+markers',
    line: {{ color: '{color_scheme["primary"]}', width: 3 }},
    marker: {{ color: '{color_scheme["primary"]}', size: 8 }}
}}];

var layout = {{
    title: '',
    xaxis: {{ title: 'Date' }},
    yaxis: {{ title: 'Risk Score' }},
    paper_bgcolor: '{color_scheme["background"]}',
    plot_bgcolor: '{color_scheme["background"]}',
    font: {{ color: '{color_scheme["text"]}' }}
}};

Plotly.newPlot('{chart_id}', data, layout, {{responsive: true}});
        '''
        
        html_content = self.chart_templates['base_html'].format(
            title=config.title,
            chart_id=chart_id,
            height=config.height,
            bg_color=color_scheme['background'],
            text_color=color_scheme['text'],
            chart_script=chart_script
        )
        
        # Save HTML file
        output_file = self.output_dir / f"{chart_id}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return VisualizationResult(
            chart_id=chart_id,
            chart_type=config.chart_type.value,
            output_path=str(output_file),
            html_embed=html_content,
            success=True
        )

    def _create_network_graph(self, chart_id: str, config: ChartConfiguration,
                            hosts: List[Dict[str, Any]], connections: List[Dict[str, Any]]) -> VisualizationResult:
        """Create a network topology graph."""
        # Simplified network graph - in practice, you'd use a more sophisticated graph library
        color_scheme = self.color_schemes.get(config.color_scheme.value, 
                                            self.color_schemes[ColorScheme.SECURITY.value])
        
        # Prepare nodes and edges for visualization
        nodes = []
        for i, host in enumerate(hosts):
            nodes.append({
                'id': i,
                'label': host.get('ip', f'Host-{i}'),
                'color': self._get_host_color(host, color_scheme)
            })
        
        chart_script = f'''
// Network graph placeholder - would use D3.js or similar in production
var networkDiv = document.getElementById('{chart_id}');
networkDiv.innerHTML = '<div style="text-align: center; padding: 50px; color: {color_scheme["text"]};">' +
    '<h3>Network Topology</h3>' +
    '<p>Hosts discovered: {len(hosts)}</p>' +
    '<p>Connections: {len(connections)}</p>' +
    '<p>Interactive network graph would be displayed here</p>' +
    '</div>';
        '''
        
        html_content = self.chart_templates['base_html'].format(
            title=config.title,
            chart_id=chart_id,
            height=config.height,
            bg_color=color_scheme['background'],
            text_color=color_scheme['text'],
            chart_script=chart_script
        )
        
        # Save HTML file
        output_file = self.output_dir / f"{chart_id}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return VisualizationResult(
            chart_id=chart_id,
            chart_type=config.chart_type.value,
            output_path=str(output_file),
            html_embed=html_content,
            success=True
        )

    def _get_host_color(self, host: Dict[str, Any], color_scheme: Dict[str, str]) -> str:
        """Determine color for host based on its characteristics."""
        # Color hosts based on vulnerability count or other factors
        vuln_count = host.get('vulnerability_count', 0)
        
        if vuln_count > 10:
            return color_scheme.get('danger', '#DC3545')
        elif vuln_count > 5:
            return color_scheme.get('warning', '#FFC107')
        elif vuln_count > 0:
            return color_scheme.get('secondary', '#6C757D')
        else:
            return color_scheme.get('success', '#28A745')

    def _create_attack_path_graph(self, chart_id: str, config: ChartConfiguration,
                                attack_steps: List[Dict[str, Any]]) -> VisualizationResult:
        """Create an attack path visualization."""
        color_scheme = self.color_schemes.get(config.color_scheme.value, 
                                            self.color_schemes[ColorScheme.SECURITY.value])
        
        chart_script = f'''
// Attack path visualization placeholder
var attackDiv = document.getElementById('{chart_id}');
attackDiv.innerHTML = '<div style="text-align: center; padding: 50px; color: {color_scheme["text"]};">' +
    '<h3>Attack Path Analysis</h3>' +
    '<p>Attack steps: {len(attack_steps)}</p>' +
    '<p>Interactive attack path visualization would be displayed here</p>' +
    '</div>';
        '''
        
        html_content = self.chart_templates['base_html'].format(
            title=config.title,
            chart_id=chart_id,
            height=config.height,
            bg_color=color_scheme['background'],
            text_color=color_scheme['text'],
            chart_script=chart_script
        )
        
        # Save HTML file
        output_file = self.output_dir / f"{chart_id}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return VisualizationResult(
            chart_id=chart_id,
            chart_type=config.chart_type.value,
            output_path=str(output_file),
            html_embed=html_content,
            success=True
        )

    def create_dashboard(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comprehensive dashboard with multiple visualizations."""
        self.logger.info("Creating comprehensive dashboard")
        
        dashboard_results = {
            'dashboard_id': f"dashboard_{int(time.time())}",
            'visualizations': [],
            'success': True,
            'error': None
        }
        
        try:
            # Create vulnerability severity chart
            if 'vulnerability_analysis' in analysis_results:
                vuln_chart = self.create_vulnerability_severity_chart(
                    analysis_results['vulnerability_analysis']
                )
                if vuln_chart.success:
                    dashboard_results['visualizations'].append(vuln_chart.__dict__)
            
            # Create risk assessment chart if available
            if 'risk_assessment' in analysis_results:
                # Create additional visualizations based on risk data
                pass
            
            # Create network topology if available
            if 'network_topology' in analysis_results:
                network_chart = self.create_network_topology_map(
                    analysis_results['network_topology']
                )
                if network_chart.success:
                    dashboard_results['visualizations'].append(network_chart.__dict__)
            
        except Exception as e:
            self.logger.error(f"Error creating dashboard: {e}")
            dashboard_results['success'] = False
            dashboard_results['error'] = str(e)
        
        return dashboard_results


def main():
    """Main function for testing the module."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Visual Builder Module")
    parser.add_argument("--input-file", required=True, help="Input JSON file with analysis results")
    parser.add_argument("--chart-type", choices=['pie', 'bar', 'line', 'network'], 
                       default='pie', help="Type of chart to create")
    parser.add_argument("--output-dir", help="Output directory for visualizations")
    
    args = parser.parse_args()
    
    # Load analysis data
    with open(args.input_file, 'r') as f:
        analysis_data = json.load(f)
    
    # Configuration
    config = {}
    if args.output_dir:
        config['output_dir'] = args.output_dir
    
    # Initialize visual builder
    visual_builder = VisualBuilder(config)
    
    # Create visualization based on type
    if args.chart_type == 'pie' and 'vulnerability_analysis' in analysis_data:
        result = visual_builder.create_vulnerability_severity_chart(
            analysis_data['vulnerability_analysis']
        )
    elif args.chart_type == 'dashboard':
        result = visual_builder.create_dashboard(analysis_data)
    else:
        print(f"Chart type {args.chart_type} not supported or data not available")
        return
    
    # Print results
    if isinstance(result, dict) and 'visualizations' in result:
        print(f"\n=== Dashboard Created ===")
        print(f"Dashboard ID: {result['dashboard_id']}")
        print(f"Visualizations: {len(result['visualizations'])}")
    else:
        print(f"\n=== Visualization Created ===")
        print(f"Chart ID: {result.chart_id}")
        print(f"Output path: {result.output_path}")
        print(f"Success: {result.success}")
        if result.error:
            print(f"Error: {result.error}")


if __name__ == "__main__":
    main()