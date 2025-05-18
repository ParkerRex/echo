#!/bin/bash

# Get the app directory
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$APP_DIR"

# Define test directories to clean
TEST_UPLOADS_DIR="$APP_DIR/output_files/uploads/test"
TEST_USER_UPLOADS_DIR="$APP_DIR/output_files/uploads/test-user-id"

# Also check for and clean the incorrect path that might have been created
INCORRECT_PATH="$(cd "$APP_DIR/.." && pwd)/output_files/uploads/test"

echo "Cleaning test files..."

# Remove files in test directory
if [ -d "$TEST_UPLOADS_DIR" ]; then
    echo "Removing files from $TEST_UPLOADS_DIR"
    rm -rf "$TEST_UPLOADS_DIR"/*
    echo "✓ Test directory cleaned"
fi

# Remove mp4 files in test-user-id directory
if [ -d "$TEST_USER_UPLOADS_DIR" ]; then
    echo "Removing mp4 files from $TEST_USER_UPLOADS_DIR"
    rm -rf "$TEST_USER_UPLOADS_DIR"/*.mp4
    echo "✓ Test user files cleaned"
fi

# Clean incorrect path if it exists
if [ -d "$INCORRECT_PATH" ]; then
    echo "Cleaning incorrect path: $INCORRECT_PATH"
    rm -rf "$INCORRECT_PATH"
    echo "✓ Incorrect path removed"
fi

# Recreate the test directory structure
mkdir -p "$TEST_UPLOADS_DIR"

echo "Test files cleanup complete!" 