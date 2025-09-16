#!/bin/bash

export ANTHROPIC_BASE_URL=https://gaccode.com/claudecode
export ANTHROPIC_API_KEY=sk-ant-oat01-c59fdae1647d93568b6643e619437101e7108c6d67adcc5ec6542a35bb6afcbe



# autocc.sh - Automatic switching between cctg and gac based on time
# Run with sudo privileges and loop every 10 minutes

STATE_FILE="/tmp/autocc_state"
CURRENT_STATE=""

# Function to get current state
get_current_state() {
    if [ -f "$STATE_FILE" ]; then
        CURRENT_STATE=$(cat "$STATE_FILE")
    else
        CURRENT_STATE="unknown"
    fi
}

# Function to set current state
set_current_state() {
    echo "$1" > "$STATE_FILE"
    CURRENT_STATE="$1"
}

# Function to switch to cctg with automated input
switch_to_cctg() {
    echo "Switching to cctg..."
    # Delete cctg config file before switching
    rm -f ~/.config/cctg/config.json
    expect << 'EOF'
spawn ./switchcctg.sh
expect {
    "email:" {
        send "19776000@qq.com\r"
        exp_continue
    }
    "password:" {
        send "wowowo\r"
        exp_continue
    }
    eof
}
EOF
    if [ $? -eq 0 ]; then
        set_current_state "cctg"
        echo "Successfully switched to cctg"
    else
        echo "Failed to switch to cctg"
    fi
}

# Function to switch to gac
switch_to_gac() {
    echo "Switching to gac..."
    ./switchgac.sh
    if [ $? -eq 0 ]; then
        set_current_state "gac"
        echo "Successfully switched to gac"
    else
        echo "Failed to switch to gac"
    fi
}

# Function to display current status
display_status() {
    current_time=$(date '+%H:%M:%S')
    current_hour=$(date '+%H')
    echo "========================================="
    echo "Time: $current_time"
    echo "Current State: $CURRENT_STATE"
    echo "Current Hour: $current_hour"
    
    if [ "$current_hour" -ge 9 ] && [ "$current_hour" -lt 23 ]; then
        echo "Target State: cctg (work hours: 9-23)"
    else
        echo "Target State: gac (off hours: 23-9)"
    fi
    echo "========================================="
}

# Check if expect is installed (needed for automated input)
if ! command -v expect &> /dev/null; then
    echo "Error: 'expect' is not installed. Please install it first:"
    echo "brew install expect"
    exit 1
fi

# Check if running as root/sudo
if [ "$EUID" -ne 0 ]; then
    echo "This script must be run with sudo privileges"
    echo "Usage: sudo ./autocc.sh"
    exit 1
fi

echo "Starting autocc.sh - Automatic switching service"
echo "Press Ctrl+C to stop"

# Main loop
while true; do
    # Get current state
    get_current_state
    
    # Get current hour
    current_hour=$(date '+%H')
    
    # Display status
    display_status
    
    # Determine action based on time
    if [ "$current_hour" -ge 9 ] && [ "$current_hour" -lt 23 ]; then
        # Work hours: 9-23, should be cctg
        if [ "$CURRENT_STATE" != "cctg" ]; then
            switch_to_cctg
        else
            echo "Already in cctg state"
        fi
    else
        # Off hours: 23-9, should be gac
        if [ "$CURRENT_STATE" != "gac" ]; then
            switch_to_gac
        else
            echo "Already in gac state"
        fi
    fi
    
    echo "Waiting 10 minutes before next check..."
    echo ""
    
    # Wait 10 minutes (600 seconds)
    sleep 600
done
