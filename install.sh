#!/bin/bash
set -e

NINHO_HOME="${NINHO_HOME:-$HOME/.ninho}"
REPO_URL="https://github.com/ninho-ai/ninho"

echo "🪺 Installing Ninho..."
echo ""

# Detect platform
OS="$(uname -s)"
case "$OS" in
    Linux*)  PLATFORM=linux;;
    Darwin*) PLATFORM=macos;;
    MINGW*|MSYS*|CYGWIN*) PLATFORM=windows;;
    *)
        echo "❌ Unsupported OS: $OS"
        exit 1
        ;;
esac

echo "Detected platform: $PLATFORM"

# Check for required tools
if ! command -v git &> /dev/null; then
    echo "❌ git is required but not installed"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ python3 is required but not installed"
    exit 1
fi

# Clone or update
if [ -d "$NINHO_HOME" ]; then
    echo "Updating existing installation..."
    cd "$NINHO_HOME" && git pull --quiet
else
    echo "Cloning repository..."
    git clone --quiet "$REPO_URL" "$NINHO_HOME"
fi

# Create storage directories
mkdir -p "$NINHO_HOME/storage/daily"

# Make scripts executable
chmod +x "$NINHO_HOME"/adapters/claude-code/scripts/*.py 2>/dev/null || true

# Register with Claude Code
PLUGIN_PATH="$NINHO_HOME/adapters/claude-code"
SETTINGS="$HOME/.claude/settings.json"

# Ensure .claude directory exists
mkdir -p "$HOME/.claude"

# Try to register plugin
if command -v claude &> /dev/null; then
    claude plugin add "$PLUGIN_PATH" 2>/dev/null && echo "Registered with Claude Code" || true
fi

# Fallback: manual settings.json update
if [ -f "$SETTINGS" ]; then
    if command -v jq &> /dev/null; then
        jq --arg p "$PLUGIN_PATH" \
           'if .enabledPlugins then .enabledPlugins += [$p] | .enabledPlugins |= unique else .enabledPlugins = [$p] end' \
           "$SETTINGS" > "$SETTINGS.tmp" && mv "$SETTINGS.tmp" "$SETTINGS"
    else
        python3 -c "
import json
import os

settings_path = os.path.expanduser('$SETTINGS')
plugin_path = '$PLUGIN_PATH'

try:
    with open(settings_path, 'r') as f:
        settings = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    settings = {}

plugins = settings.setdefault('enabledPlugins', [])
if plugin_path not in plugins:
    plugins.append(plugin_path)

with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=2)
"
    fi
else
    # Create new settings file
    echo "{\"enabledPlugins\": [\"$PLUGIN_PATH\"]}" > "$SETTINGS"
fi

# Install CLI (optional, for standalone use)
if command -v pip3 &> /dev/null; then
    echo "Installing Ninho CLI..."
    pip3 install --quiet -e "$NINHO_HOME/packages/cli" 2>/dev/null || true
fi

echo ""
echo "✅ Ninho installed!"
echo ""
echo "   Location: $NINHO_HOME"
echo "   Plugin:   $PLUGIN_PATH"
echo ""
echo "What happens now:"
echo "   1. Restart Claude Code to activate the plugin"
echo "   2. Just code normally - Ninho works in the background"
echo "   3. Run '/ninho:status' to see captured context"
echo ""
echo "Ninho automatically captures:"
echo "   - PRDs from your discussions"
echo "   - Learnings from corrections"
echo "   - PR-to-PRD links when you create PRs"
echo ""
echo "Documentation: https://ninho.ai"
