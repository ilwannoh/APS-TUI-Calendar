#!/bin/bash

echo "Starting APS Web Application..."
echo

# Function to kill processes on exit
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

# Set up trap to clean up on script exit
trap cleanup EXIT INT TERM

# Start backend server
echo "Starting backend server..."
cd backend
python main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend server
echo "Starting frontend server..."
cd ../frontend
python -m http.server 3000 &
FRONTEND_PID=$!

echo
echo "Application started!"
echo "Backend API: http://localhost:8000"
echo "Frontend UI: http://localhost:3000"
echo
echo "Press Ctrl+C to stop servers..."

# Wait for user interrupt
wait