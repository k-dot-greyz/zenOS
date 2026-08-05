# zenOS Quick Start

**Python ≥ 3.14.** Full command reference: **[CLI.md](./CLI.md)**.

---

## Install

```bash
git clone https://github.com/k-dot-greyz/zenOS.git
cd zenOS
cp env.example .env   # OPENROUTER_API_KEY for live models
python3.14 -m pip install -e ".[dev]"
zen --help
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
