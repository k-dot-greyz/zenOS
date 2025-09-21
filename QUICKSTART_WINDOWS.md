# 🧘 zenOS Quick Start for Windows
## The "Just Make It Work" Guide

### What You Need
- Windows with Docker Desktop installed
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

## Step 2: Download zenOS (1 minute)
Open PowerShell and run:
```powershell
# Go to your desktop (or wherever you want)
cd ~/Desktop

# Download zenOS
git clone https://github.com/kasparsgreizis/zenOS.git

# Enter the folder
cd zenOS
```

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

## Step 4: Start zenOS (2 minutes)
Back in PowerShell:
```powershell
# Start everything
.\start.ps1
```

Wait for it to say `✨ zenOS is ready!`

---

## Step 5: CHAT! 🎉
```powershell
# Enter the chat
docker-compose exec zen-cli bash
```

You're now in chat mode! Just start typing:
- "What is zenOS?"
- "Explain quantum computing like I'm 5"
- "Write me a haiku about coding"

---

## 🎮 Quick Commands Inside Chat

- `/help` - See all commands
- `/model haiku` - Use fast/cheap model
- `/model opus` - Use powerful model  
- `/cost` - Check how much you've spent
- `/exit` - Leave chat
- `Ctrl+D` - Quick exit

---

## 💰 About Costs

- **Haiku** (fast): ~$0.001 per message
- **Sonnet** (default): ~$0.01 per message
- **Opus** (powerful): ~$0.05 per message

You get $5 free credit when you sign up to OpenRouter!

---

## 🛑 To Stop zenOS
Exit the chat first (Ctrl+D), then:
```powershell
docker-compose down
```

---

## 🔄 To Start Again Later
```powershell
cd ~/Desktop/zenOS
docker-compose up -d
docker-compose exec zen-cli bash
```

---

## 🆘 If Something Goes Wrong

### "Docker not running"
→ Open Docker Desktop app first

### "Can't find docker-compose"
→ Docker Desktop should have installed it. Try restarting PowerShell.

### "API key error"
→ Check your .env file has the right key

### "No response from AI"
→ Check you have internet and your API key is valid

---

## 🎯 That's It!

You now have a powerful AI assistant in your terminal. No cloud subscriptions, no web browser needed. Just you, your terminal, and zen. 🧘

**Pro tip**: Once you're comfortable, try `/model opus` for complex tasks - it's like switching from a Honda to a Ferrari!
