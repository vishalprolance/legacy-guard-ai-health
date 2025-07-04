"""
Reporter Agent - Responsible for generating comprehensive health check reports
"""

import os
import time
import json
import logging
from datetime import datetime
from utils.html_report import HTMLReportGenerator

logger = logging.getLogger(__name__)

class ReporterAgent:
    """Agent responsible for generating comprehensive test reports"""
    
    def __init__(self, config):
        self.config = config
        self.html_generator = HTMLReportGenerator()
        self.report_data = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'test_run_id': datetime.now().strftime("%Y%m%d_%H%M%S"),
            'overall_status': 'UNKNOWN',
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'agent_results': {},
            'screenshots': [],
            'errors': [],
            'summary': '',
            'recommendations': []
        }
    
    def collect_agent_results(self, launcher_result=None, login_result=None, 
                            validator_result=None, transaction_result=None):
        """Collect results from all agents"""
        logger.info("Collecting results from all agents")
        
        # Store agent results
        if launcher_result:
            self.report_data['agent_results']['launcher'] = launcher_result
            self._process_agent_result('App Launcher', launcher_result)
        
        if login_result:
            self.report_data['agent_results']['login'] = login_result
            self._process_agent_result('Login', login_result)
        
        if validator_result:
            self.report_data['agent_results']['validator'] = validator_result
            self._process_validator_result(validator_result)
        
        if transaction_result:
            self.report_data['agent_results']['transaction'] = transaction_result
            self._process_transaction_result(transaction_result)
        
        # Calculate overall statistics
        self._calculate_overall_status()
        self._generate_summary()
        self._generate_recommendations()
    
    def _process_agent_result(self, agent_name, result):
        """Process individual agent result"""
        if result.get('status') == 'PASSED':
            self.report_data['passed_tests'] += 1
        elif result.get('status') == 'FAILED':
            self.report_data['failed_tests'] += 1
            self.report_data['errors'].append(f"{agent_name}: {result.get('message', 'Unknown error')}")
        
        self.report_data['total_tests'] += 1
        
        # Collect screenshots
        if 'screenshot' in result:
            self.report_data['screenshots'].append({
                'agent': agent_name,
                'path': result['screenshot'],
                'type': 'single'
            })
        
        if 'screenshots' in result:
            for screenshot_type, path in result['screenshots'].items():
                if path:
                    self.report_data['screenshots'].append({
                        'agent': agent_name,
                        'path': path,
                        'type': screenshot_type
                    })
    
    def _process_validator_result(self, result):
        """Process screen validator results"""
        validation_results = result.get('validation_results', [])
        
        for validation in validation_results:
            if validation.get('status') == 'PASSED':
                self.report_data['passed_tests'] += 1
            elif validation.get('status') == 'FAILED':
                self.report_data['failed_tests'] += 1
                self.report_data['errors'].append(f"Screen Validation: {validation.get('message', 'Unknown error')}")
            
            self.report_data['total_tests'] += 1
            
            # Collect validation screenshots
            if 'screenshot' in validation:
                self.report_data['screenshots'].append({
                    'agent': 'Screen Validator',
                    'path': validation['screenshot'],
                    'type': 'validation'
                })
    
    def _process_transaction_result(self, result):
        """Process transaction test results"""
        test_results = result.get('test_results', [])
        
        for test in test_results:
            if test.get('status') == 'PASSED':
                self.report_data['passed_tests'] += 1
            elif test.get('status') == 'FAILED':
                self.report_data['failed_tests'] += 1
                self.report_data['errors'].append(f"Transaction Test ({test.get('test')}): {test.get('message', 'Unknown error')}")
            
            self.report_data['total_tests'] += 1
        
        # Collect transaction screenshots
        screenshots = result.get('screenshots', {})
        for screenshot_type, path in screenshots.items():
            if path:
                self.report_data['screenshots'].append({
                    'agent': 'Transaction',
                    'path': path,
                    'type': screenshot_type
                })
    
    def _calculate_overall_status(self):
        """Calculate overall test status"""
        if self.report_data['total_tests'] == 0:
            self.report_data['overall_status'] = 'NO_TESTS'
        elif self.report_data['failed_tests'] == 0:
            self.report_data['overall_status'] = 'PASSED'
        else:
            self.report_data['overall_status'] = 'FAILED'
    
    def _generate_summary(self):
        """Generate executive summary"""
        total = self.report_data['total_tests']
        passed = self.report_data['passed_tests']
        failed = self.report_data['failed_tests']
        
        if total == 0:
            self.report_data['summary'] = "No tests were executed during this health check run."
        elif failed == 0:
            self.report_data['summary'] = f"✅ All {total} tests passed successfully. The banking application is functioning correctly."
        else:
            success_rate = (passed / total) * 100
            self.report_data['summary'] = f"⚠️ {failed} out of {total} tests failed ({success_rate:.1f}% success rate). The banking application requires attention."
    
    def _generate_recommendations(self):
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check for specific failure patterns
        errors = self.report_data['errors']
        
        if any('launch' in error.lower() for error in errors):
            recommendations.append("Application launch issues detected. Check application path and dependencies.")
        
        if any('login' in error.lower() for error in errors):
            recommendations.append("Login functionality issues detected. Verify credentials and authentication system.")
        
        if any('visual' in error.lower() or 'screen' in error.lower() for error in errors):
            recommendations.append("Visual/screen validation issues detected. UI may have changed - update baseline images if intentional.")
        
        if any('transaction' in error.lower() for error in errors):
            recommendations.append("Transaction functionality issues detected. Check transaction processing system.")
        
        # General recommendations
        if self.report_data['failed_tests'] > 0:
            recommendations.extend([
                "Review error logs for detailed failure analysis.",
                "Consider running tests during off-peak hours to reduce system load impact.",
                "Update test data and baselines if application has been recently updated."
            ])
        else:
            recommendations.extend([
                "System is functioning normally.",
                "Continue regular health checks to maintain application reliability.",
                "Consider expanding test coverage for additional workflows."
            ])
        
        self.report_data['recommendations'] = recommendations
    
    def generate_json_report(self, output_path=None):
        """Generate JSON report"""
        if not output_path:
            output_path = f"reports/health_check_{self.report_data['test_run_id']}.json"
        
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(self.report_data, f, indent=2, default=str)
            
            logger.info(f"JSON report generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to generate JSON report: {str(e)}")
            return None
    
    def generate_html_report(self, output_path=None):
        """Generate HTML report"""
        if not output_path:
            output_path = f"reports/health_check_{self.report_data['test_run_id']}.html"
        
        try:
            html_content = self.html_generator.generate_report(self.report_data, output_path)
            logger.info(f"HTML report generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to generate HTML report: {str(e)}")
            return None
    
    def send_alert_notifications(self):
        """Send alerts if tests failed (placeholder for future implementation)"""
        if self.report_data['overall_status'] == 'FAILED':
            logger.warning("Test failures detected - alerts would be sent here")
            
            # Placeholder for Slack/email notifications
            alert_message = f"""
            🚨 Bank Application Health Check Alert
            
            Status: {self.report_data['overall_status']}
            Failed Tests: {self.report_data['failed_tests']} / {self.report_data['total_tests']}
            Timestamp: {self.report_data['timestamp']}
            
            Errors:
            {chr(10).join(self.report_data['errors'][:5])}
            
            Please check the full report for details.
            """
            
            logger.info(f"Alert notification content: {alert_message}")
    
    def execute_task(self, all_agent_results=None):
        """Execute the reporting task"""
        logger.info("Starting Reporter Agent task")
        
        # If agent results provided as a dictionary, extract them
        if all_agent_results:
            self.collect_agent_results(
                launcher_result=all_agent_results.get('launcher'),
                login_result=all_agent_results.get('login'),
                validator_result=all_agent_results.get('validator'),
                transaction_result=all_agent_results.get('transaction')
            )
        
        # Generate reports
        json_report_path = self.generate_json_report()
        html_report_path = self.generate_html_report()
        
        # Send alerts if needed
        self.send_alert_notifications()
        
        return {
            'status': 'PASSED',
            'message': 'Reports generated successfully',
            'reports': {
                'json': json_report_path,
                'html': html_report_path
            },
            'summary': self.report_data['summary'],
            'overall_status': self.report_data['overall_status']
        }