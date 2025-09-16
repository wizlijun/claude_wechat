#!/bin/bash

# Test script to simulate the input prompts that switchcctg.sh might have
echo "Starting test for automated input..."
echo ""

echo -n "Please enter your email: "
read email
echo "Email entered: $email"

echo -n "Please enter your password: "
read -s password
echo ""
echo "Password entered: [hidden]"

echo ""
echo "Test completed successfully!"
echo "Email: $email"
echo "Password length: ${#password} characters"