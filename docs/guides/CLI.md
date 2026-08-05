# zenOS CLI Reference

**Floor:** Python ≥ 3.14 · **Entry:** `zen` / `zenos` → `zen.cli:main`  
**Canonical source:** this doc. README and quickstarts defer here.

Status legend:

| Tag | Meaning |
|-----|---------|
| **live** | Registered on the `zen` Click group today |
| **source** | Implemented in tree but not yet `add_command`'d |
| **wiki** | Lands with visual-wiki integration (#48) |
| **roadmap** | Old marketing / aspirational — not a real subcommand |

Verify locally anytime:

```bash
python -c "from zen.cli import cli; print(sorted(cli.commands))"
```

---

## Install & smoke

```bash
git clone https://github.com/k-dot-greyz/zenOS.git
cd zenOS
python3.14 -m pip install -e ".[dev]"
zen --help
```

Prefer `pip install -e ".[dev]"`. Copy `env.example` → `.env` for OpenRouter when you want live models.

---

## Command map

### Root — **live**

| Command | What it does |
|---------|----------------|
| `zen` / `zen --version` | Root group / version |
| `zen run [agent] [prompt]` | Run an agent (`--list`, `--create`, `--chat`, `--offline`, `--model`, `--eco`, `--debug`, `--no-critique`, `--upgrade-only`, `--vars`) |
| `zen setup` | Unified env setup (`--unattended`, `--validate-only`, `--phase`) |

```bash
zen run --list
zen run --create my-agent
zen run --chat
zen run troubleshoot "git won't push" --debug
zen setup --validate-only
```

> Top-level `zen chat` is **roadmap**. Chat today: `zen run --chat`.

---

### Dex — catalog, bench, sync — **live**

Catalog code: `zen/dex/`. Data: `dex/*.yaml` (not `pokedex/`).

| Command | What it does |
|---------|----------------|
| `zen dex [models\|procedures]` | Browse catalog (`--task`, `--tier`) |
| `zen sync` | Refresh OpenRouter / remote stats (`--force`) — **top-level**, not `zen dex sync` |
| `zen bench <m1> <m2>` | Head-to-head bench (`-t` tournament extras) |
| `zen arena` | Rankings view |

```bash
zen dex models --task "code generation"
zen dex procedures --tier legendary
zen sync --force
zen bench anthropic/claude-sonnet openai/gpt-4o
zen arena
```

**Banned in new docs/scripts:** `zen pokedex …`.

---

### Plugins — **live**

| Command | What it does |
|---------|----------------|
| `zen plugins install <source>` | Git URL or `--local` path (`--version`, `--force`) |
| `zen plugins list` | Installed plugins |
| `zen plugins info <id>` | Manifest detail |
| `zen plugins remove <id>` | Uninstall |
| `zen plugins test <id>` | Smoke test |
| `zen plugins execute <id> <procedure>` | Run procedure (`--input` JSON) |
| `zen plugins search <query>` | Discover (`--category`, `--limit`) |
| `zen plugins trending` | Trending |
| `zen plugins stats` | Registry stats |

```bash
zen plugins install https://github.com/org/zen-plugin-foo
zen plugins list
zen plugins execute foo summarize --input '{"text":"hi"}'
```

---

### Inbox — **live** (`zen inbox`)

Registered as `inbox` (Click name). Implementation module still says `receive`.

| Command | What it does |
|---------|----------------|
| `zen inbox add <type> <content>` | Enqueue (`--metadata` JSON) |
| `zen inbox list` | List (`--status`) |
| `zen inbox process <id>` | Process item |

```bash
zen inbox add note "ship the dex PR" --metadata '{"tags":["sprint"]}'
zen inbox list --status new
```

---

### PKM — **live** (optional satellite)

| Command | What it does |
|---------|----------------|
| `zen pkm setup` | Dirs / config |
| `zen pkm extract` | Pull Gemini convos (`--limit`) |
| `zen pkm list-conversations` | List |
| `zen pkm search <query>` | Search |
| `zen pkm process` | Derive knowledge |
| `zen pkm export` | `--format json\|markdown` |
| `zen pkm stats` | Stats |
| `zen pkm config-show` | Show config |
| `zen pkm schedule list\|run\|start\|stop` | Jobs |

See `zen/pkm/README.md` for Gemini cookie env vars.

```bash
zen pkm setup
zen pkm extract --limit 10
zen pkm search "rust ffi"
```

---

### In source, not wired — **source**

Defined on `zen/cli_v2.py` but not `cli.add_command`'d yet:

| Command | Notes |
|---------|--------|
| `zen doctor` | Health / AI check — wire in Track 1 CLI collapse |
| `zen help` | Rich help panel — same |

Until wired, use `zen --help` and `zen setup --validate-only`.

---

### Wiki — **wiki** (#48)

External [visual-wiki](https://github.com/k-dot-greyz/visual-wiki) app. zenOS connects; does not vendor.

| Command | What it does |
|---------|----------------|
| `zen wiki setup` | Clone `~/.zenOS/visual-wiki` or use existing |
| `zen wiki status` / `path` | Resolve checkout |
| `zen wiki dev` / `build` | Next.js |
| `zen wiki export` / `prompt` | Agent-ready payloads |
| `zen wiki sync` | `~/.zenOS/context/visual-wiki*` |
| `zen wiki pull` / `pipe <url>` | `/api/pipe` against running `dev` |

Env: `ZEN_VISUAL_WIKI_PATH`, `ZEN_VISUAL_WIKI_URL`, `DEV_MASTER_ROOT` (`dex/09-repos/visual-wiki`).

---

## Global flags & env

| Flag / env | Effect |
|------------|--------|
| `--offline` / `ZEN_OFFLINE` / `ZEN_PREFER_OFFLINE` | Prefer local models |
| `--model` / `ZEN_MODEL` / `ZEN_DEFAULT_MODEL` | Pin model id |
| `--eco` / `ZEN_ECO_MODE` | Battery-lean paths |
| `--ai-mode` / `ZEN_AI_MODE` | Machine-friendly output (cli_v2) |
| `--debug` | Tracebacks on `run` |
| `--no-critique` | Skip PromptOS auto-critique |
| `COMPACT_MODE=1` / Termux | Mobile chat UI |

---

## Not commands (do not document as shipping)

| Fantasy | Reality |
|---------|---------|
| `zen pokedex …` | → `zen dex …` |
| `zen dex sync` | → `zen sync` |
| `zen notes …` | → `zen pkm` / `zen inbox` / wiki |
| `zen context sync` | → `zen wiki sync` (when #48 lands) |
| `zen swarm` / `zen delegate` | roadmap |
| `zen repo analyze\|health\|optimize` | roadmap |
| `zen chat` (top-level) | → `zen run --chat` |
| `zen procedures list` | → `zen dex procedures` |

---

## Architecture notes

1. **One entrypoint:** `zen.cli:main` → `cli()`. Fold remaining `cli_v2` helpers (`doctor`, `help`) into the same group — don’t add a second console script.
2. **Groups:** Click subgroups (`plugins`, `pkm`, `inbox`, later `wiki`).
3. **Rust-bound:** dex catalog parse is the first crate candidate; CLI stays Python glue.
4. **TDD story:** install → `zen --help` → `zen dex models` → offline `pytest` green.

See: [Rework sprint audit](../planning/REWORK_SPRINT_AUDIT.md) · [CI](../../.github/CI.md) · [Track](../../.github/TRACK.md)

---

## Cheat sheet

```bash
zen --help
zen setup --validate-only
zen run --list
zen dex models --task coding
zen sync
zen plugins list
zen pkm stats
zen inbox list
zen arena
```
