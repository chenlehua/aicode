#!/bin/bash

# Start frontend server
cd "$(dirname "$0")/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start development server
echo "Starting frontend server on http://localhost:5173"
npm run dev
