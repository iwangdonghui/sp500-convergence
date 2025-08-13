#!/usr/bin/env python3
"""
Demo script for professional report generation features.

This script demonstrates the new professional report generation capabilities
added in Stage 2, including PDF reports, Excel exports, and chart generation.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os
from datetime import datetime

from sp500_convergence import SP500Analyzer, download_slickcharts_data
from data_processor import DataProcessor
from report_generator import generate_comprehensive_report


def demo_with_real_data():
    """Demo with real S&P 500 data."""
    print("🚀 Professional Report Generation Demo")
    print("=" * 60)
    print("Using real S&P 500 data from SlickCharts...")
    
    try:
        # Download real data
        print("\n📥 Downloading S&P 500 data...")
        data = download_slickcharts_data()
        print(f"✅ Downloaded {len(data)} years of data ({data['year'].min()}-{data['year'].max()})")
        
        # Create data processor
        processor = DataProcessor()
        processor.set_data(data)
        
        # Generate reports
        output_dir = Path("demo_reports")
        output_dir.mkdir(exist_ok=True)
        
        print(f"\n📋 Generating professional reports...")
        
        # Generate PDF report
        print("  📄 Generating PDF report...")
        pdf_data = processor.generate_professional_report('pdf')
        pdf_path = output_dir / f"sp500_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        with open(pdf_path, 'wb') as f:
            f.write(pdf_data)
        print(f"     ✅ PDF saved: {pdf_path} ({len(pdf_data):,} bytes)")
        
        # Generate Excel report
        print("  📊 Generating Excel report...")
        excel_data = processor.generate_professional_report('excel')
        excel_path = output_dir / f"sp500_analysis_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        with open(excel_path, 'wb') as f:
            f.write(excel_data)
        print(f"     ✅ Excel saved: {excel_path} ({len(excel_data):,} bytes)")
        
        # Generate chart
        print("  📈 Generating risk metrics chart...")
        try:
            chart_data = processor.export_chart('risk_metrics', 'png')
            if chart_data:
                chart_path = output_dir / f"sp500_risk_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                with open(chart_path, 'wb') as f:
                    f.write(chart_data)
                print(f"     ✅ Chart saved: {chart_path} ({len(chart_data):,} bytes)")
            else:
                print("     ⚠️  Chart export returned empty data (may need kaleido package)")
        except Exception as e:
            print(f"     ⚠️  Chart export failed: {e}")
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"📁 All files saved to: {output_dir.absolute()}")
        
        # Display file listing
        print(f"\n📋 Generated files:")
        for file in sorted(output_dir.glob("*")):
            file_size = file.stat().st_size
            print(f"   📄 {file.name} ({file_size:,} bytes)")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def demo_report_features():
    """Demo the key features of the professional report system."""
    print("\n" + "=" * 60)
    print("PROFESSIONAL REPORT SYSTEM FEATURES")
    print("=" * 60)
    
    features = [
        ("📄 PDF Reports", [
            "Professional branded design with company colors",
            "Executive summary with key metrics",
            "Comprehensive risk analysis section",
            "Methodology and disclaimers",
            "High-quality charts and tables",
            "Multi-language support (Chinese/English)"
        ]),
        
        ("📊 Excel Reports", [
            "Executive summary sheet with key metrics",
            "Detailed risk metrics with proper formatting",
            "Automatic column width adjustment",
            "Professional styling and colors",
            "Percentage and ratio formatting",
            "Ready for further analysis"
        ]),
        
        ("📈 Chart Exports", [
            "High-resolution PNG format (1200x800)",
            "Professional color scheme",
            "Risk-return scatter plots",
            "Comparative bar charts",
            "Multi-panel layouts",
            "Publication-ready quality"
        ]),
        
        ("🔧 Technical Features", [
            "Automatic data validation and filtering",
            "Smart configuration based on available data",
            "Error handling and graceful degradation",
            "Memory-efficient processing",
            "Caching for improved performance",
            "Streamlit integration"
        ])
    ]
    
    for category, feature_list in features:
        print(f"\n{category}")
        print("-" * 40)
        for feature in feature_list:
            print(f"  ✅ {feature}")
    
    print(f"\n🎯 Use Cases:")
    print("  • Investment committee presentations")
    print("  • Client reporting and communication")
    print("  • Regulatory compliance documentation")
    print("  • Academic research and analysis")
    print("  • Portfolio performance evaluation")


def demo_integration_guide():
    """Show how to integrate the report system."""
    print("\n" + "=" * 60)
    print("INTEGRATION GUIDE")
    print("=" * 60)
    
    print("\n🔧 Web UI Integration:")
    print("  1. Load data using DataProcessor")
    print("  2. Run analysis to populate results")
    print("  3. Navigate to 'Risk Metrics' tab")
    print("  4. Use professional report generation buttons")
    print("  5. Download generated reports")
    
    print("\n💻 Programmatic Usage:")
    print("""
    # Basic usage
    from data_processor import DataProcessor
    
    processor = DataProcessor()
    processor.set_data(your_data)
    
    # Generate PDF report
    pdf_data = processor.generate_professional_report('pdf')
    
    # Generate Excel report
    excel_data = processor.generate_professional_report('excel')
    
    # Export charts
    chart_data = processor.export_chart('risk_metrics', 'png')
    """)
    
    print("\n📦 Dependencies:")
    print("  • reportlab (PDF generation)")
    print("  • openpyxl (Excel generation)")
    print("  • plotly (Chart generation)")
    print("  • pandas, numpy (Data processing)")


def main():
    """Run the complete demo."""
    print("🎯 S&P 500 Professional Report Generation Demo")
    print("=" * 80)
    
    # Show features
    demo_report_features()
    
    # Show integration guide
    demo_integration_guide()
    
    # Ask user if they want to run the actual demo
    print("\n" + "=" * 60)
    print("LIVE DEMO")
    print("=" * 60)
    
    response = input("\n🤔 Would you like to run a live demo with real S&P 500 data? (y/n): ")
    
    if response.lower().startswith('y'):
        success = demo_with_real_data()
        
        if success:
            print("\n🎉 Demo completed successfully!")
            print("✅ Professional report system is fully operational!")
            
            print("\n🌐 Next steps:")
            print("  1. Open the web application: http://localhost:8501")
            print("  2. Load data and run analysis")
            print("  3. Go to 'Risk Metrics' tab")
            print("  4. Try the professional report generation buttons")
            
        else:
            print("\n❌ Demo encountered issues. Please check the error messages above.")
    else:
        print("\n👍 Demo skipped. The professional report system is ready for use!")
    
    print("\n" + "=" * 80)
    print("Thank you for trying the S&P 500 Professional Report System!")
    print("=" * 80)


if __name__ == '__main__':
    main()
