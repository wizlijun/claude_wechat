#!/bin/bash

# Copy claude1 to claude and test version
echo "Copying /opt/homebrew/bin/claude1 to /opt/homebrew/bin/claude..."

# Remove existing claude if it exists
if [ -f "/opt/homebrew/bin/claude" ] || [ -L "/opt/homebrew/bin/claude" ]; then
    sudo rm /opt/homebrew/bin/claude
    echo "Removed existing claude"
fi

# Copy claude1 to claude
sudo ln -s "$(readlink /opt/homebrew/bin/claude1)" /opt/homebrew/bin/claude
echo "Copied /opt/homebrew/bin/claude1 to /opt/homebrew/bin/claude"

# Test the version
echo "Testing claude version..."
claude -p "who are you,what is your version"
