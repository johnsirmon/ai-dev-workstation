#!/bin/bash
# Weekly automated update script for AI Agent Development Workstation
# This script orchestrates the complete update process

set -e

echo "AI Agent Development Workstation - Weekly Update"
echo "Started: $(date)"

# Create necessary directories
mkdir -p reports logs

# Set up logging
LOG_FILE="logs/update-$(date +%Y-%m-%d).log"
exec 1> >(tee -a "$LOG_FILE")
exec 2> >(tee -a "$LOG_FILE" >&2)

# Function to check if Python packages are installed
check_python_deps() {
    echo "Checking Python dependencies..."
    
    # Check if virtual environment exists and activate it
    if [ -d ".venv" ]; then
        echo "Activating virtual environment..."
        source .venv/bin/activate
    else
        echo "Virtual environment not found. Creating one..."
        python3 -m venv .venv
        source .venv/bin/activate
    fi
    
    # Install dependencies if needed
    if ! python3 -c "import requests, packaging, bs4" 2>/dev/null; then
        echo "Installing required Python packages..."
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt
        else
            pip install requests packaging beautifulsoup4
        fi
    fi
    
    echo "Python dependencies ready"
}

# Function to run tool version checks
run_tool_checks() {
    echo ""
    echo "Running tool version checks..."
    echo "================================="
    
    if [ -f "scripts/update-tools.py" ]; then
        python3 scripts/update-tools.py
        echo "Tool version check completed"
    else
        echo "ERROR: Tool version checker not found"
        exit 1
    fi
}

# Function to run forum monitoring
run_forum_monitoring() {
    echo ""
    echo "Running forum monitoring..."
    echo "=============================="
    
    if [ -f "scripts/forum-monitor.py" ]; then
        python3 scripts/forum-monitor.py
        echo "Forum monitoring completed"
    else
        echo "ERROR: Forum monitor not found"
        exit 1
    fi
}

# Function to update MCP server configurations
update_mcp_configs() {
    echo ""
    echo "Updating MCP server configurations..."
    echo "======================================="
    
    # Check if MCP servers are up to date
    if command -v npx &> /dev/null; then
        echo "Checking MCP server versions..."
        
        # Update context7 if available
        if npx --yes @upstash/context7-mcp --version &> /dev/null; then
            echo "Context7 MCP server is available"
        else
            echo "WARNING: Context7 MCP server not accessible - check configuration"
        fi
        
        # Update other MCP servers
        echo "MCP server check completed"
    else
        echo "WARNING: npm/npx not found - MCP servers may not be available"
    fi
}

# Function to generate weekly summary
generate_summary() {
    echo ""
    echo "Generating weekly summary..."
    echo "=============================="
    
    SUMMARY_FILE="reports/weekly-summary-$(date +%Y-%m-%d).md"
    
    cat > "$SUMMARY_FILE" << EOF
# Weekly AI Agent Development Update
*Generated: $(date)*

## Summary
This weekly update includes:
- Tool version checks and updates
- Community forum monitoring
- MCP server configuration updates
- Trending tool analysis

## Files Updated
- \`config/tools-tracking.json\` - Tool version tracking
- \`README.md\` - Updated with latest versions and trending tools
- \`reports/community-insights-$(date +%Y-%m-%d).md\` - Community insights
- \`reports/community-insights-$(date +%Y-%m-%d).json\` - Ranked discussion signals

## Next Steps
1. Review the community insights report for emerging trends
2. Use the JSON insights report for automation or dashboards
3. Evaluate any new trending tools for potential inclusion
4. Test any updated tool versions in development environment
5. Consider updating development workflow based on new findings

## Automation Status
- **Automated**: Tool version checking
- **Automated**: Forum monitoring
- **Automated**: README updates
- **Manual**: Tool evaluation and integration decisions

---
*This update was generated automatically by the AI Agent Development Workstation update system.*
EOF

    echo "Weekly summary generated: $SUMMARY_FILE"
}

# Function to commit and push changes if any
commit_and_push_changes() {
    echo ""
    echo "Checking for changes to commit..."
    echo "==================================="
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo "Not in a git repository - skipping commit"
        return 0
    fi
    
    # Check for any changes
    if git diff --quiet && git diff --cached --quiet; then
        echo "No changes to commit"
        return 0
    fi
    
    echo "Changes detected, creating commit..."
    
    # Show what will be committed
    echo "Files to be committed:"
    git status --porcelain
    
    # Add all tracked files that have been modified
    git add -u
    
    # Add new reports and logs
    git add reports/ logs/ 2>/dev/null || true
    
    # Add updated config
    git add config/tools-tracking.json 2>/dev/null || true
    
    # Add updated README if it was modified
    git add README.md 2>/dev/null || true
    
    # Create commit with detailed message
    commit_msg="Weekly automated update - $(date +%Y-%m-%d)

🤖 Automated Updates:
- Updated tool versions and tracking
- Added community insights report  
- Refreshed trending tools analysis
- Updated README with latest versions

📊 Update Summary:
$(git diff --cached --stat)

🔧 Generated by AI Agent Development Workstation automation"
    
    if git commit -m "$commit_msg"; then
        echo "✅ Changes committed successfully"
        echo "Commit hash: $(git rev-parse --short HEAD)"
        
        # Push changes to remote if configured
        push_changes
    else
        echo "❌ Failed to create commit"
        return 1
    fi
}

# Function to push changes to remote repository
push_changes() {
    echo ""
    echo "Pushing changes to remote repository..."
    echo "========================================"
    
    # Check if remote exists
    if ! git remote get-url origin > /dev/null 2>&1; then
        echo "No remote 'origin' configured - skipping push"
        return 0
    fi
    
    # Get current branch
    current_branch=$(git branch --show-current)
    
    if [ -z "$current_branch" ]; then
        echo "Unable to determine current branch - skipping push"
        return 1
    fi
    
    echo "Current branch: $current_branch"
    
    # Check if upstream is set
    if ! git rev-parse --abbrev-ref --symbolic-full-name @{u} > /dev/null 2>&1; then
        echo "Setting upstream for branch $current_branch"
        if git push --set-upstream origin "$current_branch"; then
            echo "✅ Upstream set and changes pushed successfully"
        else
            echo "❌ Failed to set upstream and push changes"
            return 1
        fi
    else
        # Push to existing upstream
        if git push; then
            echo "✅ Changes pushed successfully to $(git remote get-url origin)"
        else
            echo "❌ Failed to push changes"
            return 1
        fi
    fi
}

# Main execution
main() {
    echo "Starting automated update process..."
    
    # Check dependencies
    check_python_deps
    
    # Run tool checks
    run_tool_checks
    
    # Run forum monitoring
    run_forum_monitoring
    
    # Update MCP configurations
    update_mcp_configs
    
    # Generate summary
    generate_summary
    
    # Commit and push changes
    commit_and_push_changes
    
    echo ""
    echo "Weekly update completed successfully!"
    echo "======================================"
    echo "Completed: $(date)"
    echo "Log file: $LOG_FILE"
    echo ""
    echo "Next actions to consider:"
    echo "1. Review the generated reports in the reports/ directory"
    echo "2. Check for any new trending tools that might be worth investigating"
    echo "3. Test any updated tool versions in your development environment"
    echo "4. Consider updating your development workflow based on community insights"
    echo ""
}

# Run main function
main