import requests
import urllib3
import os
from dotenv import load_dotenv

urllib3.disable_warnings()

load_dotenv()

PROXMOX_HOST = os.getenv("PROXMOX_HOST")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
REALM = os.getenv("REALM")
NODE = os.getenv("NODE")

print(PROXMOX_HOST, USERNAME, PASSWORD, REALM, NODE)

def get_proxmox_token():
    url = f"https://{PROXMOX_HOST}:8006/api2/json/access/ticket"
    data = {
        "username": USERNAME,
        "password": PASSWORD,
        "realm": REALM,
    }
    response = requests.post(url, data=data, verify=False)
    response.raise_for_status()
    result = response.json()["data"]
    return result["ticket"], result["CSRFPreventionToken"]


def list_vms():
    
    ticket, csrf_token = get_proxmox_token()
    headers = {
        "Cookie": f"PVEAuthCookie={ticket}",
        "CSRFPreventionToken": csrf_token,
    }
    url = f"https://{PROXMOX_HOST}:8006/api2/json/cluster/resources?type=vm"
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    
    vms = response.json()["data"]
    qemu_vms = []
    lxc_vms = []
    
    for vm in vms:
        if vm["type"] == "qemu":
            qemu_vms.append(vm)
        elif vm["type"] == "lxc":
            lxc_vms.append(vm)
    
    return qemu_vms, lxc_vms

def control_vm(vmid, action):
    ticket, csrf_token = get_proxmox_token()
    headers = {
        "Cookie": f"PVEAuthCookie={ticket}",
        "CSRFPreventionToken": csrf_token,
    }
    
    url = f"https://{PROXMOX_HOST}:8006/api2/json/nodes/{NODE}/qemu/{vmid}/status/{action}"
    
    response = requests.post(url, headers=headers, verify=False)
    response.raise_for_status()
    
    return response.json()

if __name__ == "__main__":
    print(list_vms())