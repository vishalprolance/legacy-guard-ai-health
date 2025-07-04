# Bank Application Health Check Automation

🏦 **Agentic AI-powered automation framework for legacy desktop banking application health checks**

This project implements a comprehensive health check system using **CrewAI** agents to automatically test and validate a bank's legacy Windows desktop application. The system performs daily health checks with minimal server load while providing detailed reporting and AI-powered analysis.

## 🎯 Key Features

- **Agentic Architecture**: Uses CrewAI framework with specialized agents for different testing aspects
- **Visual Validation**: SSIM-based screenshot comparison with baseline images
- **OCR Text Extraction**: Tesseract-powered text validation and verification
- **AI Semantic Analysis**: Local LLM integration for intelligent UI validation
- **Comprehensive Reporting**: HTML reports with screenshots, analysis, and recommendations
- **Production-Safe**: Designed for off-peak execution without affecting live systems

## 🏗️ Architecture

### Agents

1. **App Launcher Agent** - Handles application startup and initialization
2. **Login Agent** - Manages authentication and credential entry
3. **Screen Validator Agent** - Performs visual, OCR, and semantic validation
4. **Transaction Agent** - Tests transaction workflows and form interactions
5. **Reporter Agent** - Generates comprehensive HTML and JSON reports

### Core Technologies

- **CrewAI** - Agent orchestration and task management
- **pywinauto** - Windows desktop application automation
- **pytesseract** - OCR text extraction
- **OpenCV + scikit-image** - Image processing and comparison
- **Local LLM API** - AI-powered semantic analysis
- **Python 3.8+** - Core runtime

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd bank_app_health_check

# Run automated setup
python setup.py
```

### 2. Configuration

Edit `.env` file with your specific settings:

```env
# Application settings
APP_PATH=C:\Program Files\BankApp\BankApp.exe
APP_TITLE=Bank Application

# Test credentials
TEST_USERNAME=testuser
TEST_PASSWORD=testpassword

# Local LLM configuration
LLM_API_URL=http://localhost:8000/v1/chat/completions
LLM_API_KEY=your-local-llm-api-key
LLM_MODEL_NAME=gpt-4-turbo
```

### 3. Run Health Check

```bash
# Execute complete health check
python crew_main.py

# View reports
open reports/health_check_[timestamp].html
```

## 📁 Project Structure

```
bank_app_health_check/
├── crew_main.py                 # Main orchestrator
├── agents/                      # CrewAI agents
│   ├── launcher.py              # App launch agent
│   ├── login.py                 # Authentication agent
│   ├── validator.py             # Screen validation agent
│   ├── transaction.py           # Transaction testing agent
│   └── reporter.py              # Report generation agent
├── utils/                       # Utility modules
│   ├── visual_diff.py           # Visual comparison tools
│   ├── ocr_validation.py        # OCR processing
│   └── html_report.py           # Report generation
├── config/                      # Configuration files
│   └── confluence_flows.json    # Test flow definitions
├── baseline/                    # Baseline screenshots
├── screenshots/                 # Runtime screenshots
├── reports/                     # Generated reports
├── logs/                        # Application logs
├── requirements.txt             # Python dependencies
├── setup.py                     # Automated setup script
└── .env.example                 # Environment template
```

## 🔧 Configuration

### Test Flow Configuration

Edit `config/confluence_flows.json` to define your test scenarios:

```json
{
  "test_flows": [
    {
      "name": "login_flow",
      "description": "Complete login process validation",
      "priority": "HIGH",
      "steps": [
        {
          "action": "locate_login_fields",
          "expected": "username_and_password_fields_found",
          "timeout": 10
        }
      ]
    }
  ],
  "validation": {
    "similarity_threshold": 0.85,
    "ocr_confidence_threshold": 60
  }
}
```

### Baseline Images

1. Run initial health check to capture screenshots
2. Review captured screenshots in `screenshots/` folder
3. Copy approved screenshots to `baseline/` folder for future comparisons

## 📊 Reports

The system generates comprehensive reports including:

- **Executive Summary** - Overall health status and key metrics
- **Agent Results** - Detailed results from each testing agent
- **Visual Comparisons** - Screenshot differences and similarity scores
- **OCR Analysis** - Text extraction results and validations
- **AI Insights** - Semantic analysis from local LLM
- **Recommendations** - Actionable improvement suggestions

### Sample Report Structure

```html
🏦 Bank Application Health Check
├── 📊 Summary (4/4 tests passed - 100% success rate)
├── 🤖 Agent Results
│   ├── ✅ App Launcher - Application launched successfully
│   ├── ✅ Login Agent - Authentication completed
│   ├── ✅ Screen Validator - All screens validated
│   └── ✅ Transaction Agent - Workflows tested
├── 📸 Screenshots (with clickable enlargement)
└── 💡 Recommendations
```

## 🔒 Security & Production Considerations

### Security Features
- Credential masking in logs and reports
- Secure screenshot storage with access controls
- Test-only credentials (no production data)
- Configurable sensitive data exclusion

### Production Safety
- Off-peak execution scheduling
- Single user simulation to minimize load
- Read-only operations (no actual transactions)
- Graceful error handling and recovery
- Automatic application cleanup

## 🛠️ Advanced Usage

### Custom Agent Development

```python
from crewai import Agent, Task

# Create custom validation agent
custom_agent = Agent(
    role="Custom Validator",
    goal="Validate specific business rules",
    backstory="Expert in domain-specific validation",
    verbose=True
)

# Add to crew
crew.agents.append(custom_agent)
```

### Extending Visual Validation

```python
# Add custom visual elements
validator.validate_visual_elements(
    screenshot_path,
    expected_elements=['custom_button.png', 'logo.png']
)
```

### LLM Integration

```python
# Custom semantic analysis prompt
semantic_result = validator.perform_llm_semantic_analysis(
    screenshot_path,
    context="loan application screen validation"
)
```

## 📅 Scheduling & Automation

### Windows Task Scheduler

```batch
# Create scheduled task for daily execution
schtasks /create /tn "BankHealthCheck" /tr "python C:\path\to\crew_main.py" /sc daily /st 02:00
```

### Service Deployment

```python
# Run as Windows service (using python-windows-service)
import servicemanager
import win32service

class HealthCheckService(win32service.ServiceFramework):
    def main(self):
        # Execute health check
        pass
```

## 🐛 Troubleshooting

### Common Issues

1. **Application Not Found**
   ```
   Solution: Update APP_PATH in .env file
   Check: Verify application installation path
   ```

2. **OCR Not Working**
   ```
   Solution: Install Tesseract OCR
   Windows: Download from GitHub releases
   Update: TESSERACT_CMD path in .env
   ```

3. **LLM Connection Failed**
   ```
   Solution: Verify LLM_API_URL is accessible
   Check: API key and model name configuration
   Test: curl http://localhost:8000/v1/models
   ```

4. **Screenshots Empty/Black**
   ```
   Solution: Check application focus and visibility
   Update: Window title matching in config
   Try: Different screen capture methods
   ```

### Debug Mode

```bash
# Enable verbose logging
DEBUG_MODE=true python crew_main.py

# View detailed logs
tail -f logs/health_check.log
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🆘 Support

- **Documentation**: Check inline code comments and docstrings
- **Issues**: Create GitHub issue with error logs and configuration
- **Discussions**: Use GitHub Discussions for questions and suggestions

## 🔮 Roadmap

- [ ] **Multi-application Support** - Test multiple banking applications
- [ ] **API Integration** - REST API for remote health check triggering
- [ ] **Dashboard UI** - Streamlit-based monitoring dashboard
- [ ] **ML Anomaly Detection** - Automatic detection of UI anomalies
- [ ] **Cloud Deployment** - Azure/AWS deployment options
- [ ] **Performance Metrics** - Application performance monitoring
- [ ] **Integration Testing** - End-to-end workflow validation

---

**🏦 Built for banking reliability, powered by AI intelligence**