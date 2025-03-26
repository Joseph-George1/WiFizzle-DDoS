#!/bin/bash

# Define colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check for Python 3
if ! command -v python3 >/dev/null 2>&1; then
  echo -e "${RED}Looks like Python 3 decided to take a nap. Go wake it up! (Install required)${NC}"
  exit 1
fi

# Check for sudo privileges
if [ "$(id -u)" -ne 0 ]; then
  echo -e "${RED}Uh oh, seems you don't have the key to the castle! (Sudo privileges needed)${NC}"
  exit 1
fi

# Check for aircrack-ng installation
if ! command -v aircrack-ng >/dev/null 2>&1; then
  echo -e "${GREEN}aircrack-ng is missing in action! We'll try to recruit it for your mission.${NC}"
  if ! sudo apt install -y aircrack-ng; then
    echo -e "${RED}Oh no, the recruitment failed! Maybe a manual installation is needed.${NC}"
    exit 1
  fi
  echo -e "${GREEN}aircrack-ng joined the party! Let's crack some protocols ;).${NC}"
fi

# Define variables
script_name="WiFizzle"
python_script="WiFizzle_DDoS.py"
install_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec_path="/usr/local/bin/$script_name"

# Error handling function
handle_error() {
    echo -e "${RED}Error: $1${NC}"
    exit 1
}

# Create executable script
echo -e "${GREEN}Creating executable script...${NC}"
echo "#!/bin/bash" | sudo tee "$exec_path" > /dev/null
echo "cd \"$install_dir\" && python3 \"$python_script\"" | sudo tee -a "$exec_path" > /dev/null
sudo chmod +x "$exec_path" || handle_error "Failed to set permissions for $exec_path."

# Inform user
echo -e "${GREEN}Installation completed successfully.${NC}"
echo "You can now run \"$script_name\" from anywhere in the terminal."
