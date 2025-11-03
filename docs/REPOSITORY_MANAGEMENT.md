# zenOS Repository Management Procedures

Comprehensive guide to zenOS repository management capabilities, procedures, and tools.

## Overview

zenOS provides a complete suite of repository management tools designed to handle local repository discovery, GitHub integration, health auditing, and maintenance operations. These tools work together to provide a unified repository management experience.

## Core Tools

### 1. Local Repository Scanner (`find_all_local_repos.py`)

**Purpose**: Discover all git repositories on the local filesystem.

**Capabilities**:
- Recursive scanning with configurable depth
- Exclusion pattern support
- JSON output for automation
- Detailed repository information

**Usage**:
```bash
# Basic scan of default locations
python find_all_local_repos.py

# Scan specific paths with custom depth
python find_all_local_repos.py -p C:/dev -p D:/projects --max-depth 5

# Save results to JSON
python find_all_local_repos.py --json repos.json --details
```

### 2. Enhanced GitHub Cloner (`clone_all_repos.py`)

**Purpose**: Clone or update repositories from GitHub with advanced features.

**Capabilities**:
- Multiple GitHub account support
- Configurable destination directories
- Dry-run mode for safety
- Private repository support
- Fork filtering options

**Usage**:
```bash
# Clone repos for default user
python clone_all_repos.py

# Clone from specific user to custom directory
python clone_all_repos.py -u octocat -d ./github-repos

# Multiple users with preview
python clone_all_repos.py -u user1 -u user2 --dry-run

# Include private repos, save results
python clone_all_repos.py --include-private --json results.json
```

### 3. Unified Repository Manager (`zen_repo_manager.py`)

**Purpose**: Comprehensive repository management with multiple subcommands.

**Commands**:
- `scan`: Discover local repositories
- `sync`: Sync with remote sources
- `status`: Check repository status
- `audit`: Perform health audits

**Usage**:
```bash
# Scan for repositories
python zen_repo_manager.py scan --details

# Audit repository health
python zen_repo_manager.py audit --output audit.md

# Check status of repositories
python zen_repo_manager.py status -p ./projects

# Sync repositories
python zen_repo_manager.py sync -u myusername --dry-run
```

### 4. Repository MCP Server (`repositories-mcp`)

**Purpose**: MCP-compatible server providing repository management tools for AI assistants.

**Available Tools**:
- `scan_local_repositories`: Scan filesystem for git repos
- `get_repository_status`: Get detailed repo status
- `fetch_github_repositories`: Query GitHub API
- `clone_repository`: Clone git repositories
- `update_repository`: Pull latest changes
- `audit_repositories`: Comprehensive health audit

## zenOS Procedures

### Individual Procedures

#### `zen.repo.scan` - Repository Discovery
**Type**: Analytical, Common
**Complexity**: 30, **Efficiency**: 95%, **Accuracy**: 98%

**Description**: Scan local filesystem for all git repositories.

**Requirements**:
- Filesystem access
- Git repository detection

**Tools**: `find_all_local_repos.py`, `zen_repo_manager.py scan`

#### `zen.repo.audit` - Repository Audit
**Type**: Analytical, Uncommon
**Complexity**: 45, **Efficiency**: 88%, **Accuracy**: 94%

**Description**: Comprehensive audit of repository health and status.

**Requirements**:
- Repository scanning
- Status analysis
- Health scoring

**Tools**: `zen_repo_manager.py audit`, `repositories-mcp audit_repositories`

#### `zen.repo.sync` - Repository Sync
**Type**: Operational, Uncommon
**Complexity**: 55, **Efficiency**: 85%, **Reliability**: 90%

**Description**: Synchronize repositories with remote sources.

**Requirements**:
- Git operations
- Remote access
- Conflict resolution

**Tools**: `clone_all_repos.py`, `zen_repo_manager.py sync`, `repositories-mcp clone_repository`

#### `zen.repo.status` - Repository Status
**Type**: Monitoring, Common
**Complexity**: 25, **Efficiency**: 98%, **Accuracy**: 100%

**Description**: Get current status of repositories.

**Requirements**:
- Git status
- Branch information
- Remote status

**Tools**: `zen_repo_manager.py status`, `repositories-mcp get_repository_status`

### Procedure Combinations

#### Repository Health Check (1.6x multiplier)
**Procedures**: `zen.repo.scan` → `zen.repo.audit` → `zen.repo.status`
**Description**: Complete repository discovery, audit, and status assessment.

**Usage Flow**:
1. Discover all repositories
2. Audit health and identify issues
3. Get current status for verification

#### Repository Maintenance (1.7x multiplier)
**Procedures**: `zen.repo.audit` → `zen.repo.sync` → `zen.repo.status`
**Description**: Audit repositories, sync with remotes, and verify status.

**Usage Flow**:
1. Audit current repository state
2. Sync with remote sources
3. Verify final status

## Configuration

### Environment Variables

```bash
# GitHub integration
export GITHUB_TOKEN="your_personal_access_token"
export GITHUB_USERNAME="your_github_username"

# Default paths
export REPO_DEST_DIR="/path/to/repositories"

# MCP server paths
export PYTHONPATH="$PYTHONPATH:/path/to/zenOS"
```

### MCP Configuration

Add to your MCP configuration (`mcp-config/configs/mcp.json`):

```json
{
  "repositories": {
    "command": "python",
    "args": ["-m", "repositories_mcp.server"],
    "env": {
      "GITHUB_TOKEN": "${GITHUB_TOKEN}",
      "GITHUB_USERNAME": "${GITHUB_USERNAME}",
      "REPO_DEST_DIR": "${REPO_DEST_DIR}"
    }
  }
}
```

## Common Workflows

### 1. Initial Repository Discovery
```bash
# Scan and audit all repositories
python zen_repo_manager.py scan --details --json scan.json
python zen_repo_manager.py audit --output audit.md
```

### 2. Repository Backup/Migration
```bash
# Clone all repositories to backup location
python clone_all_repos.py -u myusername -d /backup/repos --yes
```

### 3. Health Monitoring
```bash
# Regular health check
python zen_repo_manager.py audit
python zen_repo_manager.py status
```

### 4. Multi-Account Management
```bash
# Sync repositories from multiple accounts
python clone_all_repos.py -u personal -u work -u oss --yes
```

## Troubleshooting

### Common Issues

#### Permission Denied
- Ensure proper filesystem permissions
- Run with appropriate user privileges
- Check exclusion patterns for system directories

#### GitHub API Rate Limiting
- Set `GITHUB_TOKEN` environment variable
- Reduce API call frequency
- Use `--dry-run` to preview operations

#### Repository Path Issues
- Use absolute paths for reliability
- Check destination directory permissions
- Verify git installation and PATH

#### MCP Server Connection
- Install required dependencies: `pip install mcp requests`
- Set `PYTHONPATH` to include zenOS directory
- Check MCP server logs for errors

### Health Check Indicators

#### Repository Health Scores
- **90-100**: Excellent health
- **80-89**: Good health, minor issues
- **50-79**: Needs attention
- **<50**: Critical issues requiring immediate action

#### Common Health Issues
- Uncommitted changes
- Outdated branches (behind remote)
- Missing remote configuration
- Repository corruption

## Integration Examples

### With AI Assistants
```text
"Scan my local repositories and audit their health"
"Clone all repositories from user 'octocat'"
"Check the status of repositories in ~/projects"
"Audit repository health and save report"
```

### With Automation Scripts
```bash
#!/bin/bash
# Weekly repository maintenance
python zen_repo_manager.py audit --output weekly-audit.md
python zen_repo_manager.py sync --yes
python zen_repo_manager.py status > weekly-status.txt
```

### With MCP Clients
The repository MCP server integrates with:
- Claude Desktop
- Cursor IDE
- Other MCP-compatible applications

## Future Enhancements

### Planned Features
- Repository dependency analysis
- Automated conflict resolution
- Repository migration tools
- Advanced health monitoring
- Integration with CI/CD pipelines

### Extension Points
- Custom audit rules
- Repository templates
- Automated maintenance schedules
- Integration with project management tools

---

*This documentation reflects zenOS repository management capabilities as of 2025-01-08. Procedures and tools continue to evolve through usage and community contributions.*
