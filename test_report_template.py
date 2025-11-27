"""
Test Report Template and Generator
Generates comprehensive test reports for conflict detection system
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class TestReportGenerator:
    """Generate detailed test reports"""
    
    def __init__(self, test_results: Dict[str, Any], system_info: Dict[str, Any]):
        """
        Initialize report generator
        
        Args:
            test_results: Test execution results
            system_info: System information
        """
        self.test_results = test_results
        self.system_info = system_info
        self.timestamp = datetime.now().isoformat()
    
    def generate_html_report(self, output_file: str = 'test_report.html') -> None:
        """Generate HTML test report"""
        html_content = self._build_html_report()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def generate_json_report(self, output_file: str = 'test_report.json') -> None:
        """Generate JSON test report"""
        report = {
            'timestamp': self.timestamp,
            'summary': self._generate_summary(),
            'system_info': self.system_info,
            'test_results': self.test_results,
            'recommendations': self._generate_recommendations()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
    
    def generate_markdown_report(self, output_file: str = 'test_report.md') -> None:
        """Generate Markdown test report"""
        md_content = self._build_markdown_report()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
    
    def _build_html_report(self) -> str:
        """Build HTML report content"""
        summary = self._generate_summary()
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Multi-Annotator Conflict Detection - Test Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
        }}
        .header {{
            border-bottom: 3px solid #007bff;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #007bff;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header p {{
            color: #666;
            font-size: 0.95em;
        }}
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .card.success {{
            background: linear-gradient(135deg, #66bb6a 0%, #43a047 100%);
        }}
        .card.warning {{
            background: linear-gradient(135deg, #ffa726 0%, #fb8c00 100%);
        }}
        .card.error {{
            background: linear-gradient(135deg, #ef5350 0%, #e53935 100%);
        }}
        .card-value {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .card-label {{
            font-size: 0.85em;
            opacity: 0.9;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section-title {{
            font-size: 1.8em;
            color: #007bff;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
            color: #007bff;
        }}
        tr:hover {{
            background-color: #f9f9f9;
        }}
        .status-pass {{
            color: #28a745;
            font-weight: bold;
        }}
        .status-fail {{
            color: #dc3545;
            font-weight: bold;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #ddd;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Test Execution Report</h1>
            <p>Multi-Annotator Conflict Detection System</p>
            <p>Generated: {self.timestamp}</p>
        </div>
        
        <div class="summary-cards">
            <div class="card {'success' if summary['overall_status'] == 'PASSED' else 'error'}">
                <div class="card-value">{summary['overall_status']}</div>
                <div class="card-label">Overall Status</div>
            </div>
            <div class="card success">
                <div class="card-value">{summary['total_tests']}</div>
                <div class="card-label">Total Tests</div>
            </div>
            <div class="card success">
                <div class="card-value">{summary['passed_tests']}</div>
                <div class="card-label">Passed Tests</div>
            </div>
            <div class="card {'error' if summary['failed_tests'] > 0 else 'warning'}">
                <div class="card-value">{summary['failed_tests']}</div>
                <div class="card-label">Failed Tests</div>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">Test Results Summary</h2>
            <p><strong>Success Rate:</strong> {summary['success_rate']}%</p>
            <p><strong>Execution Time:</strong> {summary.get('execution_time', 'N/A')}</p>
        </div>
        
        <div class="footer">
            <p>Report generated automatically by Multi-Annotator Conflict Detection System</p>
            <p>For more information, visit: https://github.com/yourusername/conflict-detection-system</p>
        </div>
    </div>
</body>
</html>
"""
    
    def _build_markdown_report(self) -> str:
        """Build Markdown report content"""
        summary = self._generate_summary()
        
        report = f"""# Multi-Annotator Conflict Detection System
## Test Execution Report

**Generated:** {self.timestamp}

---

## Executive Summary

- **Overall Status:** {summary['overall_status']}
- **Total Tests:** {summary['total_tests']}
- **Passed:** {summary['passed_tests']}
- **Failed:** {summary['failed_tests']}
- **Success Rate:** {summary['success_rate']}%

---

## System Information

| Item | Value |
|------|-------|
| Platform | {self.system_info.get('platform', 'N/A')} |
| Python Version | {self.system_info.get('python_version', 'N/A')} |
| Test Framework | {self.system_info.get('test_framework', 'unittest')} |

---

## Test Categories

### Unit Tests
- Conflict Detection Tests
- Conflict Reasoning Tests
- Label Resolution Tests
- Edge Cases Tests
- Sentiment Analysis Tests

### Integration Tests
- Data Loading and Validation
- Pipeline Execution
- Output Generation
- Report Generation

### Performance Tests
- Large Dataset Handling
- Memory Usage
- Execution Time

---

## Recommendations

"""
        recommendations = self._generate_recommendations()
        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n"
        
        return report
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics"""
        total_tests = self.test_results.get('total_tests', 0)
        passed_tests = self.test_results.get('passed_tests', 0)
        failed_tests = self.test_results.get('failed_tests', 0)
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        return {
            'overall_status': 'PASSED' if failed_tests == 0 else 'FAILED',
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': round(success_rate, 2),
            'execution_time': self.test_results.get('execution_time', 'N/A')
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        summary = self._generate_summary()
        
        if summary['failed_tests'] > 0:
            recommendations.append("Review failed tests and fix issues identified")
        
        if summary['success_rate'] < 100:
            recommendations.append("Investigate edge cases causing test failures")
        
        recommendations.append("Run tests regularly as part of CI/CD pipeline")
        recommendations.append("Monitor performance metrics for regression")
        recommendations.append("Update tests when functionality changes")
        
        return recommendations


# Template for test result data structure
TEST_RESULT_TEMPLATE = {
    "timestamp": datetime.now().isoformat(),
    "total_tests": 0,
    "passed_tests": 0,
    "failed_tests": 0,
    "execution_time": "0s",
    "test_categories": {
        "unit_tests": {
            "count": 0,
            "passed": 0,
            "failed": 0,
            "tests": []
        },
        "integration_tests": {
            "count": 0,
            "passed": 0,
            "failed": 0,
            "tests": []
        },
        "performance_tests": {
            "count": 0,
            "passed": 0,
            "failed": 0,
            "tests": []
        }
    },
    "coverage": {
        "overall": 0,
        "by_module": {
            "analyzer": 0,
            "main": 0
        }
    }
}

# Template for system information
SYSTEM_INFO_TEMPLATE = {
    "platform": "Windows/Linux/Darwin",
    "python_version": "3.x.x",
    "test_framework": "unittest",
    "environment": "local/docker",
    "timestamp": datetime.now().isoformat()
}
