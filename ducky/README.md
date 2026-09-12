# 🦆 ducky — portable zenOS env setup payload

**ducky** is a tap-to-run env setup and hydration bundle for zenOS. Copy it to a USB drive or Android shared storage, run once, and get local diagnostics plus a scaffolded dev workspace.

## What it does

1. **env-doctor** — collects local deets (OS, shell, Python, git, Termux, `.env` presence, validation issues) into `.zen-hydration/local-deets.json`
2. **hydrate** — materializes scaffold files from `dev-master` if available, else `ducky/hydrate/*` templates
3. **programmatic setup** — falls back to `python setup.py --unattended` (or `--validate-only` for `minimal` profile)

## Quick start

### Desktop / USB (Linux/macOS)

```bash
git clone https://github.com/k-dot-greyz/zenOS.git
cd zenOS
bash ducky/run.sh
```

From a USB mount:

```bash
bash /media/$USER/USB/zenOS/ducky/run.sh
```

### Windows

```powershell
cd zenOS
.\ducky\run.ps1
```

### Android (Termux)

```bash
# Copy zenOS to shared storage or clone on device
termux-setup-storage
cd ~/zenOS
DUCKY_PROFILE=mobile bash ducky/run.sh
```

**Widget shortcut:** point Termux:Widget at `ducky/tap-termux.sh` or `ducky/hydrate/mobile/termux-widget-ducky.sh`.

## Profiles

| Profile | Hydration | Setup |
|---------|-----------|-------|
| `minimal` | default templates | `setup.py --validate-only` |
| `developer` (default) | default templates | `setup.py --unattended` |
| `mobile` | mobile templates + aliases | `setup.py --unattended` |
| `offline` | default templates | `scripts/setup-offline.sh` |

```bash
DUCKY_PROFILE=mobile bash ducky/run.sh
```

## dev-master hydration

If a sibling `dev-master` repo exists with a `hydration/` directory, ducky prefers it over in-repo templates:

```bash
export ZEN_DEV_MASTER=/path/to/dev-master
bash ducky/run.sh
```

Checked paths (in order):

- `$ZEN_DEV_MASTER/hydration`
- `../dev-master/hydration`
- `../../dev-master/hydration`

## Outputs

| File | Purpose |
|------|---------|
| `.zen-hydration/local-deets.json` | Machine-readable local environment report |
| `.zen-hydration/ducky-report.json` | Same report (doctor artifact) |
| `.zen-hydration/manifest.json` | Hydration profile, source, timestamp |

## env-doctor only

```bash
python ducky/env_doctor.py
python ducky/env_doctor.py --json-only
```

## Related

- Linear: [ZEN-286](https://linear.app/zenos/issue/ZEN-286)
- `docs/issues/ZEN-286.md` — full issue hydration
- `docs/guides/QUICKSTART_TERMUX.md` — Termux install guide
- `setup.py` — programmatic fallback setup
