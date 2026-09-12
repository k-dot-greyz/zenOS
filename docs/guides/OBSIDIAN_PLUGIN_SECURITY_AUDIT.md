# Security Audit Protocol: Obsidian Community Plugin Policies, Automated Scanning, and Manual Review

This document defines the audit protocol for evaluating Obsidian community plugins in security-sensitive contexts (e.g., local PKM vaults containing personal or confidential data). It synthesizes Obsidian's official security model, automated review system, and developer policies into an actionable checklist and threat model.

## 1. Scope and threat model

- **Threat actor:** malicious or compromised plugin authors, supply-chain attacks via dependencies, or attackers abusing shared vaults to propagate plugin state.
- **Trust boundary:** Obsidian desktop app (Electron/Node.js) with full user-level filesystem and network access; plugins inherit Obsidian's capabilities.
- **Assets at risk:** all files readable/writable by Obsidian (vault + other user files), credentials/tokens stored in vault, clipboard, and any data sent over the network.
- **Blast radius:** a single malicious plugin can exfiltrate arbitrary files, modify notes/configs, install additional programs, and establish persistence via startup scripts or scheduled tasks.

## 2. Official policy and review references (SSOT)

Anchor all audit work to these sources:

- **Plugin security (official help):** Restricted Mode, plugin capabilities, review process, reporting. https://github.com/obsidianmd/obsidian-help/blob/master/en/Extending%20Obsidian/Plugin%20security.md
- **The future of Obsidian plugins (May 2026):** automated reviews for every version, malware scanning, safety scorecards, upcoming disclosures and verified authors. https://obsidian.md/blog/future-of-plugins/
- **Developer self-critique checklist (Security section):** disclosures, dependencies, telemetry, lockfiles. https://docs.obsidian.md/oo/plugin
- **Less is safer (supply-chain philosophy):** minimal dependencies, version pinning, no postinstall, slow upgrades. https://obsidian.md/blog/less-is-safer/
- **Community plugin directory:** plugin pages with safety scorecards and flags. https://community.obsidian.md/plugins

## 3. Automated scanning rules (what Obsidian's reviewer checks)

Obsidian's automated review system scans **every plugin version** for security and code-quality issues; results appear as a **safety scorecard** on each plugin page.

Key automated checks (inferred from official docs and ecosystem tooling):

- **Malware & known vulnerabilities:** static analysis for malicious patterns and known CVEs in dependencies.
- **Policy adherence:** compliance with Developer Policies (e.g., no closed-source new submissions, proper manifest, README disclosures).
- **Code quality & ESLint rules:** enforcement of Obsidian's plugin guidelines via `eslint-plugin-obsidianmd` (36 rules as of 2026).
- **Dependency hygiene:** presence of lockfiles (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`), minimal and pinned dependencies.
- **Telemetry & ads:** detection of client-side telemetry, analytics, or ad networks that collect sensitive usage data.
- **Disclosures:** README must declare payments, account requirements, network use, external file access, ads, telemetry, and closed-source components.

Plugins that fail automated review are removed from search within 24 hours for new versions; older plugins are grandfathered temporarily but will be phased out.

## 4. Manual review criteria (human audit checklist)

Use this checklist for high-sensitivity vaults or when a plugin's scorecard/behavior raises concerns.

### 4.1 Pre-install triage (directory & scorecard)

- [ ] Verify the plugin appears in the **Community directory** with a visible **safety scorecard**.
- [ ] Check **download count, update recency, author reputation**, and labels (Official, Paid, Optional payments).
- [ ] Review **automated review status** and any warnings/flags on the scorecard.
- [ ] Read the **README** for required disclosures: network use, external file access, payments, telemetry, closed-source code.

### 4.2 Source code review (independent security audit)

Obsidian explicitly recommends an independent security audit before using community plugins with sensitive data.

Focus areas:

- **Network calls:** search for `fetch`, `XMLHttpRequest`, `WebSocket`, `axios`, `requestUrl`; identify destinations, triggers, and data sent.
- **Filesystem access:** look for Node/Electron `fs`, `path`, `Vault.adapter`, `FileSystemAdapter`, recursive reads/writes, access outside the vault.
- **Shell/execution:** any `child_process`, `exec`, `spawn`, `osascript`, or bridges to shell commands.
- **Secrets handling:** hardcoded tokens, `.env` reads, credential storage in `data.json`, logging of sensitive fields.
- **Obfuscation / dynamic code:** heavily minified bundles, dynamic imports from remote URLs, post-install fetch of additional payloads.
- **Dependencies:** audit `package.json` and lockfile for unnecessary or risky dependencies; prefer minimal, pinned deps.

If code functionality is unclear or heavily obfuscated, treat the plugin as high-risk.

### 4.3 Runtime behavior validation (dynamic analysis)

In a controlled environment (disposable VM or container):

- [ ] Install the plugin in a **clean vault** with canary tokens (unique strings, fake API keys).
- [ ] Monitor **network traffic** (Wireshark, mitmproxy) for unexpected outbound connections.
- [ ] Watch **process tree** for Obsidian spawning shells/script interpreters (powershell, cmd, bash, zsh, osascript).
- [ ] Inspect **file activity** under `.obsidian/plugins/<plugin-id>` and beyond the vault directory.

### 4.4 Data-leak & exfiltration threat modeling

Model worst-case blast radius:

- **Confidentiality:** can the plugin read all vault notes, attachments, and other user files, then exfiltrate via HTTPS/DNS/clipboard?
- **Integrity:** can it modify notes, inject malicious links, or alter config files to persist across sessions?
- **Execution:** can it install additional programs, schedule tasks, or drop LaunchAgents/startup scripts?
- **Supply chain:** does the plugin depend on remote CDNs, analytics, or telemetry that could be compromised later?

For high-sensitivity vaults, assume any network-capable plugin can exfiltrate everything Obsidian can access unless verified otherwise.

## 5. Identifying malicious plugins: red flags

Treat these signals as strong indicators of risk:

- **Failed or missing scorecard** in the Community directory.
- **No README disclosures** about network, filesystem, payments, or telemetry.
- **Heavy obfuscation** or dynamically fetched remote code.
- **Unnecessary dependencies** (analytics, telemetry, ad networks) in a simple plugin.
- **Hardcoded tokens or secrets** in source or `data.json` examples.
- **Shell/execution bridges** without clear, justified use cases.
- **Reports or flags** from the community (Discord, forums, Reddit) about suspicious behavior.

If you suspect a plugin is malicious: flag it on the plugin page, report to Obsidian support, and/or DM moderators.

## 6. Baseline hardening for sensitive PKM vaults

- [ ] Keep **Restricted Mode ON** by default; only disable for trusted plugins.
- [ ] **Disable community plugin sync** unless explicitly required; prevents shared vaults from propagating plugin state.
- [ ] Treat **shared vaults/workspaces from unknown parties as untrusted content + configuration**.
- [ ] Prefer **popular, well-maintained plugins** with strong community trust and clean scorecards.
- [ ] For extremely sensitive vaults, run Obsidian in a **sandboxed/contained environment** (dedicated user account, container, or VM).

## 7. Ongoing monitoring & update policy

- [ ] **Delay updates** by 1–2 weeks to let the community surface issues.
- [ ] Re-check **scorecards** after each new version; failed reviews should trigger removal from search within 24 hours.
- [ ] Subscribe to **security discussions** in Obsidian forums/Discord and watch for plugin-specific flags.
- [ ] Periodically **audit installed plugins** and remove unused ones; review `.obsidian/plugins/` configs as executable trust surfaces.

## 8. Reference manifest (for automation & PRs)

```yaml
title: "Obsidian Plugin Security & Blast Radius Audit"
sources:
  - name: "Plugin security (official help)"
    url: "https://github.com/obsidianmd/obsidian-help/blob/master/en/Extending%20Obsidian/Plugin%20security.md"
    role: "SSOT for plugin capabilities, Restricted Mode, and review process"
  - name: "The future of Obsidian plugins (May 2026)"
    url: "https://obsidian.md/blog/future-of-plugins/"
    role: "Automated reviews, scorecards, disclosures, verified authors"
  - name: "Obsidian October plugin self-critique checklist"
    url: "https://docs.obsidian.md/oo/plugin"
    role: "Security disclosures, dependencies, telemetry, lockfiles"
  - name: "Less is safer (supply-chain philosophy)"
    url: "https://obsidian.md/blog/less-is-safer/"
    role: "Minimal dependencies, version pinning, no postinstall"
  - name: "Community plugin directory"
    url: "https://community.obsidian.md/plugins"
    role: "Safety scorecards, plugin metadata, flags"
```

## 9. Appendix: detection rules (Elastic-style KQL examples)

For SOC/IR contexts monitoring Obsidian abuse (e.g., PHANTOMPULSE-style campaigns):

```kql
// Obsidian spawning shells/script interpreters
process.name : ("Obsidian.exe" OR "Obsidian") 
and process.parent.name : ("powershell.exe" OR "cmd.exe" OR "bash" OR "zsh" OR "osascript")

// File activity under plugin directories
file.directory : ("*.obsidian/plugins/*") 
and process.name : ("Obsidian.exe" OR "Obsidian")
```

Adjust paths and process names per platform (Windows/macOS/Linux).

## 10. zenOS integration notes

- Place this guide under `docs/guides/` alongside other security and setup documentation.
- Reference from `docs/REPOSITORY_MANAGEMENT.md` and any security-related blueprints.
- Consider adding a CI check that links to this guide when `.obsidian/` config changes are detected in PRs.
- For zenOS agents that interact with Obsidian vaults, treat this as required reading before enabling any plugin-based integrations.
