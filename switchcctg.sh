#!/bin/bash

# Switch claude symlink to cctg and test version
echo "Switching /opt/homebrew/bin/claude symlink to /opt/homebrew/bin/cctg..."

# Remove existing symlink if it exists
if [ -L "/opt/homebrew/bin/claude" ]; then
    sudo rm /opt/homebrew/bin/claude
    echo "Removed existing symlink"
fi

# Create new symlink to cctg
sudo ln -s /opt/homebrew/bin/cctg /opt/homebrew/bin/claude
echo "Created symlink: /opt/homebrew/bin/claude -> /opt/homebrew/bin/cctg"

# Test the version
echo "Testing claude version..."
claude -p "what is your version"
