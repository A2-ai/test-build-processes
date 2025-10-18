#!/bin/bash
set -e

echo "Removing test-build-processes..."

# Clean up any configuration or state files if they exist
# if [ -d /etc/test-build-processes ]; then
#     echo "Removing configuration directory at /etc/test-build-processes"
#     rm -rf /etc/test-build-processes
# fi

echo "Pre-removal cleanup complete!"
echo "The binary will be removed from /usr/local/bin/test-build-processes"
