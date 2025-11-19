# Setup Guide

## API Keys Configuration

This project requires API keys for several services. **IMPORTANT**: Never commit `.mcp.json` with real API keys to git.

### Step 1: Copy Template

```bash
cp .mcp.json.template .mcp.json
```

### Step 2: Obtain API Keys

#### FDA API Key (Required for FDA drug data)
1. Visit: https://open.fda.gov/apis/authentication/
2. Sign up for a free API key
3. Add to `.mcp.json`: `FDA_API_KEY`

#### FRED API Key (Required for economic data)
1. Visit: https://fred.stlouisfed.org/docs/api/api_key.html
2. Create free FRED account
3. Generate API key
4. Add to `.mcp.json`: `FRED_API_KEY`

#### Data Commons API Key (Required for population/disease statistics)
1. Visit: https://docs.datacommons.org/api/
2. Request API key
3. Add to `.mcp.json`: `DC_API_KEY`

### Step 3: Update Server Paths

Edit `.mcp.json` and update all `/path/to/` references to point to your actual MCP server installations.

Example:
```json
"ct-gov-mcp": {
    "command": "node",
    "args": ["/Users/yourname/code/ct.gov-mcp-server/dist/index.js"],
    "env": {}
}
```

### Step 4: Verify Setup

```bash
# Test that .mcp.json is gitignored
git status  # Should NOT show .mcp.json

# Verify API keys work
python3 -c "from scripts.mcp.servers.fda_mcp import search; print('FDA OK')"
```

## Security Notes

- ✅ `.mcp.json` is gitignored (contains secrets)
- ✅ `.mcp.json.template` is version controlled (no secrets)
- ⚠️ Never commit real API keys to git
- ⚠️ If keys are exposed, revoke immediately

## MCP Server Installation

See individual MCP server repositories for installation instructions:
- ct-gov-mcp: https://github.com/[your-org]/ct.gov-mcp-server
- fda-mcp: https://github.com/[your-org]/fda-mcp-server
- [etc...]
