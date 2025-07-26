# Automated Web Application Testing with Natural Language

A comprehensive system that performs automated web application testing using natural language instructions. Convert plain English commands like "Click the login button" into actual Playwright test actions.

## 🚀 Features

- **Natural Language Processing**: Convert plain English commands into test actions using OpenAI GPT
- **Playwright Integration**: Execute tests on real websites with full browser automation
- **Visual Dashboard**: Clean React-based interface for creating tests and viewing results
- **Screenshot Capture**: Automatic screenshots for each test step and failures
- **Test History**: Track and manage all your test sessions
- **Real-time Execution**: Watch tests run in real-time with live status updates
- **Comprehensive Reporting**: Detailed results with execution times and error messages

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Playwright    │
│   (React)       │◄──►│   (Node.js)     │◄──►│   Engine        │
│                 │    │                 │    │                 │
│ • Dashboard     │    │ • NLP Service   │    │ • Browser       │
│ • Test Creator  │    │ • Test Executor │    │ • Screenshots   │
│ • Results View  │    │ • Database      │    │ • Actions       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   OpenAI API    │
                       │   (GPT-4)       │
                       └─────────────────┘
```

## 📋 Prerequisites

- Node.js 18+ and npm
- OpenAI API key
- Git

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd automation-testing
```

### 2. Install Dependencies

```bash
# Install root dependencies
npm install

# Install client dependencies
npm run install:all
```

### 3. Environment Setup

```bash
# Copy environment template
cp .env.example .env
```

Edit `.env` file with your configuration:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
PORT=3001
NODE_ENV=development

# Database Configuration
DB_PATH=./data/tests.db

# Playwright Configuration
HEADLESS=false
BROWSER_TYPE=chromium
DEFAULT_TIMEOUT=30000
```

### 4. Install Playwright Browsers

```bash
npx playwright install
```

## 🚀 Running the Application

### Development Mode

```bash
# Start both frontend and backend
npm run dev
```

This will start:
- Backend API server on `http://localhost:3001`
- Frontend React app on `http://localhost:3000`

### Production Mode

```bash
# Build frontend
npm run client:build

# Start backend server
npm run server:start
```

## 📖 Usage Guide

### Creating Your First Test

1. **Navigate to Create Test**: Click "Create Test" in the navigation
2. **Fill Test Details**:
   - **Test Name**: Give your test a descriptive name
   - **Description**: Optional description of what the test does
   - **Target URL**: The website you want to test
3. **Add Commands**: Write natural language commands like:
   - "Navigate to https://example.com"
   - "Click the 'Login' button"
   - "Type 'user@example.com' in the email field"
   - "Verify the page contains 'Welcome'"
4. **Run Test**: Click "Create & Run Test"

### Supported Commands

#### Navigation
- "Navigate to https://example.com"
- "Go to the homepage"

#### Clicking
- "Click the login button"
- "Click on 'Submit'"
- "Click the element with id 'submit-btn'"

#### Typing
- "Type 'hello world' in the search box"
- "Enter 'user@example.com' in the email field"
- "Fill the password field with 'secret123'"

#### Verification
- "Verify the page title contains 'Dashboard'"
- "Check that the page contains 'Welcome'"
- "Verify the element '#success-message' is visible"

#### Waiting
- "Wait for 3 seconds"
- "Wait for the loading spinner to disappear"
- "Wait for the '#content' element to appear"

#### Other Actions
- "Scroll to the bottom of the page"
- "Hover over the menu item"
- "Select 'Option 1' from the dropdown"
- "Take a screenshot"

### Viewing Results

After running a test, you'll see:
- **Overall Status**: Pass/Fail status with summary statistics
- **Step-by-Step Results**: Each command with its execution status
- **Screenshots**: Visual proof of each step
- **Error Messages**: Detailed error information for failed steps
- **Execution Times**: Performance metrics for each step

## 🧪 Testing

### Run Unit Tests

```bash
npm test
```

### Run E2E Tests

```bash
npx playwright test
```

## 📁 Project Structure

```
automation-testing/
├── client/                 # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── App.js
│   └── package.json
├── server/                 # Node.js backend
│   ├── database/           # Database setup
│   ├── routes/             # API routes
│   ├── services/           # Business logic
│   │   ├── nlpService.js   # Natural language processing
│   │   └── testExecutor.js # Playwright test execution
│   ├── tests/              # Unit tests
│   ├── utils/              # Utilities
│   └── index.js
├── screenshots/            # Test screenshots
├── logs/                   # Application logs
├── data/                   # SQLite database
├── .env.example           # Environment template
├── package.json
└── README.md
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for NLP | Required |
| `PORT` | Backend server port | 3001 |
| `NODE_ENV` | Environment mode | development |
| `DB_PATH` | SQLite database path | ./data/tests.db |
| `HEADLESS` | Run browser in headless mode | false |
| `BROWSER_TYPE` | Browser type (chromium/firefox/webkit) | chromium |
| `DEFAULT_TIMEOUT` | Default action timeout (ms) | 30000 |

### Playwright Configuration

Edit `playwright.config.js` to customize:
- Browser types and devices
- Test timeouts
- Screenshot settings
- Trace collection

## 🐛 Troubleshooting

### Common Issues

1. **OpenAI API Errors**
   - Verify your API key is correct
   - Check your OpenAI account has sufficient credits
   - Ensure you have access to GPT-4

2. **Playwright Browser Issues**
   - Run `npx playwright install` to install browsers
   - Check if your system supports the selected browser type

3. **Database Errors**
   - Ensure the `data/` directory exists and is writable
   - Delete `data/tests.db` to reset the database

4. **Port Conflicts**
   - Change `PORT` in `.env` if 3001 is already in use
   - Update the proxy setting in `client/package.json`

### Debug Mode

Enable debug logging:

```bash
# Set log level to debug
LOG_LEVEL=debug npm run dev
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Playwright](https://playwright.dev/) for browser automation
- [OpenAI](https://openai.com/) for natural language processing
- [React](https://reactjs.org/) for the frontend framework
- [Express.js](https://expressjs.com/) for the backend API
