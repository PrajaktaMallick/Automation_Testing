# Quick Setup Guide

This guide will help you get the Automated Web Testing system up and running in under 10 minutes.

## 🚀 Quick Start

### Step 1: Prerequisites Check

Ensure you have:
- [ ] Node.js 18+ installed (`node --version`)
- [ ] npm installed (`npm --version`)
- [ ] OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Step 2: Installation

```bash
# 1. Navigate to your project directory
cd automation-testing

# 2. Install all dependencies
npm run install:all

# 3. Install Playwright browsers
npx playwright install chromium
```

### Step 3: Configuration

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Edit .env file with your OpenAI API key
# Replace 'your_openai_api_key_here' with your actual API key
```

**Required .env changes:**
```env
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

### Step 4: Start the Application

```bash
# Start both frontend and backend
npm run dev
```

Wait for both servers to start:
- ✅ Backend: `Server running on http://localhost:3001`
- ✅ Frontend: `webpack compiled successfully`

### Step 5: Access the Application

Open your browser and go to: **http://localhost:3000**

## 🧪 Test Your Setup

### Create a Simple Test

1. Click **"Create Test"** in the navigation
2. Fill in the form:
   - **Test Name**: "Google Search Test"
   - **Target URL**: "https://www.google.com"
   - **Commands**:
     ```
     Navigate to https://www.google.com
     Type "playwright testing" in the search box
     Click the "Google Search" button
     Verify the page contains "results"
     ```
3. Click **"Create & Run Test"**
4. Watch your test execute!

## 🔧 Troubleshooting

### Issue: "OpenAI API key not found"
**Solution**: Make sure your `.env` file has the correct API key:
```env
OPENAI_API_KEY=sk-your-actual-key-here
```

### Issue: "Port 3001 already in use"
**Solution**: Change the port in `.env`:
```env
PORT=3002
```
Then update `client/package.json` proxy setting to match.

### Issue: "Playwright browser not found"
**Solution**: Install browsers:
```bash
npx playwright install
```

### Issue: Frontend won't load
**Solution**: 
1. Check if both servers are running
2. Try accessing backend directly: http://localhost:3001/health
3. Clear browser cache and reload

## 📱 What's Next?

Once your setup is working:

1. **Explore the Dashboard**: View test statistics and recent tests
2. **Try Different Commands**: Experiment with various natural language commands
3. **Check Test History**: View all your past test runs
4. **Examine Screenshots**: See visual proof of each test step

## 🎯 Example Test Scenarios

### E-commerce Login Test
```
Navigate to https://demo.opencart.com
Click "My Account"
Click "Login"
Type "test@example.com" in the email field
Type "password123" in the password field
Click the "Login" button
Verify the page contains "My Account"
```

### Form Submission Test
```
Navigate to https://httpbin.org/forms/post
Type "John Doe" in the customer name field
Type "john@example.com" in the email field
Type "555-1234" in the telephone field
Click the "Submit" button
Verify the page contains "form"
```

### Search Functionality Test
```
Navigate to https://www.wikipedia.org
Type "artificial intelligence" in the search box
Click the "Search" button
Verify the page title contains "Artificial intelligence"
Take a screenshot
```

## 🆘 Need Help?

- Check the main README.md for detailed documentation
- Look at the browser console for error messages
- Check the terminal output for server errors
- Verify your OpenAI API key has sufficient credits

## ✅ Setup Complete!

You're now ready to create automated web tests using natural language! 🎉
