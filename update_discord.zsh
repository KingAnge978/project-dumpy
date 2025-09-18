#!/usr/bin/env zsh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    echo -e "${RED}Error: Do not run this script as root.${NC}"
    exit 1
fi

echo -e "${YELLOW}Updating Discord...${NC}"

# Download latest Discord .tar.gz
echo -e "${GREEN}Downloading the latest Discord for Linux...${NC}"
wget -q --show-progress "https://discord.com/api/download?platform=linux&format=tar.gz" -O /tmp/discord.tar.gz || {
    echo -e "${RED}Failed to download Discord. Check your internet connection.${NC}"
    exit 1
}

# Extract the .tar.gz
echo -e "${GREEN}Extracting files...${NC}"
tar -xzf /tmp/discord.tar.gz -C /tmp/ || {
    echo -e "${RED}Failed to extract Discord. Corrupted download?${NC}"
    exit 1
}

# Stop Discord if running
echo -e "${YELLOW}Stopping running Discord processes...${NC}"
pkill -f Discord || echo -e "${YELLOW}Discord was not running.${NC}"

# Move to /opt/Discord (requires sudo)
echo -e "${GREEN}Installing to /opt/Discord...${NC}"
sudo rm -rf /opt/Discord 2>/dev/null
sudo mv /tmp/Discord /opt/Discord || {
    echo -e "${RED}Failed to move Discord to /opt/Discord.${NC}"
    exit 1
}

# Update symlink in /usr/bin
echo -e "${GREEN}Updating symlink...${NC}"
sudo ln -sf /opt/Discord/Discord /usr/bin/discord || {
    echo -e "${YELLOW}Could not update symlink. Continuing anyway.${NC}"
}

# Create and install a proper .desktop file
echo -e "${GREEN}Creating .desktop file...${NC}"
cat <<EOF | sudo tee /usr/share/applications/discord.desktop >/dev/null
[Desktop Entry]
Name=Discord
Exec=/usr/bin/discord
Icon=discord
Type=Application
Categories=Network;InstantMessaging;
StartupWMClass=discord
EOF

# Update desktop database
sudo update-desktop-database /usr/share/applications

# Cleanup
rm -f /tmp/discord.tar.gz

echo -e "${GREEN}Discord has been updated successfully!${NC}"
echo -e "${YELLOW}You can now launch Discord from your app menu or by running 'discord'.${NC}"

