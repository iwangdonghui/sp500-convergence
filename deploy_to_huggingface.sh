#!/bin/bash

# 🚀 Deploy to Hugging Face Spaces Script
# This script helps deploy the S&P 500 GIPS Analysis Platform to Hugging Face Spaces

echo "🚀 S&P 500 GIPS Analysis Platform - Hugging Face Deployment"
echo "=========================================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the project root directory."
    exit 1
fi

echo "📁 Current directory: $(pwd)"
echo "✅ Found app.py - proceeding with deployment..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Error: Git repository not found. Please initialize git first."
    exit 1
fi

echo "✅ Git repository found"

# Check if Hugging Face CLI is installed
if ! command -v huggingface-cli &> /dev/null; then
    echo "⚠️  Hugging Face CLI not found. Installing..."
    pip install huggingface_hub
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Hugging Face CLI. Please install manually:"
        echo "   pip install huggingface_hub"
        exit 1
    fi
fi

echo "✅ Hugging Face CLI is available"

# Check current Hugging Face login status
echo "🔐 Checking Hugging Face authentication..."
huggingface-cli whoami

if [ $? -ne 0 ]; then
    echo "⚠️  Not logged in to Hugging Face. Please login:"
    echo "   You can login with your token or username/password"
    
    read -p "Do you want to login now? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        huggingface-cli login
        
        if [ $? -ne 0 ]; then
            echo "❌ Login failed. Please try again manually:"
            echo "   huggingface-cli login"
            exit 1
        fi
    else
        echo "❌ Please login to Hugging Face first:"
        echo "   huggingface-cli login"
        exit 1
    fi
fi

echo "✅ Hugging Face authentication successful"

# Check if Hugging Face remote exists
if git remote get-url hf &> /dev/null; then
    echo "✅ Hugging Face remote 'hf' found"
    HF_URL=$(git remote get-url hf)
    echo "   Remote URL: $HF_URL"
else
    echo "⚠️  Hugging Face remote 'hf' not found"
    read -p "Enter your Hugging Face Space URL (e.g., https://huggingface.co/spaces/username/space-name): " HF_SPACE_URL
    
    if [ -z "$HF_SPACE_URL" ]; then
        echo "❌ No URL provided. Exiting."
        exit 1
    fi
    
    echo "🔗 Adding Hugging Face remote..."
    git remote add hf "$HF_SPACE_URL"
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to add Hugging Face remote. Please check the URL."
        exit 1
    fi
    
    echo "✅ Hugging Face remote added successfully"
fi

# Check if there are uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  You have uncommitted changes:"
    git status --short
    
    read -p "Do you want to commit these changes? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter commit message: " COMMIT_MSG
        
        if [ -z "$COMMIT_MSG" ]; then
            COMMIT_MSG="Update for Hugging Face deployment"
        fi
        
        git add .
        git commit -m "$COMMIT_MSG"
        
        if [ $? -ne 0 ]; then
            echo "❌ Commit failed. Please check for errors."
            exit 1
        fi
        
        echo "✅ Changes committed successfully"
    else
        echo "⚠️  Proceeding with uncommitted changes..."
    fi
fi

# Push to Hugging Face
echo "🚀 Pushing to Hugging Face Spaces..."
echo "   This may take a few minutes depending on the size of your repository..."

git push hf main

if [ $? -eq 0 ]; then
    echo "🎉 Successfully deployed to Hugging Face Spaces!"
    echo ""
    echo "📋 Deployment Summary:"
    echo "   ✅ Code pushed to Hugging Face"
    echo "   ✅ Streamlit app will be automatically built"
    echo "   ✅ Your space should be available shortly"
    echo ""
    echo "🌐 Your Hugging Face Space:"
    HF_URL=$(git remote get-url hf)
    echo "   $HF_URL"
    echo ""
    echo "⏱️  Note: It may take a few minutes for your space to build and become available."
    echo "   You can check the build status on your Hugging Face Space page."
    echo ""
    echo "🎯 Features available in your deployed app:"
    echo "   • 📊 S&P 500 data analysis and visualization"
    echo "   • 🏛️ GIPS compliance analysis and reporting"
    echo "   • 🔍 Multi-asset analysis with efficient frontier"
    echo "   • 📋 Professional PDF report generation"
    echo "   • 🎨 Optimized fonts for Chinese and financial data"
    echo ""
    echo "✨ Your S&P 500 GIPS Analysis Platform is now live!"
    
else
    echo "❌ Failed to push to Hugging Face Spaces"
    echo ""
    echo "🔧 Troubleshooting steps:"
    echo "   1. Check your internet connection"
    echo "   2. Verify your Hugging Face authentication:"
    echo "      huggingface-cli whoami"
    echo "   3. Check if you have write access to the space"
    echo "   4. Try logging in again:"
    echo "      huggingface-cli login"
    echo "   5. Check the Hugging Face remote URL:"
    echo "      git remote -v"
    echo ""
    echo "📞 If problems persist, check:"
    echo "   • Hugging Face Space settings and permissions"
    echo "   • Repository size limits"
    echo "   • Network connectivity"
    
    exit 1
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo "Thank you for using the S&P 500 GIPS Analysis Platform! 🏛️📈"
