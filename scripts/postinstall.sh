#!/bin/bash
set -e

echo "Installing test-build-processes..."

# Make the binary executable (should already be, but ensure it)
chmod +x /usr/local/bin/test-build-processes

# Create a simple symlink or additional capability demonstration
# This is a simple example to show we can run post-installation scripts
echo "Post-installation: Binary installed to /usr/local/bin/test-build-processes"
echo "You can now run 'test-build-processes' from anywhere in your system"

# Optional: Add any additional setup here (e.g., creating config directories)
# mkdir -p /etc/test-build-processes
# echo "Created configuration directory at /etc/test-build-processes"

echo "Installation complete!"
