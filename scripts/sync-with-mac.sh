#!/bin/bash
# Sync shared content between Windows and Mac versions
# Run this when you make major updates to core AI framework information

set -e

MAC_REPO_PATH="/home/johnsirmon/projects/ai-dev-workstation-mac"

echo "Syncing shared content between Windows and Mac versions..."

# Check if Mac repo exists
if [ ! -d "$MAC_REPO_PATH" ]; then
    echo "Mac repository not found at $MAC_REPO_PATH"
    exit 1
fi

# Sync core AI framework information (manual review needed)
echo "Updating AI framework versions in Mac version..."

# Copy shared configuration parts (you'll need to adapt these)
# Note: This is a starting point - you may want to be more selective

echo "Manual sync points to consider:"
echo "1. AI framework versions in README.md section 3"
echo "2. Community monitoring sources in config/tools-tracking.json"
echo "3. MCP server base configurations"
echo "4. General AI agent development concepts"
echo ""
echo "Remember: Keep platform-specific sections separate!"
echo "- Installation methods (WSL vs Homebrew)"
echo "- File paths and directory structures"
echo "- Performance tips"
echo "- Troubleshooting guides"

# Create a diff to show what needs manual review
echo "Creating diff for manual review..."
diff -u README.md "$MAC_REPO_PATH/README.md" > sync-diff.txt 2>/dev/null || true

if [ -s sync-diff.txt ]; then
    echo "Differences found - review sync-diff.txt for manual updates"
else
    echo "No significant differences found"
fi

echo "Sync check completed!"