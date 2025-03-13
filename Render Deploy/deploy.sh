#!/bin/bash

# This script helps prepare and deploy the application to Render

echo "Preparing files for Render deployment..."

# Check if render-cli is installed
if ! command -v render &> /dev/null
then
    echo "render-cli not found. You can deploy manually by following the instructions in README.md"
    echo "Or install render-cli: npm install -g @render/cli"
else
    echo "render-cli found. You can deploy using: render deploy"
fi

echo "Files are ready for deployment!"
echo "Follow the instructions in README.md to deploy your application to Render."
echo "Once deployed, you can share the URL with anyone to access your dashboard." 