# Test Examples and Use Cases

This document provides comprehensive examples of how to use the Automated Web Testing system for various scenarios.

## 🎯 Basic Examples

### 1. Simple Navigation Test
```
Test Name: Basic Navigation
Target URL: https://example.com

Commands:
1. Navigate to https://example.com
2. Verify the page title contains "Example"
3. Take a screenshot
```

### 2. Form Filling Test
```
Test Name: Contact Form
Target URL: https://httpbin.org/forms/post

Commands:
1. Navigate to https://httpbin.org/forms/post
2. Type "John Smith" in the customer name field
3. Type "john.smith@email.com" in the email field
4. Type "555-0123" in the telephone field
5. Type "This is a test message" in the comments field
6. Click the "Submit" button
7. Verify the page contains "form"
```

## 🛒 E-commerce Testing

### Shopping Cart Flow
```
Test Name: Add to Cart Flow
Target URL: https://demo.opencart.com

Commands:
1. Navigate to https://demo.opencart.com
2. Click on "Cameras" in the navigation menu
3. Click on the first product image
4. Click the "Add to Cart" button
5. Click the "Shopping Cart" link
6. Verify the page contains "Shopping Cart"
7. Verify the page contains "Checkout"
```

### User Registration
```
Test Name: User Registration
Target URL: https://demo.opencart.com

Commands:
1. Navigate to https://demo.opencart.com
2. Click "My Account" in the top navigation
3. Click "Register"
4. Type "John" in the first name field
5. Type "Doe" in the last name field
6. Type "john.doe.test@example.com" in the email field
7. Type "555-0123" in the telephone field
8. Type "password123" in the password field
9. Type "password123" in the password confirm field
10. Click the privacy policy checkbox
11. Click the "Continue" button
```

## 🔐 Authentication Testing

### Login Flow
```
Test Name: Login Test
Target URL: https://the-internet.herokuapp.com/login

Commands:
1. Navigate to https://the-internet.herokuapp.com/login
2. Type "tomsmith" in the username field
3. Type "SuperSecretPassword!" in the password field
4. Click the "Login" button
5. Verify the page contains "You logged into a secure area"
6. Click the "Logout" button
7. Verify the page contains "You logged out of the secure area"
```

### Failed Login Test
```
Test Name: Invalid Login Test
Target URL: https://the-internet.herokuapp.com/login

Commands:
1. Navigate to https://the-internet.herokuapp.com/login
2. Type "invaliduser" in the username field
3. Type "wrongpassword" in the password field
4. Click the "Login" button
5. Verify the page contains "Your username is invalid"
```

## 📝 Form Validation Testing

### Required Field Validation
```
Test Name: Form Validation
Target URL: https://the-internet.herokuapp.com/forgot_password

Commands:
1. Navigate to https://the-internet.herokuapp.com/forgot_password
2. Click the "Retrieve password" button
3. Verify the page contains "Internal Server Error"
4. Go back to the previous page
5. Type "test@example.com" in the email field
6. Click the "Retrieve password" button
7. Verify the page contains "Your e-mail's been sent"
```

## 🎨 UI Interaction Testing

### Dropdown and Selection
```
Test Name: Dropdown Selection
Target URL: https://the-internet.herokuapp.com/dropdown

Commands:
1. Navigate to https://the-internet.herokuapp.com/dropdown
2. Select "Option 1" from the dropdown
3. Verify "Option 1" is selected
4. Select "Option 2" from the dropdown
5. Verify "Option 2" is selected
```

### File Upload Test
```
Test Name: File Upload
Target URL: https://the-internet.herokuapp.com/upload

Commands:
1. Navigate to https://the-internet.herokuapp.com/upload
2. Click the "Choose File" button
3. Upload a test file
4. Click the "Upload" button
5. Verify the page contains "File Uploaded"
```

### Drag and Drop
```
Test Name: Drag and Drop
Target URL: https://the-internet.herokuapp.com/drag_and_drop

Commands:
1. Navigate to https://the-internet.herokuapp.com/drag_and_drop
2. Drag element A to element B
3. Verify the elements have switched positions
4. Take a screenshot
```

## 🔍 Search and Filter Testing

### Search Functionality
```
Test Name: Wikipedia Search
Target URL: https://www.wikipedia.org

Commands:
1. Navigate to https://www.wikipedia.org
2. Type "Playwright" in the search box
3. Click the search button
4. Verify the page title contains "Playwright"
5. Click on the first search result
6. Verify the page contains "browser automation"
```

### Filter and Sort
```
Test Name: Product Filtering
Target URL: https://demo.opencart.com

Commands:
1. Navigate to https://demo.opencart.com
2. Click on "Laptops & Notebooks" in the menu
3. Click "Show All Laptops & Notebooks"
4. Click the "List" view button
5. Select "Name (A - Z)" from the sort dropdown
6. Verify the products are sorted alphabetically
```

## 📱 Responsive Testing

### Mobile View Test
```
Test Name: Mobile Navigation
Target URL: https://example.com

Commands:
1. Navigate to https://example.com
2. Resize browser to mobile width
3. Click the mobile menu button
4. Verify the navigation menu is visible
5. Click a menu item
6. Verify the page navigates correctly
```

## ⚡ Performance Testing

### Page Load Test
```
Test Name: Page Load Performance
Target URL: https://example.com

Commands:
1. Navigate to https://example.com
2. Wait for 2 seconds
3. Verify the page is fully loaded
4. Take a screenshot
5. Navigate to https://example.com/about
6. Wait for 2 seconds
7. Verify the page contains "About"
```

## 🧪 Advanced Testing Scenarios

### Multi-step Workflow
```
Test Name: Complete User Journey
Target URL: https://demo.opencart.com

Commands:
1. Navigate to https://demo.opencart.com
2. Click "My Account" and then "Register"
3. Fill out the registration form with test data
4. Complete the registration process
5. Search for "iPhone"
6. Add the first iPhone to cart
7. Go to checkout
8. Fill out billing information
9. Complete the order process
10. Verify order confirmation
```

### Error Handling Test
```
Test Name: 404 Error Handling
Target URL: https://example.com

Commands:
1. Navigate to https://example.com/nonexistent-page
2. Verify the page contains "404" or "Not Found"
3. Click the home link
4. Verify you're back on the homepage
```

### Session Management
```
Test Name: Session Persistence
Target URL: https://the-internet.herokuapp.com/login

Commands:
1. Navigate to https://the-internet.herokuapp.com/login
2. Login with valid credentials
3. Navigate to a different page
4. Navigate back to the secure area
5. Verify you're still logged in
6. Refresh the page
7. Verify the session persists
```

## 💡 Tips for Writing Effective Tests

### 1. Be Specific with Selectors
Instead of: "Click the button"
Use: "Click the 'Submit' button" or "Click the button with id 'submit-btn'"

### 2. Add Verification Steps
Always verify that actions completed successfully:
```
1. Click the "Login" button
2. Verify the page contains "Welcome" or "Dashboard"
```

### 3. Handle Dynamic Content
For content that loads dynamically:
```
1. Click the "Load Data" button
2. Wait for 3 seconds
3. Verify the data table is populated
```

### 4. Use Screenshots for Visual Verification
```
1. Navigate to the homepage
2. Take a screenshot
3. Click the menu button
4. Take a screenshot to compare
```

### 5. Test Both Success and Failure Paths
Create separate tests for:
- Valid inputs (success path)
- Invalid inputs (error handling)
- Edge cases (boundary conditions)

## 🎯 Best Practices

1. **Keep tests focused**: One test should verify one specific functionality
2. **Use descriptive names**: Test names should clearly indicate what's being tested
3. **Add context**: Include the target URL and brief description
4. **Verify outcomes**: Always check that actions produced expected results
5. **Handle waits**: Add appropriate waits for dynamic content
6. **Clean up**: Log out or reset state when needed
7. **Document assumptions**: Note any prerequisites or setup requirements
