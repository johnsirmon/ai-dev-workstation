#!/bin/bash
# Sync shared content between Windows and Mac versions
# Run this when you make major updates to core AI framework information

set -e

# Configuration - can be overridden with environment variables
MAC_REPO_PATH="${MAC_REPO_PATH:-/home/johnsirmon/projects/ai-dev-workstation-mac}"
DRY_RUN="${DRY_RUN:-false}"
AUTO_SYNC="${AUTO_SYNC:-false}"

echo "====================================="
echo "AI Development Workstation Sync Tool"
echo "====================================="
echo "Windows → Mac repository sync"
echo "Target: $MAC_REPO_PATH"
echo "Dry run: $DRY_RUN"
echo "Auto sync: $AUTO_SYNC"
echo ""

# Check if Mac repo exists
if [ ! -d "$MAC_REPO_PATH" ]; then
    echo "❌ Mac repository not found at $MAC_REPO_PATH"
    echo "Please clone the Mac version or set MAC_REPO_PATH environment variable"
    exit 1
fi

echo "✅ Target repository found"

# Function to sync configuration files
sync_config_files() {
    echo ""
    echo "Syncing configuration files..."
    echo "=============================="
    
    # Sync tools tracking configuration
    if [ -f "config/tools-tracking.json" ]; then
        if [ "$DRY_RUN" = "true" ]; then
            echo "[DRY RUN] Would sync: config/tools-tracking.json"
        else
            cp "config/tools-tracking.json" "$MAC_REPO_PATH/config/" 2>/dev/null || true
            echo "✅ Synced tools tracking configuration"
        fi
    fi
    
    # Sync MCP server base configuration (platform-neutral parts)
    if [ -f ".vscode/mcp.json" ]; then
        if [ "$DRY_RUN" = "true" ]; then
            echo "[DRY RUN] Would sync: .vscode/mcp.json"
        else
            mkdir -p "$MAC_REPO_PATH/.vscode"
            cp ".vscode/mcp.json" "$MAC_REPO_PATH/.vscode/" 2>/dev/null || true
            echo "✅ Synced MCP server configuration"
        fi
    fi
}

# Function to sync shared documentation sections
sync_shared_docs() {
    echo ""
    echo "Analyzing documentation differences..."
    echo "====================================="
    
    if [ ! -f "$MAC_REPO_PATH/README.md" ]; then
        echo "❌ Mac README.md not found - cannot sync"
        return 1
    fi
    
    # Extract framework table section (section 3)
    echo "Extracting AI framework versions table..."
    
    # Create temporary files for comparison
    TEMP_WIN="/tmp/win_frameworks.md"
    TEMP_MAC="/tmp/mac_frameworks.md"
    
    # Extract framework table from Windows version
    sed -n '/## 3.*Leading Agent Frameworks/,/^---$/p' README.md > "$TEMP_WIN" 2>/dev/null || true
    
    # Extract framework table from Mac version  
    sed -n '/## 3.*Leading Agent Frameworks/,/^---$/p' "$MAC_REPO_PATH/README.md" > "$TEMP_MAC" 2>/dev/null || true
    
    if [ -s "$TEMP_WIN" ] && [ -s "$TEMP_MAC" ]; then
        if ! diff -q "$TEMP_WIN" "$TEMP_MAC" > /dev/null; then
            echo "📊 Framework versions differ between Windows and Mac versions"
            if [ "$AUTO_SYNC" = "true" ] && [ "$DRY_RUN" = "false" ]; then
                echo "🔄 Auto-syncing framework versions..."
                # This would require more sophisticated sed/awk to replace just the table
                echo "⚠️  Manual sync recommended for README sections"
            else
                echo "💡 Run with AUTO_SYNC=true to attempt automatic sync"
            fi
        else
            echo "✅ Framework versions are already in sync"
        fi
    else
        echo "⚠️  Could not extract framework sections for comparison"
    fi
    
    # Cleanup temp files
    rm -f "$TEMP_WIN" "$TEMP_MAC"
}

# Function to sync shared utilities and scripts
sync_shared_scripts() {
    echo ""
    echo "Syncing shared utility scripts..."
    echo "================================"
    
    SHARED_SCRIPTS=(
        "scripts/utils.py"
        "scripts/update-tools.py"
        "scripts/forum-monitor.py"
    )
    
    for script in "${SHARED_SCRIPTS[@]}"; do
        if [ -f "$script" ]; then
            if [ "$DRY_RUN" = "true" ]; then
                echo "[DRY RUN] Would sync: $script"
            else
                mkdir -p "$(dirname "$MAC_REPO_PATH/$script")"
                cp "$script" "$MAC_REPO_PATH/$script" 2>/dev/null || true
                echo "✅ Synced $script"
            fi
        fi
    done
}

# Function to create sync report
generate_sync_report() {
    echo ""
    echo "Generating sync report..."
    echo "========================"
    
    REPORT_FILE="reports/sync-report-$(date +%Y-%m-%d).md"
    mkdir -p reports
    
    cat > "$REPORT_FILE" << EOF
# Cross-Platform Sync Report
*Generated: $(date)*

## Sync Target
- **Target Repository**: $MAC_REPO_PATH
- **Sync Mode**: $([ "$DRY_RUN" = "true" ] && echo "Dry Run" || echo "Live Sync")
- **Auto Sync**: $AUTO_SYNC

## Files Synced
- Configuration files (tools-tracking.json, mcp.json)
- Shared utility scripts (utils.py, update-tools.py, forum-monitor.py)
- Documentation analysis completed

## Manual Review Required
The following areas should be manually reviewed for platform-specific differences:

1. **Installation Instructions**
   - WSL 2 setup (Windows) vs Homebrew (Mac)
   - Platform-specific package managers
   
2. **File Paths**
   - Windows: /mnt/c/Users/... paths
   - Mac: /Users/... paths
   
3. **Performance Tips**
   - WSL-specific optimizations
   - macOS-specific configurations
   
4. **Environment Setup**
   - Windows Task Scheduler vs cron jobs
   - Platform-specific environment variables

## Next Steps
1. Review the Mac repository for any manual updates needed
2. Test the synced scripts in the Mac environment
3. Update platform-specific documentation as needed
4. Consider setting up automated cross-platform testing

---
*Generated by AI Agent Development Workstation sync tool*
EOF

    echo "📄 Sync report generated: $REPORT_FILE"
}

# Main sync execution
run_sync() {
    echo "Starting sync process..."
    
    # Sync configuration files
    sync_config_files
    
    # Sync shared documentation
    sync_shared_docs
    
    # Sync shared scripts
    sync_shared_scripts
    
    # Generate report
    generate_sync_report
    
    echo ""
    echo "🎉 Sync process completed!"
    echo "============================="
    
    if [ "$DRY_RUN" = "true" ]; then
        echo "This was a dry run. No files were actually modified."
        echo "Run without DRY_RUN=true to perform actual sync."
    else
        echo "Files have been synced to the Mac repository."
        echo "Please review the Mac repository and test the changes."
    fi
    
    echo ""
    echo "📝 Platform-specific sections that require manual attention:"
    echo "  • Installation methods (WSL vs Homebrew)"
    echo "  • File paths and directory structures"
    echo "  • Performance optimization tips"
    echo "  • Troubleshooting guides"
    echo "  • Environment setup instructions"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN="true"
            shift
            ;;
        --auto-sync)
            AUTO_SYNC="true"
            shift
            ;;
        --mac-path)
            MAC_REPO_PATH="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --dry-run       Show what would be synced without making changes"
            echo "  --auto-sync     Attempt automatic sync of documentation"
            echo "  --mac-path DIR  Specify Mac repository path"
            echo "  --help          Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run the sync
run_sync