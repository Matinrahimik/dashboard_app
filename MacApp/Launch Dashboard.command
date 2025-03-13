#!/bin/bash

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to that directory
cd "$DIR"

# Run the app
./SurveyDashboard

# If the app exits, keep the terminal window open for a moment
echo "Application closed. This window will close in 5 seconds..."
sleep 5 