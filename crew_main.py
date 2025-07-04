#!/usr/bin/env python3
"""
Main entry point for the Bank Application Health Check Automation
Using CrewAI for agent orchestration and task management
"""

import os
import sys
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from crewai import Crew, Agent, Task

# Import custom agents
from agents.launcher import AppLauncherAgent
from agents.login import LoginAgent
from agents.validator import ScreenValidatorAgent
from agents.transaction import TransactionAgent
from agents.reporter import ReporterAgent

# Import utilities
from utils.visual_diff import VisualDiffValidator
from utils.ocr_validation import OCRValidator
from utils.html_report import HTMLReportGenerator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/health_check.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class BankAppHealthChecker:
    """Main orchestrator for bank application health check automation"""
    
    def __init__(self):
        self.config = self.load_config()
        self.setup_directories()
        self.initialize_agents()
        
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            with open('config/confluence_flows.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("Configuration file not found. Creating default config.")
            return self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration"""
        default_config = {
            "app_config": {
                "app_path": "C:\\Program Files\\BankApp\\BankApp.exe",
                "app_title": "Bank Application",
                "timeout": 30
            },
            "test_flows": [
                {
                    "name": "login_flow",
                    "description": "Validate login functionality",
                    "steps": [
                        {"action": "launch_app", "expected": "app_launched"},
                        {"action": "enter_credentials", "expected": "dashboard_visible"},
                        {"action": "validate_dashboard", "expected": "dashboard_elements_present"}
                    ]
                },
                {
                    "name": "transaction_flow",
                    "description": "Validate transaction screens",
                    "steps": [
                        {"action": "navigate_to_transactions", "expected": "transaction_screen"},
                        {"action": "validate_transaction_elements", "expected": "elements_present"},
                        {"action": "return_to_dashboard", "expected": "dashboard_visible"}
                    ]
                }
            ],
            "validation": {
                "similarity_threshold": 0.85,
                "ocr_confidence_threshold": 60
            }
        }
        
        # Save default config
        os.makedirs('config', exist_ok=True)
        with open('config/confluence_flows.json', 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def setup_directories(self):
        """Create necessary directories"""
        directories = ['logs', 'reports', 'screenshots', 'baseline']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def initialize_agents(self):
        """Initialize all CrewAI agents"""
        # App Launcher Agent
        self.launcher_agent = Agent(
            role="Application Launcher",
            goal="Launch and initialize the bank application",
            backstory="Expert in application startup and initialization processes",
            verbose=True,
            allow_delegation=False
        )
        
        # Login Agent
        self.login_agent = Agent(
            role="Login Specialist",
            goal="Handle authentication and login processes",
            backstory="Security-focused agent specializing in authentication workflows",
            verbose=True,
            allow_delegation=False
        )
        
        # Screen Validator Agent
        self.validator_agent = Agent(
            role="Screen Validator",
            goal="Validate UI elements and screen content using visual and semantic analysis",
            backstory="Expert in visual testing and UI validation with AI-powered analysis",
            verbose=True,
            allow_delegation=False
        )
        
        # Transaction Agent
        self.transaction_agent = Agent(
            role="Transaction Tester",
            goal="Navigate and validate transaction-related screens and workflows",
            backstory="Specialist in financial transaction testing and validation",
            verbose=True,
            allow_delegation=False
        )
        
        # Reporter Agent
        self.reporter_agent = Agent(
            role="Report Generator",
            goal="Generate comprehensive health check reports",
            backstory="Documentation expert specializing in test result analysis and reporting",
            verbose=True,
            allow_delegation=False
        )
    
    def create_tasks(self):
        """Create tasks for each agent based on configuration"""
        tasks = []
        
        # App Launch Task
        launch_task = Task(
            description="Launch the bank application and verify it starts successfully",
            agent=self.launcher_agent,
            expected_output="Application launched and ready for testing"
        )
        tasks.append(launch_task)
        
        # Login Task
        login_task = Task(
            description="Perform login using test credentials and validate dashboard access",
            agent=self.login_agent,
            expected_output="Successfully logged in and dashboard is accessible"
        )
        tasks.append(login_task)
        
        # Screen Validation Task
        validation_task = Task(
            description="Validate critical screens using visual comparison and LLM analysis",
            agent=self.validator_agent,
            expected_output="All critical screens validated with pass/fail status"
        )
        tasks.append(validation_task)
        
        # Transaction Testing Task
        transaction_task = Task(
            description="Test transaction-related screens and workflows",
            agent=self.transaction_agent,
            expected_output="Transaction workflows tested and validated"
        )
        tasks.append(transaction_task)
        
        # Reporting Task
        report_task = Task(
            description="Generate comprehensive HTML report with test results",
            agent=self.reporter_agent,
            expected_output="HTML report generated with all test results and screenshots"
        )
        tasks.append(report_task)
        
        return tasks
    
    def run_health_check(self):
        """Execute the complete health check workflow"""
        logger.info("Starting Bank Application Health Check")
        
        try:
            # Create tasks
            tasks = self.create_tasks()
            
            # Create crew
            crew = Crew(
                agents=[
                    self.launcher_agent,
                    self.login_agent,
                    self.validator_agent,
                    self.transaction_agent,
                    self.reporter_agent
                ],
                tasks=tasks,
                verbose=True
            )
            
            # Execute the crew
            result = crew.kickoff()
            
            logger.info("Health check completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            # Generate error report
            self.generate_error_report(str(e))
            return None
    
    def generate_error_report(self, error_message):
        """Generate error report when health check fails"""
        report_generator = HTMLReportGenerator()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        error_data = {
            "timestamp": timestamp,
            "status": "FAILED",
            "error": error_message,
            "tests": []
        }
        
        report_path = f"reports/error_report_{timestamp}.html"
        report_generator.generate_report(error_data, report_path)
        logger.info(f"Error report generated: {report_path}")

def main():
    """Main entry point"""
    print("🏦 Bank Application Health Check Automation")
    print("=" * 50)
    
    # Initialize health checker
    health_checker = BankAppHealthChecker()
    
    # Run health check
    result = health_checker.run_health_check()
    
    if result:
        print("✅ Health check completed successfully")
        print(f"📊 Report available in: reports/")
    else:
        print("❌ Health check failed")
        print("🔍 Check logs for details")

if __name__ == "__main__":
    main()