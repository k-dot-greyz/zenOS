# 🧘 zenOS Quick Start for Linux
## The "Just Make It Work" Guide

### What You Need
- Linux with Python 3.8+
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
Open terminal and run:
```bash
curl -sSL https://raw.githubusercontent.com/kasparsgreizis/zenOS/main/install.sh | bash
```

This will:
- Auto-detect Linux
- Download zenOS
- Install Python packages
- Download NLTK data
- Install the sample plugin
- Test everything
- Set up your environment

---

## Step 3: Add Your API Key (1 minute)
```bash
# Copy the example config
cp env.example .env

# Edit it with your favorite editor
nano .env
```

In the editor:
1. Find the line: `OPENROUTER_API_KEY=sk-or-v1-your-api-key-here`
2. Replace `sk-or-v1-your-api-key-here` with YOUR key from Step 1
3. Save and exit (Ctrl+X, then Y, then Enter)

---

## Step 4: Test zenOS! 🎉
```bash
# Set up environment
export PYTHONPATH="$PWD"

# Test the system
python3 zen/cli.py --help

# Install a sample plugin
python3 zen/cli.py plugins install ./examples/sample-plugin --local

# List your plugins
python3 zen/cli.py plugins list

# Test a plugin
python3 zen/cli.py plugins execute com.example.text-processor text.summarize "Hello from zenOS!"
```

---

## Step 5: Use AI Agents! 🤖
```bash
# Test the troubleshooter agent
python3 zen/cli.py run troubleshooter "My computer is running slow"

# Test the critic agent  
python3 zen/cli.py run critic "Write a function that adds two numbers"

# Test the assistant agent
python3 zen/cli.py run assistant "What is the meaning of life?"
```

---

## 🎮 Plugin Commands

```bash
# List all plugins
python3 zen/cli.py plugins list

# Install a plugin from GitHub
python3 zen/cli.py plugins install https://github.com/username/plugin-repo

# Install a plugin locally
python3 zen/cli.py plugins install ./path/to/plugin --local

# Execute a plugin procedure
python3 zen/cli.py plugins execute plugin-id procedure-id "input data"

# Test a plugin
python3 zen/cli.py plugins test plugin-id

# Show plugin stats
python3 zen/cli.py plugins stats
```

---

## 🤖 AI Agent Commands

```bash
# Use the troubleshooter agent
python3 zen/cli.py run troubleshooter "Your problem here"

# Use the critic agent
python3 zen/cli.py run critic "Your prompt here"

# Use the assistant agent
python3 zen/cli.py run assistant "Your question here"
```

---

## 💰 About Costs

- **Haiku** (fast): ~$0.001 per message
- **Sonnet** (default): ~$0.01 per message
- **Opus** (powerful): ~$0.05 per message

You get $5 free credit when you sign up to OpenRouter!

---

## 🔄 To Start Again Later
```bash
cd ~/zenOS
export PYTHONPATH="$PWD"
python3 zen/cli.py --help
```

---

## 🆘 If Something Goes Wrong

### "Module not found" errors
→ Make sure you set `export PYTHONPATH="$PWD"` in your terminal

### "API key error"
→ Check your .env file has the right key

### "No response from AI"
→ Check you have internet and your API key is valid

### "Plugin installation failed"
→ Make sure you have all dependencies installed: `pip3 install --user rich click aiohttp aiofiles psutil pyyaml textblob nltk`

---

## 🎯 That's It!

You now have a powerful AI plugin system with working agents! No Docker needed, just Python and your terminal. 🧘

**Pro tip**: Try installing plugins from GitHub repos - just add a `zenos-plugin.yaml` file and boom, instant zenOS integration!