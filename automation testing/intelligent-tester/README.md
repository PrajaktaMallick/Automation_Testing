# 🤖 Intelligent Web Tester

An advanced AI-powered web testing system that converts natural language prompts into executable browser automation tests. Built with FastAPI, React, Playwright, and integrated with MCP (Model Context Protocol) for intelligent test planning.

## 🌟 Features

### 🧠 AI-Powered Testing
- **Natural Language Processing**: Convert plain English into test actions
- **MCP Integration**: Advanced prompt understanding and context awareness
- **Intelligent Element Detection**: Smart selectors with multiple fallback strategies
- **Context-Aware Planning**: Website analysis for optimized test execution

### 🎯 Advanced Automation
- **Multi-Browser Support**: Chromium, Firefox, and WebKit
- **Dynamic Content Handling**: Smart waits and element detection
- **Error Recovery**: Automatic retries and fallback mechanisms
- **Screenshot Capture**: Visual documentation of every step

### 📊 Real-Time Monitoring
- **Live Execution Tracking**: Watch tests run in real-time
- **Progress Indicators**: Visual feedback on test completion
- **Performance Metrics**: Detailed timing and success rate analytics
- **WebSocket Updates**: Real-time status updates

### 🎨 Modern Interface
- **React + Tailwind CSS**: Beautiful, responsive design
- **Interactive Dashboard**: Comprehensive test management
- **Screenshot Gallery**: Visual test result browsing
- **Analytics & Insights**: Performance trends and recommendations

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │   FastAPI       │    │   Playwright    │
│   (Port 3000)   │◄──►│   Backend       │◄──►│   Browser       │
│                 │    │   (Port 8000)   │    │   Engine        │
│ • Dashboard     │    │                 │    │                 │
│ • Test Creator  │    │ • Action        │    │ • Smart Element │
│ • Results View  │    │   Planner       │    │   Detection     │
│ • Analytics     │    │ • Test          │    │ • Screenshot    │
└─────────────────┘    │   Orchestrator  │    │   Capture       │
                       │ • Session Mgmt  │    │ • Multi-Browser │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   AI Services   │
                       │                 │
                       │ • OpenAI GPT-4  │
                       │ • Anthropic     │
                       │ • MCP Protocol  │
                       └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** with pip
- **Node.js 18+** with npm
- **Git**
- **OpenAI API Key** (optional but recommended)

### 1. Clone Repository

```bash
git clone <repository-url>
cd intelligent-tester
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# At minimum, set OPENAI_API_KEY for full AI features
```

### 3. Install Dependencies

```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Install Playwright browsers
python -m playwright install

# Install Node.js dependencies
npm run install:all
```

### 4. Start the Application

```bash
# Start both backend and frontend
npm run dev
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📖 Usage Guide

### Creating Your First Test

1. **Navigate to Create Test** (http://localhost:3000/create)
2. **Enter Target Website**: e.g., `https://www.flipkart.com`
3. **Analyze Website** (optional): Click "Analyze" to understand site structure
4. **Write Test Prompt**: Describe what you want to test in plain English

### Example Prompts

#### E-commerce Testing
```
Login with jyoti@test.com / 123456, then search for headphones and add first result to cart
```

#### Form Testing
```
Go to the contact page, fill out the form with test data, and submit it
```

#### Navigation Testing
```
Click the third image on the homepage and proceed to checkout
```

#### Authentication Testing
```
Test if logging out works after adding an item to cart
```

### Supported Commands

The AI understands various action types:

- **Navigation**: "Go to", "Navigate to", "Visit"
- **Clicking**: "Click", "Press", "Select"
- **Typing**: "Type", "Enter", "Fill"
- **Verification**: "Verify", "Check", "Confirm"
- **Waiting**: "Wait for", "Pause"
- **Scrolling**: "Scroll to", "Scroll down"

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 | - | Recommended |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | - | Optional |
| `MCP_SERVER_URL` | MCP server endpoint | - | Optional |
| `BACKEND_PORT` | Backend server port | 8000 | No |
| `HEADLESS` | Run browser in headless mode | false | No |
| `BROWSER_TYPE` | Browser type (chromium/firefox/webkit) | chromium | No |
| `DEFAULT_TIMEOUT` | Default action timeout (ms) | 30000 | No |

### Browser Configuration

```env
# Browser settings
HEADLESS=false                    # Set to true for headless mode
BROWSER_TYPE=chromium            # chromium, firefox, or webkit
VIEWPORT_WIDTH=1280              # Browser viewport width
VIEWPORT_HEIGHT=720              # Browser viewport height
DEFAULT_TIMEOUT=30000            # Default timeout in milliseconds
```

### AI Model Configuration

```env
# AI settings
DEFAULT_MODEL=gpt-4              # OpenAI model to use
TEMPERATURE=0.1                  # Model temperature (0-1)
MAX_TOKENS=2000                  # Maximum response tokens
```

## 🧪 Example Test Scenarios

### 1. Flipkart Shopping Flow
```
Website: https://www.flipkart.com
Prompt: Login with test@example.com / password123, search for "wireless headphones", filter by price under 2000, and add the first result to cart
```

### 2. GitHub Repository Testing
```
Website: https://github.com
Prompt: Go to the search page, search for "playwright", click on the first repository, and check if it has a README file
```

### 3. Form Submission Testing
```
Website: https://httpbin.org/forms/post
Prompt: Fill out the contact form with name "John Doe", email "john@example.com", and message "Test message", then submit
```

### 4. E-commerce Checkout Flow
```
Website: https://demo.opencart.com
Prompt: Add a camera to cart, go to checkout, fill billing details, and proceed to payment options
```

## 📊 Features in Detail

### Intelligent Element Detection

The system uses multiple strategies to find elements:

1. **AI-Generated Selectors**: Context-aware CSS selectors
2. **Fallback Strategies**: Multiple selector attempts
3. **Text-Based Detection**: Natural language element finding
4. **Accessibility Attributes**: ARIA labels and roles
5. **Visual Recognition**: Screenshot-based element location

### Real-Time Execution Monitoring

- **Live Progress**: Watch tests execute step by step
- **Screenshot Capture**: Visual proof of each action
- **Error Handling**: Automatic retries and detailed error messages
- **Performance Metrics**: Execution time and success rates

### Advanced Test Planning

- **Website Analysis**: Automatic site structure detection
- **Context Awareness**: Intelligent action sequencing
- **Risk Assessment**: Identify potentially dangerous actions
- **Optimization**: Reduce redundant actions and improve reliability

## 🛠️ Development

### Project Structure

```
intelligent-tester/
├── backend/                 # FastAPI backend
│   ├── main.py             # Application entry point
│   ├── models/             # Data models
│   ├── services/           # Business logic
│   │   ├── mcp_client.py   # MCP integration
│   │   ├── action_planner.py # AI action planning
│   │   ├── browser_engine.py # Playwright automation
│   │   └── test_orchestrator.py # Test coordination
│   └── utils/              # Utilities
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   └── services/       # API services
│   └── public/
├── screenshots/            # Test screenshots
├── logs/                   # Application logs
└── docs/                   # Documentation
```

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests
cd frontend
npm test

# End-to-end tests
npm run test:e2e
```

### API Documentation

Visit http://localhost:8000/docs for interactive API documentation.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Playwright](https://playwright.dev/) - Browser automation
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://reactjs.org/) - Frontend framework
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- [OpenAI](https://openai.com/) - AI language models
- [Anthropic](https://anthropic.com/) - Claude AI models

## 🆘 Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](issues/)
- 💬 [Discussions](discussions/)
- 📧 Email: support@example.com

---

**Built with ❤️ for the testing community**
