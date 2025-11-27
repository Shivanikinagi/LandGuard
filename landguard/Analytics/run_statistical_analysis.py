from analytics.statistical_analyzer import StatisticalAnalyzer

# Initialize analyzer with correct path
analyzer = StatisticalAnalyzer('Blockchain/blockchain/storage/evidence')

# Generate comprehensive report
report = analyzer.generate_report(
    'analytics/outputs/reports/statistical_report.json'
)

# Print summary - add error handling
if 'error' in report:
    print(f"⚠️ Error: {report['error']}")
    print("💡 Ensure Blockchain evidence data exists first:")
    print("   python Blockchain/blockchain/evidence_package.py")
else:
    print(report.keys())
    print(report)
    analyzer.print_summary(report)