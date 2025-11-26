# scripts/run_statistical_analysis.py
from analytics.statistical_analyzer import StatisticalAnalyzer

# Initialize analyzer
analyzer = StatisticalAnalyzer('Blockchain/blockchain/blockchain/storage/audit_logs')

# Generate comprehensive report
report = analyzer.generate_report(
    'analytics/outputs/reports/statistical_report.json'
)

# Print summary
print(report.keys())
print(report)
analyzer.print_summary(report)