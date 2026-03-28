"""
Static Factory Simulation PDF Report Generator

Runs a SimPy factory simulation and generates a comprehensive PDF report
with visualizations, statistics, and analysis.

Usage:
    python generate_pdf_report.py [options]

Examples:
    python generate_pdf_report.py --duration 100
    python generate_pdf_report.py --machines 10 --workers 20 --output report.pdf
    python generate_pdf_report.py --config custom_config.json
"""

import io
import argparse
import copy
from datetime import datetime
from typing import Dict, List

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from factory_simulation import run_simulation, DEFAULT_CONFIG, SimulationMetrics

# Constants
PAGE_WIDTH = letter[0]
PAGE_HEIGHT = letter[1]
MARGIN = 0.75 * inch

# Color palette matching dashboard
COLORS = {
    'completed': '#27ae60',
    'in_progress': '#f39c12',
    'raw_materials': '#3498db',
    'finished_goods': '#9b59b6',
    'passed': '#27ae60',
    'failed': '#e74c3c',
    'machines': ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#e67e22']
}


def create_production_chart(metrics: SimulationMetrics) -> io.BytesIO:
    """Generate production over time chart"""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot data
    ax.plot(metrics.time, metrics.products_completed,
            label='Completed', color=COLORS['completed'], linewidth=2.5, marker='o', markersize=4)
    ax.plot(metrics.time, metrics.products_in_progress,
            label='In Progress', color=COLORS['in_progress'], linewidth=2.5, marker='s', markersize=4)

    # Styling
    ax.set_xlabel('Simulation Time', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Products', fontsize=12, fontweight='bold')
    ax.set_title('Production Over Time', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='best', fontsize=11, frameon=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_facecolor('#f9f9f9')

    # Save to buffer
    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight', facecolor='white')
    buffer.seek(0)
    plt.close()

    return buffer


def create_inventory_chart(metrics: SimulationMetrics) -> io.BytesIO:
    """Generate inventory levels chart"""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot data with filled areas
    ax.fill_between(metrics.time, metrics.raw_materials, alpha=0.3, color=COLORS['raw_materials'], label='Raw Materials')
    ax.plot(metrics.time, metrics.raw_materials,
            color=COLORS['raw_materials'], linewidth=2.5, marker='o', markersize=4)

    ax.fill_between(metrics.time, metrics.finished_goods, alpha=0.3, color=COLORS['finished_goods'], label='Finished Goods')
    ax.plot(metrics.time, metrics.finished_goods,
            color=COLORS['finished_goods'], linewidth=2.5, marker='s', markersize=4)

    # Styling
    ax.set_xlabel('Simulation Time', fontsize=12, fontweight='bold')
    ax.set_ylabel('Units in Inventory', fontsize=12, fontweight='bold')
    ax.set_title('Inventory Levels Over Time', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='best', fontsize=11, frameon=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_facecolor('#f9f9f9')

    # Save to buffer
    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight', facecolor='white')
    buffer.seek(0)
    plt.close()

    return buffer


def create_quality_chart(metrics: SimulationMetrics) -> io.BytesIO:
    """Generate quality control chart"""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot data
    ax.plot(metrics.time, metrics.quality_passed,
            label='Passed', color=COLORS['passed'], linewidth=2.5, marker='o', markersize=4)
    ax.plot(metrics.time, metrics.quality_failed,
            label='Failed', color=COLORS['failed'], linewidth=2.5, marker='x', markersize=6)

    # Styling
    ax.set_xlabel('Simulation Time', fontsize=12, fontweight='bold')
    ax.set_ylabel('Product Count', fontsize=12, fontweight='bold')
    ax.set_title('Quality Control Results', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='best', fontsize=11, frameon=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_facecolor('#f9f9f9')

    # Save to buffer
    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight', facecolor='white')
    buffer.seek(0)
    plt.close()

    return buffer


def create_machine_utilization_chart(metrics: SimulationMetrics) -> io.BytesIO:
    """Generate machine utilization chart"""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot data for each machine
    for idx, (machine_name, utilization_data) in enumerate(metrics.machine_utilization.items()):
        color = COLORS['machines'][idx % len(COLORS['machines'])]
        time_slice = metrics.time[:len(utilization_data)]
        ax.plot(time_slice, utilization_data,
                label=machine_name, color=color, linewidth=2.5, marker='o', markersize=3)

    # Styling
    ax.set_xlabel('Simulation Time', fontsize=12, fontweight='bold')
    ax.set_ylabel('Utilization (%)', fontsize=12, fontweight='bold')
    ax.set_title('Machine Utilization Over Time', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(0, 100)
    ax.legend(loc='best', fontsize=10, frameon=True, shadow=True, ncol=2)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_facecolor('#f9f9f9')

    # Save to buffer
    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight', facecolor='white')
    buffer.seek(0)
    plt.close()

    return buffer


def calculate_quality_rate(metrics: SimulationMetrics) -> float:
    """Calculate quality pass rate percentage"""
    passed = metrics.quality_passed[-1] if metrics.quality_passed else 0
    failed = metrics.quality_failed[-1] if metrics.quality_failed else 0
    total = passed + failed
    return (passed / total * 100) if total > 0 else 0


def calculate_final_metrics(metrics: SimulationMetrics) -> Dict:
    """Calculate all final summary metrics"""
    return {
        'total_products': metrics.products_completed[-1] if metrics.products_completed else 0,
        'quality_rate': calculate_quality_rate(metrics),
        'avg_cycle_time': metrics.average_cycle_time[-1] if metrics.average_cycle_time else 0,
        'worker_util': metrics.worker_utilization[-1] if metrics.worker_utilization else 0,
        'final_raw_materials': metrics.raw_materials[-1] if metrics.raw_materials else 0,
        'final_finished_goods': metrics.finished_goods[-1] if metrics.finished_goods else 0,
        'total_passed': metrics.quality_passed[-1] if metrics.quality_passed else 0,
        'total_failed': metrics.quality_failed[-1] if metrics.quality_failed else 0,
    }


def analyze_machine_performance(metrics: SimulationMetrics) -> Dict:
    """Analyze individual machine performance"""
    machine_stats = {}
    for machine_name, util_data in metrics.machine_utilization.items():
        if util_data:
            final_util = util_data[-1]
            avg_util = sum(util_data) / len(util_data)
            peak_util = max(util_data)
        else:
            final_util = avg_util = peak_util = 0

        machine_stats[machine_name] = {
            'final_utilization': final_util,
            'average_utilization': avg_util,
            'peak_utilization': peak_util
        }
    return machine_stats


def create_kpi_table(metrics: SimulationMetrics) -> Table:
    """Create KPI summary table"""
    final_metrics = calculate_final_metrics(metrics)

    data = [
        ['Products Completed', 'Quality Pass Rate', 'Avg Cycle Time', 'Worker Utilization'],
        [
            f"{int(final_metrics['total_products']):,}",
            f"{final_metrics['quality_rate']:.1f}%",
            f"{final_metrics['avg_cycle_time']:.2f}",
            f"{final_metrics['worker_util']:.1f}%"
        ]
    ]

    table = Table(data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 14),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('TOPPADDING', (0, 1), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 15),
    ]))

    return table


def create_config_table(config: Dict) -> Table:
    """Create configuration parameters table"""
    data = [
        ['Parameter', 'Value'],
        ['Simulation Duration', f"{config.get('duration', 'N/A')}"],
        ['Production Lines', str(config.get('num_production_lines', 'N/A'))],
        ['Machines', str(config.get('num_machines', 'N/A'))],
        ['Workers', str(config.get('num_workers', 'N/A'))],
        ['Materials per Product', str(config.get('materials_per_product', 'N/A'))],
        ['Defect Rate', f"{config.get('defect_rate', 0) * 100:.1f}%"],
        ['Raw Material Capacity', str(config.get('raw_material_capacity', 'N/A'))],
        ['Finished Goods Capacity', str(config.get('finished_goods_capacity', 'N/A'))],
    ]

    table = Table(data, colWidths=[3*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica'),
        ('FONTNAME', (1, 1), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
    ]))

    return table


def create_machine_stats_table(machine_stats: Dict) -> Table:
    """Create detailed machine statistics table"""
    data = [['Machine', 'Final Util (%)', 'Avg Util (%)', 'Peak Util (%)']]

    for machine_name, stats in machine_stats.items():
        data.append([
            machine_name,
            f"{stats['final_utilization']:.1f}%",
            f"{stats['average_utilization']:.1f}%",
            f"{stats['peak_utilization']:.1f}%"
        ])

    table = Table(data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
    ]))

    return table


def generate_insights(metrics: SimulationMetrics, config: Dict) -> str:
    """Generate insights and analysis text"""
    final_metrics = calculate_final_metrics(metrics)
    machine_stats = analyze_machine_performance(metrics)

    insights = []

    # Production efficiency
    if final_metrics['total_products'] > 0:
        insights.append(f"• Successfully completed {int(final_metrics['total_products'])} products during the simulation.")

    # Quality analysis
    if final_metrics['quality_rate'] >= 98:
        insights.append(f"• Excellent quality performance with {final_metrics['quality_rate']:.1f}% pass rate.")
    elif final_metrics['quality_rate'] >= 95:
        insights.append(f"• Good quality performance with {final_metrics['quality_rate']:.1f}% pass rate.")
    else:
        insights.append(f"• Quality performance at {final_metrics['quality_rate']:.1f}% - consider process improvements.")

    # Worker utilization
    if final_metrics['worker_util'] < 50:
        insights.append(f"• Worker utilization is low at {final_metrics['worker_util']:.1f}% - consider reducing workforce or increasing production.")
    elif final_metrics['worker_util'] > 90:
        insights.append(f"• Worker utilization is high at {final_metrics['worker_util']:.1f}% - workers may be a bottleneck.")

    # Machine analysis
    if machine_stats:
        avg_machine_util = sum(s['average_utilization'] for s in machine_stats.values()) / len(machine_stats)
        if avg_machine_util > 85:
            insights.append(f"• High average machine utilization ({avg_machine_util:.1f}%) indicates efficient equipment usage.")
        elif avg_machine_util < 60:
            insights.append(f"• Low average machine utilization ({avg_machine_util:.1f}%) suggests excess capacity.")

    # Inventory status
    if final_metrics['final_raw_materials'] < config.get('raw_material_capacity', 1000) * 0.2:
        insights.append(f"• Raw material inventory is low ({int(final_metrics['final_raw_materials'])} units) - ensure adequate supply.")

    return '\n'.join(insights) if insights else '• Simulation completed successfully.'


def add_header_footer(canvas, doc):
    """Add header and footer to each page"""
    canvas.saveState()

    # Header
    canvas.setFont('Helvetica-Bold', 10)
    canvas.setFillColorRGB(0.2, 0.2, 0.2)
    canvas.drawString(MARGIN, PAGE_HEIGHT - 0.5*inch, "Factory Simulation Report")
    canvas.line(MARGIN, PAGE_HEIGHT - 0.6*inch, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 0.6*inch)

    # Footer
    canvas.setFont('Helvetica', 8)
    canvas.setFillColorRGB(0.5, 0.5, 0.5)
    canvas.drawRightString(PAGE_WIDTH - MARGIN, 0.5*inch, f"Page {doc.page}")
    canvas.drawString(MARGIN, 0.5*inch, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    canvas.restoreState()


def generate_pdf_report(metrics: SimulationMetrics, config: Dict, output_path: str, title: str = "Factory Simulation Report"):
    """Generate complete PDF report"""

    # Create PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
        leftMargin=MARGIN,
        rightMargin=MARGIN
    )

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=6,
        alignment=TA_LEFT
    )

    # Build story
    story = []

    # Page 1: Executive Summary
    story.append(Paragraph(title, title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}", normal_style))
    story.append(Spacer(1, 0.3*inch))

    # KPI Cards
    story.append(Paragraph("Key Performance Indicators", heading_style))
    story.append(create_kpi_table(metrics))
    story.append(Spacer(1, 0.2*inch))

    # Configuration
    story.append(Paragraph("Simulation Configuration", heading_style))
    config_with_duration = config.copy()
    config_with_duration['duration'] = metrics.time[-1] if metrics.time else 0
    story.append(create_config_table(config_with_duration))
    story.append(Spacer(1, 0.2*inch))

    # Insights
    story.append(Paragraph("Key Insights", heading_style))
    insights_text = generate_insights(metrics, config)
    for line in insights_text.split('\n'):
        story.append(Paragraph(line, normal_style))

    story.append(PageBreak())

    # Page 2: Production and Inventory Charts
    story.append(Paragraph("Production Analysis", heading_style))
    story.append(Spacer(1, 0.1*inch))

    chart1 = create_production_chart(metrics)
    story.append(Image(chart1, width=6.5*inch, height=4*inch))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("Inventory Management", heading_style))
    story.append(Spacer(1, 0.1*inch))

    chart2 = create_inventory_chart(metrics)
    story.append(Image(chart2, width=6.5*inch, height=4*inch))

    story.append(PageBreak())

    # Page 3: Quality and Machine Utilization
    story.append(Paragraph("Quality Control", heading_style))
    story.append(Spacer(1, 0.1*inch))

    chart3 = create_quality_chart(metrics)
    story.append(Image(chart3, width=6.5*inch, height=4*inch))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("Machine Utilization", heading_style))
    story.append(Spacer(1, 0.1*inch))

    chart4 = create_machine_utilization_chart(metrics)
    story.append(Image(chart4, width=6.5*inch, height=4*inch))

    story.append(PageBreak())

    # Page 4: Detailed Statistics
    story.append(Paragraph("Detailed Statistics", heading_style))
    story.append(Spacer(1, 0.2*inch))

    # Final metrics summary
    final_metrics = calculate_final_metrics(metrics)
    story.append(Paragraph("Final Metrics Summary", ParagraphStyle('SubHeading', parent=heading_style, fontSize=13)))

    summary_data = [
        ['Metric', 'Value'],
        ['Total Products Completed', f"{int(final_metrics['total_products']):,}"],
        ['Products Passed Quality', f"{int(final_metrics['total_passed']):,}"],
        ['Products Failed Quality', f"{int(final_metrics['total_failed']):,}"],
        ['Quality Pass Rate', f"{final_metrics['quality_rate']:.2f}%"],
        ['Average Cycle Time', f"{final_metrics['avg_cycle_time']:.2f}"],
        ['Worker Utilization', f"{final_metrics['worker_util']:.2f}%"],
        ['Final Raw Materials', f"{int(final_metrics['final_raw_materials']):,} units"],
        ['Final Finished Goods', f"{int(final_metrics['final_finished_goods']):,} units"],
    ]

    summary_table = Table(summary_data, colWidths=[3.5*inch, 2.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica'),
        ('FONTNAME', (1, 1), (1, -1), 'Helvetica-Bold'),
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 0.3*inch))

    # Machine statistics
    story.append(Paragraph("Machine Performance Breakdown", ParagraphStyle('SubHeading', parent=heading_style, fontSize=13)))
    machine_stats = analyze_machine_performance(metrics)
    story.append(create_machine_stats_table(machine_stats))

    # Build PDF
    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Generate PDF report for factory simulation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_pdf_report.py
  python generate_pdf_report.py --duration 200 --machines 10
  python generate_pdf_report.py --config custom.json --output my_report.pdf
        """
    )

    parser.add_argument('--duration', type=float, default=100,
                       help='Simulation duration in time units (default: 100)')
    parser.add_argument('--production-lines', type=int, default=8,
                       help='Number of production lines (default: 8)')
    parser.add_argument('--machines', type=int, default=5,
                       help='Number of machines (default: 5)')
    parser.add_argument('--workers', type=int, default=10,
                       help='Number of workers (default: 10)')
    parser.add_argument('--output', type=str, default=None,
                       help='Output PDF file path (default: auto-generated timestamp)')
    parser.add_argument('--title', type=str, default='Factory Simulation Report',
                       help='Report title (default: "Factory Simulation Report")')

    return parser.parse_args()


def main():
    """Main execution function"""
    args = parse_arguments()

    # Create configuration
    config = copy.deepcopy(DEFAULT_CONFIG)
    config['num_production_lines'] = args.production_lines
    config['num_machines'] = args.machines
    config['num_workers'] = args.workers

    # Generate output path if not specified
    if args.output is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.output = f'factory_simulation_report_{timestamp}.pdf'

    # Run simulation
    print("=" * 60)
    print("Factory Simulation PDF Report Generator")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Duration: {args.duration}")
    print(f"  Production Lines: {args.production_lines}")
    print(f"  Machines: {args.machines}")
    print(f"  Workers: {args.workers}")
    print(f"\nRunning simulation...")

    metrics = run_simulation(config, duration=args.duration)

    print(f"Simulation complete!")
    print(f"\nGenerating PDF report...")

    # Generate PDF
    generate_pdf_report(metrics, config, args.output, args.title)

    print(f"✓ PDF report generated: {args.output}")

    # Print summary
    final_metrics = calculate_final_metrics(metrics)
    print(f"\n" + "=" * 60)
    print("Simulation Summary:")
    print("=" * 60)
    print(f"  Products Completed: {int(final_metrics['total_products']):,}")
    print(f"  Quality Pass Rate: {final_metrics['quality_rate']:.1f}%")
    print(f"  Average Cycle Time: {final_metrics['avg_cycle_time']:.2f}")
    print(f"  Worker Utilization: {final_metrics['worker_util']:.1f}%")
    print(f"  Final Raw Materials: {int(final_metrics['final_raw_materials']):,}")
    print(f"  Final Finished Goods: {int(final_metrics['final_finished_goods']):,}")
    print("=" * 60)


if __name__ == "__main__":
    main()
