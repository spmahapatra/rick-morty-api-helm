#!/bin/bash

#############################################################################
# Local Release Review Script
#
# Purpose: Help developers review changes before creating a release tag
# Usage: ./scripts/review-release.sh [previous-tag]
# Example: ./scripts/review-release.sh v1.0.0
#
# This script performs comprehensive local review before tag creation:
# - Shows commit log since last tag
# - Shows file changes
# - Runs tests
# - Runs linting
# - Validates version consistency
#############################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LATEST_TAG=""

###############################################################################
# Helper Functions
###############################################################################

print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}${1}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ ${1}${NC}"
}

print_error() {
    echo -e "${RED}❌ ${1}${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  ${1}${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  ${1}${NC}"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_error "$1 is not installed"
        exit 1
    fi
}

###############################################################################
# Git Operations
###############################################################################

get_latest_tag() {
    if git describe --tags --abbrev=0 2>/dev/null; then
        return
    else
        echo "No previous tags found"
    fi
}

get_commits_since_tag() {
    local tag="$1"
    if [ -z "$tag" ]; then
        git log --oneline HEAD
    else
        git log "${tag}..HEAD" --oneline
    fi
}

get_changed_files() {
    local tag="$1"
    if [ -z "$tag" ]; then
        git diff --name-only --cached
    else
        git diff "${tag}..HEAD" --name-only
    fi
}

get_file_diff() {
    local tag="$1"
    if [ -z "$tag" ]; then
        git diff --cached
    else
        git diff "${tag}..HEAD"
    fi
}

###############################################################################
# Validation Checks
###############################################################################

check_working_tree_clean() {
    print_header "Checking Git Working Tree"
    
    if [ -n "$(git status --porcelain)" ]; then
        print_error "Working tree is dirty. Commit all changes first:"
        git status --short
        return 1
    fi
    
    print_success "Working tree is clean"
    return 0
}

check_commits_exist() {
    local tag="$1"
    print_header "Reviewing Commits"
    
    local commits
    commits=$(get_commits_since_tag "$tag")
    
    if [ -z "$commits" ]; then
        print_warning "No commits found since tag: $tag"
        return 1
    fi
    
    echo "Commits since ${tag:-initial}:"
    echo "$commits"
    print_success "Commits exist and ready for release"
    return 0
}

check_tests_pass() {
    print_header "Running Tests"
    
    if [ ! -f "$PROJECT_ROOT/tests" ] && [ ! -f "$PROJECT_ROOT/pytest.ini" ]; then
        print_warning "No test suite detected, skipping tests"
        return 0
    fi
    
    if ! pytest tests/ -v --tb=short 2>/dev/null; then
        print_error "Tests failed. Fix issues before creating release tag."
        return 1
    fi
    
    print_success "All tests passed"
    return 0
}

check_linting() {
    print_header "Running Linting Checks"
    
    local lint_failed=0
    
    # Check black formatting
    if command -v black &> /dev/null; then
        if ! black --check src/ 2>/dev/null; then
            print_warning "Code formatting issues detected. Run: black src/"
            lint_failed=1
        else
            print_success "Black formatting OK"
        fi
    fi
    
    # Check flake8
    if command -v flake8 &> /dev/null; then
        if ! flake8 src/ 2>/dev/null; then
            print_warning "Flake8 issues detected. Run: flake8 src/"
            lint_failed=1
        else
            print_success "Flake8 checks OK"
        fi
    fi
    
    # Check pylint
    if command -v pylint &> /dev/null; then
        if ! pylint src/ 2>/dev/null; then
            print_warning "Pylint issues detected. Run: pylint src/"
            lint_failed=1
        else
            print_success "Pylint checks OK"
        fi
    fi
    
    return $lint_failed
}

check_version_consistency() {
    print_header "Checking Version Consistency"
    
    local version_file="$PROJECT_ROOT/src/__init__.py"
    
    if [ ! -f "$version_file" ]; then
        print_warning "Version file not found: $version_file"
        return 0
    fi
    
    # Extract version from __init__.py
    if grep -q "__version__" "$version_file"; then
        print_success "Version defined in $version_file"
        grep "__version__" "$version_file"
    else
        print_warning "No __version__ found in $version_file"
    fi
    
    return 0
}

check_changelog_updated() {
    print_header "Checking CHANGELOG"
    
    if [ ! -f "$PROJECT_ROOT/CHANGELOG.md" ]; then
        print_warning "CHANGELOG.md not found"
        return 0
    fi
    
    # Check if CHANGELOG has been modified recently
    if git diff HEAD CHANGELOG.md | grep -q "^+"; then
        print_success "CHANGELOG.md has been updated"
        echo ""
        echo "Recent changes:"
        git diff HEAD CHANGELOG.md | head -20
    else
        print_warning "CHANGELOG.md does not appear to have changes in working tree"
    fi
    
    return 0
}

###############################################################################
# Change Review
###############################################################################

show_file_changes() {
    local tag="$1"
    print_header "Files Changed"
    
    local changed_files
    changed_files=$(get_changed_files "$tag")
    
    if [ -z "$changed_files" ]; then
        print_warning "No files changed since $tag"
        return 0
    fi
    
    echo "Changed files:"
    echo "$changed_files" | sed 's/^/  /'
    
    return 0
}

show_detailed_diff() {
    local tag="$1"
    print_header "Detailed Diff"
    
    echo "Showing first 100 lines of changes (use 'git diff $tag..HEAD' to view all)"
    echo ""
    get_file_diff "$tag" | head -100
    
    if [ "$(get_file_diff "$tag" | wc -l)" -gt 100 ]; then
        print_info "Output truncated. View all changes with: git diff $tag..HEAD"
    fi
}

###############################################################################
# Release Preparation
###############################################################################

suggest_new_version() {
    local tag="$1"
    
    if [ -z "$tag" ]; then
        echo "v1.0.0"
        return
    fi
    
    # Extract version parts
    local major minor patch
    major=$(echo "$tag" | sed 's/v\([0-9]*\)\.\([0-9]*\)\.\([0-9]*\).*/\1/')
    minor=$(echo "$tag" | sed 's/v\([0-9]*\)\.\([0-9]*\)\.\([0-9]*\).*/\2/')
    patch=$(echo "$tag" | sed 's/v\([0-9]*\)\.\([0-9]*\)\.\([0-9]*\).*/\3/')
    
    # Default to patch version bump
    patch=$((patch + 1))
    
    echo "v${major}.${minor}.${patch}"
}

prompt_create_tag() {
    local tag="$1"
    local message="$2"
    
    print_header "Create Release Tag"
    
    echo "Tag name: $tag"
    echo "Message: $message"
    echo ""
    read -p "Create tag? (y/n) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git tag -a "$tag" -m "$message"
        print_success "Tag created: $tag"
        echo ""
        print_info "Push tag to trigger CI/CD:"
        echo "  git push origin $tag"
        return 0
    else
        print_warning "Tag creation cancelled"
        return 1
    fi
}

###############################################################################
# Main Execution
###############################################################################

main() {
    print_header "🚀 Local Release Review Script"
    
    # Check required commands
    check_command git
    
    # Get latest tag
    LATEST_TAG=$(get_latest_tag)
    
    if [ "$LATEST_TAG" = "No previous tags found" ]; then
        print_warning "No previous tags found. This will be v1.0.0"
        LATEST_TAG=""
    else
        print_info "Latest tag: $LATEST_TAG"
    fi
    
    # Run validation checks
    check_working_tree_clean || exit 1
    check_commits_exist "$LATEST_TAG" || exit 1
    
    # Show changes
    echo ""
    show_file_changes "$LATEST_TAG"
    show_detailed_diff "$LATEST_TAG"
    
    # Run quality checks (non-blocking)
    echo ""
    check_tests_pass || print_warning "Tests should be fixed before release"
    echo ""
    check_linting || print_warning "Linting issues should be addressed"
    echo ""
    check_version_consistency
    echo ""
    check_changelog_updated
    
    # Suggest next version
    print_header "Release Preparation"
    local suggested_version
    suggested_version=$(suggest_new_version "$LATEST_TAG")
    
    echo "Suggested new version: $suggested_version"
    read -p "Enter tag name (or press Enter for suggested): " new_tag
    new_tag="${new_tag:-$suggested_version}"
    
    # Validate tag format
    if ! [[ $new_tag =~ ^v[0-9]+\.[0-9]+\.[0-9]+ ]]; then
        print_error "Invalid tag format: $new_tag"
        print_info "Use format: v{major}.{minor}.{patch} (e.g., v1.2.3)"
        exit 1
    fi
    
    # Prompt for tag message
    read -p "Enter release message: " tag_message
    tag_message="${tag_message:-Release $new_tag}"
    
    # Create tag
    prompt_create_tag "$new_tag" "$tag_message"
}

# Run main function
main "$@"
