#!/bin/bash

# Define colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check for Python 3
python3 --version >/dev/null 2>&1 || {
  echo -e "${RED}Looks like Python 3 decided to take a nap. Go wake it up! (Install required)${NC}"
  exit 1
}

# Check for sudo privileges
sudo ls / >/dev/null 2>&1 || {
  echo -e "${RED}Uh oh, seems you don't have the key to the castle! (Sudo privileges needed)${NC}"
  exit 1
}

# Check for aircrack-ng installation
aircrack-ng --version >/dev/null 2>&1 || {
  echo -e "${GREEN}aircrack-ng is missing in action! We'll try to recruit it for your mission.${NC}"
  sudo apt install -y aircrack-ng || {
    echo -e "${RED}Oh no, the recruitment failed! Maybe a manual installation is needed.${NC}"
    exit 1
  }
  echo -e "${GREEN}aircrack-ng joined the party! Let's crack some protocols ;).${NC}"
}

# Define variables
script_name="WiFizzle"
python_script="WiFizzle-DDoS.py"
install_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Error handling function
handle_error() {
    echo -e "${RED}Error: $1${NC}"
    exit 1
}

# Create executable script
echo -e "${GREEN}Creating executable script...${NC}"
echo "#!/bin/bash" | sudo tee "/bin/$script_name" > /dev/null
echo "cd \"$install_dir\" && python3 \"$python_script\"" | sudo tee -a "/bin/$script_name" > /dev/null
sudo chmod +x "/bin/$script_name" || handle_error "Failed to set permissions for /bin/$script_name."

# Inform user
echo -e "${GREEN}Installation completed successfully.${NC}"
echo "You can now run \"$script_name\" to execute the script."
