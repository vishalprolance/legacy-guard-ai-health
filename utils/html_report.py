"""
HTML Report Generator
Creates comprehensive HTML reports for health check results
"""

import os
import base64
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class HTMLReportGenerator:
    """Utility class for generating HTML reports"""
    
    def __init__(self):
        self.template = self._get_html_template()
    
    def _get_html_template(self):
        """Get the HTML template for reports"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bank Application Health Check Report</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            margin: -20px -20px 30px -20px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            border-left: 4px solid #667eea;
        }
        
        .card.passed { border-left-color: #4CAF50; }
        .card.failed { border-left-color: #f44336; }
        .card.warning { border-left-color: #ff9800; }
        
        .card-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .card-label {
            color: #666;
            font-size: 0.9em;
        }
        
        .section {
            margin-bottom: 30px;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .section h2 {
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .status-passed {
            background: #4CAF50;
            color: white;
        }
        
        .status-failed {
            background: #f44336;
            color: white;
        }
        
        .status-warning {
            background: #ff9800;
            color: white;
        }
        
        .agent-result {
            margin-bottom: 20px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background: #fafafa;
        }
        
        .agent-result h3 {
            margin-bottom: 10px;
            color: #333;
        }
        
        .screenshot-gallery {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .screenshot-item {
            text-align: center;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .screenshot-item img {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
            cursor: pointer;
            transition: transform 0.3s;
        }
        
        .screenshot-item img:hover {
            transform: scale(1.05);
        }
        
        .screenshot-title {
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }
        
        .error-list {
            background: #ffebee;
            border: 1px solid #f44336;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
        }
        
        .error-item {
            margin: 5px 0;
            padding: 5px;
            background: white;
            border-radius: 3px;
            color: #d32f2f;
        }
        
        .recommendations {
            background: #e3f2fd;
            border: 1px solid #2196f3;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
        }
        
        .recommendation-item {
            margin: 8px 0;
            padding: 8px;
            background: white;
            border-radius: 3px;
            border-left: 3px solid #2196f3;
            padding-left: 12px;
        }
        
        .metadata {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        
        .metadata-item {
            text-align: center;
        }
        
        .metadata-label {
            font-weight: bold;
            color: #666;
            font-size: 0.9em;
        }
        
        .metadata-value {
            font-size: 1.1em;
            margin-top: 5px;
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 0.9em;
        }
        
        @media (max-width: 768px) {
            .container { padding: 10px; }
            .header { padding: 20px; margin: -10px -10px 20px -10px; }
            .header h1 { font-size: 2em; }
            .summary-cards { grid-template-columns: 1fr; }
            .screenshot-gallery { grid-template-columns: 1fr; }
        }
        
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            padding-top: 100px;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.9);
        }
        
        .modal-content {
            margin: auto;
            display: block;
            width: 80%;
            max-width: 700px;
        }
        
        .close {
            position: absolute;
            top: 15px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            transition: 0.3s;
            cursor: pointer;
        }
        
        .close:hover { color: #bbb; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏦 Bank Application Health Check</h1>
            <div class="subtitle">Automated Testing Report</div>
        </div>
        
        <div class="metadata">
            <div class="metadata-item">
                <div class="metadata-label">Report Generated</div>
                <div class="metadata-value">{timestamp}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Test Run ID</div>
                <div class="metadata-value">{test_run_id}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Overall Status</div>
                <div class="metadata-value">
                    <span class="status-badge status-{overall_status_class}">{overall_status}</span>
                </div>
            </div>
        </div>
        
        <div class="summary-cards">
            <div class="card">
                <div class="card-value">{total_tests}</div>
                <div class="card-label">Total Tests</div>
            </div>
            <div class="card passed">
                <div class="card-value">{passed_tests}</div>
                <div class="card-label">Passed</div>
            </div>
            <div class="card failed">
                <div class="card-value">{failed_tests}</div>
                <div class="card-label">Failed</div>
            </div>
            <div class="card">
                <div class="card-value">{success_rate}%</div>
                <div class="card-label">Success Rate</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Executive Summary</h2>
            <p>{summary}</p>
        </div>
        
        {errors_section}
        
        <div class="section">
            <h2>🤖 Agent Results</h2>
            {agent_results_content}
        </div>
        
        {screenshots_section}
        
        <div class="section">
            <h2>💡 Recommendations</h2>
            <div class="recommendations">
                {recommendations_content}
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by Bank Application Health Check Automation Framework</p>
            <p>Powered by CrewAI • {timestamp}</p>
        </div>
    </div>
    
    <!-- Modal for image viewing -->
    <div id="imageModal" class="modal">
        <span class="close" onclick="closeModal()">&times;</span>
        <img class="modal-content" id="modalImg">
    </div>
    
    <script>
        function openModal(imgSrc) {
            document.getElementById('imageModal').style.display = 'block';
            document.getElementById('modalImg').src = imgSrc;
        }
        
        function closeModal() {
            document.getElementById('imageModal').style.display = 'none';
        }
        
        // Close modal when clicking outside the image
        window.onclick = function(event) {
            const modal = document.getElementById('imageModal');
            if (event.target == modal) {
                modal.style.display = "none";
            }
        }
        
        // Add click handlers to all screenshots
        document.addEventListener('DOMContentLoaded', function() {
            const screenshots = document.querySelectorAll('.screenshot-item img');
            screenshots.forEach(img => {
                img.onclick = function() {
                    openModal(this.src);
                };
            });
        });
    </script>
</body>
</html>
        """
    
    def _image_to_base64(self, image_path):
        """Convert image to base64 for embedding in HTML"""
        try:
            if not os.path.exists(image_path):
                return None
            
            with open(image_path, 'rb') as img_file:
                img_data = img_file.read()
                img_base64 = base64.b64encode(img_data).decode('utf-8')
                
                # Determine image type
                ext = os.path.splitext(image_path)[1].lower()
                mime_type = 'image/png' if ext == '.png' else 'image/jpeg'
                
                return f"data:{mime_type};base64,{img_base64}"
                
        except Exception as e:
            logger.error(f"Failed to convert image to base64: {str(e)}")
            return None
    
    def _generate_agent_results_html(self, agent_results):
        """Generate HTML for agent results section"""
        html_content = ""
        
        for agent_name, result in agent_results.items():
            status = result.get('status', 'UNKNOWN')
            message = result.get('message', 'No message provided')
            
            status_class = status.lower() if status.lower() in ['passed', 'failed'] else 'warning'
            
            html_content += f"""
            <div class="agent-result">
                <h3>{agent_name.title()} Agent <span class="status-badge status-{status_class}">{status}</span></h3>
                <p>{message}</p>
                
                {self._generate_detailed_results_html(result)}
            </div>
            """
        
        return html_content
    
    def _generate_detailed_results_html(self, result):
        """Generate detailed results HTML for complex agent results"""
        html = ""
        
        # Handle validation results (for validator agent)
        if 'validation_results' in result:
            html += "<h4>Validation Details:</h4><ul>"
            for validation in result['validation_results']:
                status = validation.get('status', 'UNKNOWN')
                message = validation.get('message', '')
                html += f"<li><strong>{status}:</strong> {message}</li>"
            html += "</ul>"
        
        # Handle test results (for transaction agent)
        if 'test_results' in result:
            html += "<h4>Test Details:</h4><ul>"
            for test in result['test_results']:
                status = test.get('status', 'UNKNOWN')
                test_name = test.get('test', 'Unknown Test')
                message = test.get('message', '')
                html += f"<li><strong>{test_name}:</strong> {status} - {message}</li>"
            html += "</ul>"
        
        # Handle window info (for launcher agent)
        if 'window_info' in result and result['window_info']:
            info = result['window_info']
            html += f"""
            <h4>Application Info:</h4>
            <ul>
                <li><strong>Title:</strong> {info.get('title', 'N/A')}</li>
                <li><strong>Visible:</strong> {info.get('is_visible', 'N/A')}</li>
                <li><strong>Enabled:</strong> {info.get('is_enabled', 'N/A')}</li>
            </ul>
            """
        
        return html
    
    def _generate_screenshots_html(self, screenshots):
        """Generate HTML for screenshots section"""
        if not screenshots:
            return ""
        
        html_content = """
        <div class="section">
            <h2>📸 Screenshots</h2>
            <div class="screenshot-gallery">
        """
        
        for screenshot in screenshots:
            agent = screenshot.get('agent', 'Unknown')
            path = screenshot.get('path', '')
            screenshot_type = screenshot.get('type', 'screenshot')
            
            if path and os.path.exists(path):
                img_base64 = self._image_to_base64(path)
                if img_base64:
                    filename = os.path.basename(path)
                    html_content += f"""
                    <div class="screenshot-item">
                        <div class="screenshot-title">{agent} - {screenshot_type.title()}</div>
                        <img src="{img_base64}" alt="{filename}" title="Click to enlarge">
                        <div style="margin-top: 10px; font-size: 0.8em; color: #666;">{filename}</div>
                    </div>
                    """
        
        html_content += """
            </div>
        </div>
        """
        
        return html_content
    
    def _generate_errors_html(self, errors):
        """Generate HTML for errors section"""
        if not errors:
            return ""
        
        html_content = """
        <div class="section">
            <h2>❌ Errors and Issues</h2>
            <div class="error-list">
        """
        
        for error in errors:
            html_content += f'<div class="error-item">• {error}</div>'
        
        html_content += """
            </div>
        </div>
        """
        
        return html_content
    
    def _generate_recommendations_html(self, recommendations):
        """Generate HTML for recommendations section"""
        html_content = ""
        
        for recommendation in recommendations:
            html_content += f'<div class="recommendation-item">• {recommendation}</div>'
        
        return html_content
    
    def generate_report(self, report_data, output_path):
        """Generate complete HTML report"""
        try:
            # Calculate success rate
            total_tests = report_data.get('total_tests', 0)
            passed_tests = report_data.get('passed_tests', 0)
            success_rate = int((passed_tests / total_tests * 100)) if total_tests > 0 else 0
            
            # Determine overall status class for styling
            overall_status = report_data.get('overall_status', 'UNKNOWN')
            overall_status_class = overall_status.lower() if overall_status.lower() in ['passed', 'failed'] else 'warning'
            
            # Generate sections
            agent_results_content = self._generate_agent_results_html(report_data.get('agent_results', {}))
            screenshots_section = self._generate_screenshots_html(report_data.get('screenshots', []))
            errors_section = self._generate_errors_html(report_data.get('errors', []))
            recommendations_content = self._generate_recommendations_html(report_data.get('recommendations', []))
            
            # Fill template
            html_content = self.template.format(
                timestamp=report_data.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                test_run_id=report_data.get('test_run_id', 'unknown'),
                overall_status=overall_status,
                overall_status_class=overall_status_class,
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=report_data.get('failed_tests', 0),
                success_rate=success_rate,
                summary=report_data.get('summary', 'No summary available'),
                agent_results_content=agent_results_content,
                screenshots_section=screenshots_section,
                errors_section=errors_section,
                recommendations_content=recommendations_content
            )
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write HTML file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML report generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to generate HTML report: {str(e)}")
            return None
    
    def generate_summary_report(self, report_data, output_path):
        """Generate a simplified summary report"""
        try:
            summary_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Health Check Summary</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .header { background: #667eea; color: white; padding: 20px; text-align: center; margin-bottom: 20px; }
        .summary { background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .status-passed { color: #4CAF50; font-weight: bold; }
        .status-failed { color: #f44336; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Health Check Summary</h1>
        <p>{timestamp}</p>
    </div>
    
    <div class="summary">
        <h2>Overall Status: <span class="status-{status_class}">{overall_status}</span></h2>
        <p><strong>Tests:</strong> {passed_tests}/{total_tests} passed ({success_rate}%)</p>
        <p><strong>Summary:</strong> {summary}</p>
    </div>
    
    {errors_html}
</body>
</html>
            """
            
            # Calculate values
            total_tests = report_data.get('total_tests', 0)
            passed_tests = report_data.get('passed_tests', 0)
            success_rate = int((passed_tests / total_tests * 100)) if total_tests > 0 else 0
            overall_status = report_data.get('overall_status', 'UNKNOWN')
            status_class = overall_status.lower() if overall_status.lower() in ['passed', 'failed'] else 'warning'
            
            # Generate errors HTML
            errors = report_data.get('errors', [])
            errors_html = ""
            if errors:
                errors_html = "<div class='summary'><h3>Issues:</h3><ul>"
                for error in errors[:5]:  # Show only first 5 errors
                    errors_html += f"<li>{error}</li>"
                errors_html += "</ul></div>"
            
            # Fill template
            html_content = summary_template.format(
                timestamp=report_data.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                overall_status=overall_status,
                status_class=status_class,
                total_tests=total_tests,
                passed_tests=passed_tests,
                success_rate=success_rate,
                summary=report_data.get('summary', 'No summary available'),
                errors_html=errors_html
            )
            
            # Write file
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Summary report generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to generate summary report: {str(e)}")
            return None