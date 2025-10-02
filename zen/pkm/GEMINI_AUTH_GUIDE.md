# Google Gemini Authentication Guide

This guide explains how to obtain the required cookies and tokens for accessing Google Gemini conversations through the PKM module.

## 🔐 Required Authentication Data

The PKM module needs two pieces of authentication data:

1. **Session Cookie** (`GEMINI_SESSION_COOKIE`)
2. **CSRF Token** (`GEMINI_CSRF_TOKEN`)

## 📋 Step-by-Step Instructions

### Method 1: Using Browser Developer Tools (Recommended)

1. **Open Google Gemini**
   - Go to [https://gemini.google.com](https://gemini.google.com)
   - Sign in to your Google account
   - Make sure you can see your conversations

2. **Open Developer Tools**
   - Press `F12` or right-click → "Inspect"
   - Go to the **Network** tab
   - Make sure "Preserve log" is checked

3. **Trigger a Request**
   - Refresh the page or click on a conversation
   - Look for requests to `gemini.google.com` in the Network tab

4. **Find the Session Cookie**
   - Click on any request to `gemini.google.com`
   - Go to the **Headers** tab
   - Look for `Cookie:` header
   - Copy the entire cookie string (it will be very long)

5. **Find the CSRF Token**
   - Look for requests that contain `X-Goog-Csrf-Token` in headers
   - Or look for `csrf_token` in request parameters
   - Copy the token value

### Method 2: Using Browser Extensions

1. **Install Cookie Editor Extension**
   - Chrome: [Cookie Editor](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)
   - Firefox: [Cookie Editor](https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/)

2. **Navigate to Gemini**
   - Go to [https://gemini.google.com](https://gemini.google.com)
   - Sign in and access your conversations

3. **Extract Cookies**
   - Click the Cookie Editor extension icon
   - Find cookies for `gemini.google.com`
   - Look for cookies like `__Secure-1PSID`, `__Secure-3PSID`, etc.
   - Copy the cookie values

### Method 3: Using Browser Console

1. **Open Gemini and Developer Tools**
   - Go to [https://gemini.google.com](https://gemini.google.com)
   - Open Developer Tools (`F12`)
   - Go to **Console** tab

2. **Run JavaScript Commands**
   ```javascript
   // Get all cookies
   document.cookie
   
   // Get specific cookies
   document.cookie.split(';').forEach(cookie => {
       if (cookie.includes('PSID') || cookie.includes('csrf')) {
           console.log(cookie.trim());
       }
   });
   ```

## 🔧 Setting Up Environment Variables

### Windows (PowerShell)
```powershell
# Set session cookie
$env:GEMINI_SESSION_COOKIE="your_session_cookie_here"

# Set CSRF token
$env:GEMINI_CSRF_TOKEN="your_csrf_token_here"

# Verify they're set
echo $env:GEMINI_SESSION_COOKIE
echo $env:GEMINI_CSRF_TOKEN
```

### Windows (Command Prompt)
```cmd
set GEMINI_SESSION_COOKIE=your_session_cookie_here
set GEMINI_CSRF_TOKEN=your_csrf_token_here
```

### Linux/macOS
```bash
export GEMINI_SESSION_COOKIE="your_session_cookie_here"
export GEMINI_CSRF_TOKEN="your_csrf_token_here"
```

### Using .env File
Create a `.env` file in your zenOS directory:
```env
GEMINI_SESSION_COOKIE=your_session_cookie_here
GEMINI_CSRF_TOKEN=your_csrf_token_here
```

## 🧪 Testing Your Authentication

Once you've set the environment variables, test them:

```bash
# Test PKM module
python test_pkm_simple.py

# Test extraction (with limit to avoid too many requests)
zen pkm extract --limit 1

# Check if conversations were extracted
zen pkm list-conversations
```

## ⚠️ Important Security Notes

1. **Keep Credentials Secure**
   - Never commit cookies/tokens to version control
   - Use environment variables or secure config files
   - Consider using a password manager for storage

2. **Token Expiration**
   - Session cookies expire periodically
   - You may need to refresh them every few days/weeks
   - The PKM module will show clear error messages if authentication fails

3. **Rate Limiting**
   - Google may rate limit requests
   - Use reasonable limits when extracting conversations
   - The PKM module includes built-in delays and retry logic

## 🔍 Troubleshooting

### Common Issues

1. **"Authentication failed"**
   - Check that cookies are copied completely
   - Ensure no extra spaces or characters
   - Try refreshing your Gemini session and getting new cookies

2. **"No conversations found"**
   - Verify you have conversations in your Gemini account
   - Check that you're signed into the correct Google account
   - Try accessing Gemini in your browser first

3. **"Rate limited"**
   - Wait a few minutes before trying again
   - Reduce the limit parameter (`--limit 5`)
   - Check if you have many conversations (may take time)

### Debug Mode

Enable debug mode for more detailed output:
```bash
zen pkm extract --limit 1 --debug
```

## 📚 Additional Resources

- [Google Gemini Help](https://support.google.com/gemini)
- [Browser Developer Tools Guide](https://developer.chrome.com/docs/devtools/)
- [Cookie Management Best Practices](https://owasp.org/www-community/controls/SecureCookieAttribute)

## 🆘 Getting Help

If you're still having trouble:

1. Check the PKM module logs
2. Try the debug mode
3. Verify your Gemini account has conversations
4. Make sure you're using the latest version of the PKM module

The PKM module includes comprehensive error messages to help diagnose authentication issues.
