# zenOS Quick Start

**Python ≥ 3.14.** Full command reference: **[CLI.md](./CLI.md)**.

---

## Install

### Requirements

- **Python 3.14+** (hard fail below this — `zen`, `install.sh`, and Cloud Agent `start` refuse to boot)
- Current stable deps from `pyproject.toml` / `requirements.txt`
- Preferred bootstrap: `bash scripts/zenos-env-install.sh` then `bash scripts/zenos-env-start.sh`
- Verify: `zen env-doctor`
- Optional: [uv](https://docs.astral.sh/uv/) (`uv python install 3.14`)

### Quick path

```bash
git clone https://github.com/k-dot-greyz/zenOS.git
cd zenOS
cp env.example .env   # OPENROUTER_API_KEY for live models
python3.14 -m pip install -e ".[dev]"
zen --help
```

### One-liners (curl installers)

#### Desktop (Windows/Mac/Linux)

```bash
curl -sSL https://raw.githubusercontent.com/k-dot-greyz/zenOS/main/install.sh | bash
```

#### Mobile (Termux/Android)

```bash
curl -sSL https://raw.githubusercontent.com/k-dot-greyz/zenOS/main/scripts/termux-install.sh | bash
```

#### Offline mode

```bash
curl -sSL https://raw.githubusercontent.com/k-dot-greyz/zenOS/main/scripts/setup-offline.sh | bash
```

### Manual setup

1. Clone, copy `env.example` → `.env`, install with Python 3.14:

   ```bash
   git clone https://github.com/k-dot-greyz/zenOS.git
   cd zenOS
   cp env.example .env
   python3.14 -m pip install -e ".[dev]"
   ```

2. Smoke:

   ```bash
   zen --help
   zen env-doctor
   ```

---

## First five minutes

```bash
zen --help
zen run --list
zen run --chat

zen setup --validate-only

zen dex models
zen dex procedures --tier epic
zen sync
```

---

## Where things live

| You want… | Use |
|-----------|-----|
| Models / procedures | `zen dex …` + `dex/*.yaml` |
| Refresh remote stats | `zen sync` |
| Plugins | `zen plugins …` |
| Gemini PKM | `zen pkm …` |
| Inbox pipe | `zen inbox …` |
| Environment health | `zen env-doctor` |
| Visual garden → agents | `zen wiki sync` (when #48 lands) |
| Philosophy | [`GENESIS.md`](../GENESIS.md) |
| Debt map | [`REWORK_SPRINT_AUDIT.md`](../planning/REWORK_SPRINT_AUDIT.md) |

---

## Platform guides

- [Windows](./QUICKSTART_WINDOWS.md)
- [Linux](./QUICKSTART_LINUX.md)
- [Termux / mobile](./QUICKSTART_TERMUX.md)
- [Arch mobile](./QUICKSTART_ARCH_MOBILE.md)
- [Dev environment](./DEV_ENVIRONMENT_SETUP.md)

---

## AI agents

[`AI_INSTRUCTIONS.md`](../AI_INSTRUCTIONS.md) · prefer **dex** vocabulary · don’t invent verbs missing from [CLI.md](./CLI.md).

---

*zenOS — humans and AIs, same terminal, less bullshit.*
