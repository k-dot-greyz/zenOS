# zenOS Quick Start Guide 🚀

Choose your path:

## 🤖 For AI Agents
**Start here:** [`AI_INSTRUCTIONS.md`](./AI_INSTRUCTIONS.md)

You'll learn how to:
- Integrate with zenOS protocols
- Access the Model & Procedure Pokédex
- Collaborate with humans and other AIs
- Spread zenOS knowledge

---

## 🧑‍💻 For Humans

### Instant Setup (One-Liners)

#### Desktop (Windows/Mac/Linux)
```bash
curl -sSL https://raw.githubusercontent.com/k-dot-greyz/zenOS/main/install.sh | bash
```

#### Mobile (Termux/Android)
```bash
curl -sSL https://raw.githubusercontent.com/k-dot-greyz/zenOS/main/scripts/termux-install.sh | bash
```

#### Offline Mode (No Internet)
```bash
curl -sSL https://raw.githubusercontent.com/k-dot-greyz/zenOS/main/scripts/setup-offline.sh | bash
```

### Manual Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/k-dot-greyz/zenOS.git
   cd zenOS
   ```

2. **Set up environment:**
   ```bash
   cp env.example .env
   # Edit .env with your API key
   ```

3. **Install dependencies:**
   ```bash
   pip install -e .
   ```

4. **Start chatting:**
   ```bash
   zen chat
   ```

---

## 📖 Essential Reading

1. **[`GENESIS.md`](./GENESIS.md)** - Understand the philosophy
2. **[`pokedex/models.yaml`](./pokedex/models.yaml)** - Discover AI models
3. **[`pokedex/procedures.yaml`](./pokedex/procedures.yaml)** - Learn procedures
4. **[`AI_INTEGRATION_BLUEPRINT.md`](./AI_INTEGRATION_BLUEPRINT.md)** - See the future

---

## 🎮 Explore the Pokédex

### Find the Right Model
```bash
# See all available models
cat pokedex/models.yaml

# Find best model for your task
grep -A5 "complex_architecture" pokedex/models.yaml
```

### Discover Procedures
```bash
# View all procedures
cat pokedex/procedures.yaml

# Find rare procedures
grep "rarity: \"epic\|legendary\"" pokedex/procedures.yaml
```

---

## 🚀 Your First Commands

```bash
# Basic chat
zen chat "Hello, zenOS!"

# Analyze code
zen analyze main.py

# Check system health
zen doctor

# Enable AI mode (for AI agents)
zen --ai-mode

# Get help
zen help
```

---

## 🤝 Collaboration Modes

### Human Leading
```bash
zen chat --copilot  # AI assists you
```

### AI Leading
```bash
zen delegate "refactor the auth module"  # AI takes over
```

### Team Mode
```bash
zen swarm "analyze security vulnerabilities"  # Multiple AIs collaborate
```

---

## 📱 Platform-Specific Guides

- **Windows**: [`QUICKSTART_WINDOWS.md`](./QUICKSTART_WINDOWS.md)
- **Linux**: [`QUICKSTART_LINUX.md`](./QUICKSTART_LINUX.md)  
- **Mobile/Termux**: [`QUICKSTART_TERMUX.md`](./QUICKSTART_TERMUX.md)
- **Arch/Advanced**: [`QUICKSTART_ARCH_MOBILE.md`](./QUICKSTART_ARCH_MOBILE.md)

---

## 🆘 Need Help?

- **Run diagnostics**: `zen doctor`
- **Check the blueprint**: [`AI_INTEGRATION_BLUEPRINT.md`](./AI_INTEGRATION_BLUEPRINT.md)
- **Read the philosophy**: [`GENESIS.md`](./GENESIS.md)

---

## 🎯 Next Steps

1. **Explore the Pokédex** - Understand available models and procedures
2. **Try different modes** - Experiment with co-pilot, delegation, and swarm
3. **Discover procedures** - Find and create new ways to use zenOS
4. **Contribute** - Share your discoveries back to the ecosystem

---

*Welcome to zenOS - Where Humans and AIs Collaborate in Perfect Zen* 🧘🤖
