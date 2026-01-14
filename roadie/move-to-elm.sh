#!/bin/bash

# Script to move Roadie into elm project
# Usage: ./move-to-elm.sh /path/to/elm/project

if [ -z "$1" ]; then
    echo "Usage: ./move-to-elm.sh /path/to/elm/project"
    echo "Example: ./move-to-elm.sh ~/Documents/elm"
    exit 1
fi

ELM_PATH="$1"
ROADIE_DEST="$ELM_PATH/roadie"

# Check if elm directory exists
if [ ! -d "$ELM_PATH" ]; then
    echo "Error: $ELM_PATH does not exist"
    exit 1
fi

# Create roadie directory in elm project
echo "Creating roadie folder in $ELM_PATH..."
mkdir -p "$ROADIE_DEST"

# Copy all files except .git
echo "Copying Roadie files..."
rsync -av --exclude='.git' --exclude='node_modules' --exclude='venv' --exclude='__pycache__' --exclude='.next' . "$ROADIE_DEST/"

echo "✅ Done! Roadie is now in $ROADIE_DEST"
echo ""
echo "Next steps:"
echo "1. cd $ELM_PATH"
echo "2. Update netlify.toml base directory to 'roadie/frontend'"
echo "3. Deploy to Netlify!"

