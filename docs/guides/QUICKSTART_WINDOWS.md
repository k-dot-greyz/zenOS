# 🧘 zenOS Quick Start for Windows
## The "Just Make It Work" Guide

### What You Need
- Windows 10/11 with Python 3.8+
- An OpenRouter API key (we'll get this in Step 1)
- That's it!

---

## Step 1: Get Your AI Key (2 minutes)
1. Go to https://openrouter.ai/keys
2. Sign up (it's free to start)
3. Click "Create Key"
4. Copy the key that starts with `sk-or-v1-...`
5. Keep this tab open, you'll need it in a second

---

## Step 2: One-Command Install! ⚡ (1 minute)
Open PowerShell and run:
```powershell
iwr -useb https://raw.githubusercontent.com/k-dot-greyz/zenOS/main/install.ps1 | iex
```

This will:
- Auto-detect Windows
- Download zenOS
- Install Python packages
- Download NLTK data
- Install the sample plugin
- Test everything
- Set up your environment

---

## Step 3: Add Your API Key (1 minute)
```powershell
# Copy the example config
copy env.example .env

# Open it in notepad
notepad .env
```

In Notepad:
1. Find the line: `OPENROUTER_API_KEY=sk-or-v1-your-api-key-here`
2. Replace `sk-or-v1-your-api-key-here` with YOUR key from Step 1
3. Save and close (Ctrl+S, then close Notepad)

---

## Step 4: Test zenOS! 🎉
```powershell
# Set up environment
$env:PYTHONPATH = "$PWD"

# Test the system
python zen/cli.py --help

# Install a sample plugin
python zen/cli.py plugins install ./examples/sample-plugin --local

# List your plugins
python zen/cli.py plugins list

# Test a plugin
python zen/cli.py plugins execute com.example.text-processor text.summarize "Hello from zenOS!"
```

---

## Step 5: Use AI Agents! 🤖
```powershell
# Test the troubleshooter agent
python zen/cli.py run troubleshooter "My computer is running slow"

# Test the critic agent  
python zen/cli.py run critic "Write a function that adds two numbers"

# Test the assistant agent
python zen/cli.py run assistant "What is the meaning of life?"
```

---

## 🎮 Plugin Commands

```powershell
# List all plugins
python zen/cli.py plugins list

# Install a plugin from GitHub
python zen/cli.py plugins install https://github.com/username/plugin-repo

# Install a plugin locally
python zen/cli.py plugins install ./path/to/plugin --local

# Execute a plugin procedure
python zen/cli.py plugins execute plugin-id procedure-id "input data"

# Test a plugin
python zen/cli.py plugins test plugin-id

# Show plugin stats
python zen/cli.py plugins stats
```

---

## 🤖 AI Agent Commands

```powershell
# Use the troubleshooter agent
python zen/cli.py run troubleshooter "Your problem here"

# Use the critic agent
python zen/cli.py run critic "Your prompt here"

# Use the assistant agent
python zen/cli.py run assistant "Your question here"
```

---

## 💰 About Costs

- **Haiku** (fast): ~$0.001 per message
- **Sonnet** (default): ~$0.01 per message
- **Opus** (powerful): ~$0.05 per message

You get $5 free credit when you sign up to OpenRouter!

---

## 🔄 To Start Again Later
```powershell
cd ~/Desktop/zenOS
$env:PYTHONPATH = "$PWD"
python zen/cli.py --help
```

---

## 🆘 If Something Goes Wrong

### "Module not found" errors
→ Make sure you set `$env:PYTHONPATH = "$PWD"` in PowerShell

### "API key error"
→ Check your .env file has the right key

### "No response from AI"
→ Check you have internet and your API key is valid

### "Plugin installation failed"
→ Make sure you have all dependencies installed: `pip install rich click aiohttp aiofiles psutil pyyaml textblob nltk`

---

## 🎯 That's It!

You now have a powerful AI plugin system with working agents! No Docker needed, just Python and your terminal. 🧘

**Pro tip**: Try installing plugins from GitHub repos - just add a `zenos-plugin.yaml` file and boom, instant zenOS integration!
