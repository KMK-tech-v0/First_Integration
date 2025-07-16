import subprocess

def get_wifi_passwords():
    try:
        # Get the list of Wi-Fi profiles
        profiles_data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles'], encoding='utf-8')
        profiles = [line.split(":")[1].strip() for line in profiles_data.splitlines() if "All User Profile" in line]

        wifi_passwords = {}
        for profile in profiles:
            # Get the details of each profile
            profile_info = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', profile, 'key=clear'], encoding='utf-8')
            # Extract the password
            password_line = [line for line in profile_info.splitlines() if "Key Content" in line]
            password = password_line[0].split(":")[1].strip() if password_line else None
            wifi_passwords[profile] = password

        return wifi_passwords
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    passwords = get_wifi_passwords()
    if passwords:
        for wifi, password in passwords.items():
            print(f"Wi-Fi: {wifi}, Password: {password if password else 'No password found'}")
