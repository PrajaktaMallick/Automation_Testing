# 🚀 Quick Setup Guide

Get the Intelligent Web Tester running in under 10 minutes!

## ✅ Prerequisites Check

Before starting, ensure you have:

- [ ] **Python 3.9+** (`python --version`)
- [ ] **Node.js 18+** (`node --version`)
- [ ] **npm** (`npm --version`)
- [ ] **Git** (`git --version`)
- [ ] **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys)) - Optional but recommended

## 🏃‍♂️ Quick Installation

### Step 1: Clone and Navigate

```bash
git clone <repository-url>
cd intelligent-tester
```

### Step 2: Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API keys
# Replace 'your_openai_api_key_here' with your actual API key
```

**Required .env changes:**
```env
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

### Step 3: Install Dependencies

```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Install Playwright browsers
python -m playwright install chromium

# Install Node.js dependencies
cd frontend && npm install && cd ..
```

### Step 4: Start the Application

```bash
# Start both backend and frontend
npm run dev
```

Wait for both servers to start:
- ✅ Backend: `INFO: Uvicorn running on http://0.0.0.0:8000`
- ✅ Frontend: `webpack compiled successfully`

### Step 5: Access the Application

Open your browser and go to: **http://localhost:3000**

## 🧪 Test Your Setup

### Create a Simple Test

1. Click **"Create Test"** in the navigation
2. Fill in the form:
   - **Website URL**: `https://example.com`
   - **Test Prompt**: 
     ```
     Navigate to https://example.com
     Verify the page title contains "Example"
     Take a screenshot
     ```
3. Click **"Create & Run Test"**
4. Watch your test execute!

## 🔧 Troubleshooting

### Common Issues

#### Issue: "OpenAI API key not found"
**Solution**: Make sure your `.env` file has the correct API key:
```env
OPENAI_API_KEY=sk-your-actual-key-here
```

#### Issue: "Port 8000 already in use"
**Solution**: Change the port in `.env`:
```env
BACKEND_PORT=8001
```

#### Issue: "Playwright browser not found"
**Solution**: Install browsers:
```bash
python -m playwright install
```

#### Issue: "Module not found" errors
**Solution**: Ensure all dependencies are installed:
```bash
pip install -r backend/requirements.txt
cd frontend && npm install
```

#### Issue: Frontend won't load
**Solution**: 
1. Check if both servers are running
2. Try accessing backend directly: http://localhost:8000/health
3. Clear browser cache and reload

### Debug Mode

Enable debug logging:
```bash
# Set environment variable
export LOG_LEVEL=debug

# Or add to .env file
LOG_LEVEL=debug
```

## 🎯 What's Next?

Once your setup is working:

1. **Explore the Dashboard**: View test statistics and recent tests
2. **Try Different Websites**: Test various sites like GitHub, Amazon, etc.
3. **Experiment with Prompts**: Try complex multi-step test scenarios
4. **Check Analytics**: View performance metrics and insights
5. **Review Screenshots**: See visual proof of test execution

## 📱 Example Test Scenarios

### E-commerce Flow (Flipkart)
```
Website: https://www.flipkart.com
Prompt: Search for "wireless mouse", filter by price under 1000, and add the first result to cart
```

### GitHub Repository Test
```
Website: https://github.com
Prompt: Search for "playwright", click on the first repository, and verify it has a README file
```

### Form Testing
```
Website: https://httpbin.org/forms/post
Prompt: Fill out the form with name "Test User", email "test@example.com", and submit
```

## 🔍 Verification Steps

### 1. Backend Health Check
```bash
curl http://localhost:8000/health
```
Expected response:
```json
{"status": "healthy", "timestamp": "..."}
```

### 2. Frontend Loading
- Navigate to http://localhost:3000
- Should see the dashboard with navigation sidebar
- No console errors in browser developer tools

### 3. API Documentation
- Visit http://localhost:8000/docs
- Should see interactive Swagger documentation

### 4. Test Creation
- Create a simple test as described above
- Should see test execution progress
- Should receive screenshots and results

## 🚨 Need Help?

If you encounter issues:

1. **Check the logs**: Look in `logs/` directory for error messages
2. **Verify prerequisites**: Ensure all required software is installed
3. **Check network**: Ensure you can access external websites
4. **Review environment**: Double-check your `.env` configuration
5. **Restart services**: Sometimes a fresh restart helps

### Getting Support

- 📖 Check the main [README.md](README.md) for detailed documentation
- 🐛 Report issues on the GitHub issue tracker
- 💬 Join our community discussions
- 📧 Contact support for urgent issues

## ✅ Setup Complete!

You're now ready to create intelligent web tests using natural language! 🎉

### Quick Tips for Success

- **Be specific** in your test prompts
- **Include test data** like emails and passwords
- **Use real websites** for more realistic testing
- **Check screenshots** to verify test execution
- **Review analytics** to improve test reliability

Happy testing! 🚀
