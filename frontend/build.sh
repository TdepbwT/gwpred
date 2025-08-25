#!/bin/bash
set -e

echo "Starting build process..."

# Install dependencies
npm ci

# Build the project using npx to avoid permission issues
npx vite build

echo "Build completed successfully!"
