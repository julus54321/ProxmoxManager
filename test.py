import requests
import urllib3
import os
from dotenv import load_dotenv

urllib3.disable_warnings()

load_dotenv()

USERNAME = "root"
REALM= "pam"
PROXMOX_HOST= "192.168.55.5"
NODE="pve"

PASSWORD = os.getenv("PASSWORD")

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

def get_vm_type(vmid):
    ticket, csrf_token = get_proxmox_token()
    headers = {
        "Cookie": f"PVEAuthCookie={ticket}",
        "CSRFPreventionToken": csrf_token,
    }
    
    url = f"https://{PROXMOX_HOST}:8006/api2/json/nodes/{NODE}/"
    
    qemu_response = requests.get(url + "qemu", headers=headers, verify=False)
    qemu_vms = qemu_response.json().get("data", [])
    
    lxc_response = requests.get(url + "lxc", headers=headers, verify=False)
    lxc_containers = lxc_response.json().get("data", [])
    
    for vm in qemu_vms:
        if str(vm["vmid"]) == str(vmid):
            return "qemu"
    
    for container in lxc_containers:
        if str(container["vmid"]) == str(vmid):
            return "lxc"
    
    return None 

def control_vm(vmid, action):
    vm_type = get_vm_type(vmid)
    if not vm_type:
        raise ValueError(f"VMID {vmid} not found on node {NODE}.")
    
    ticket, csrf_token = get_proxmox_token()
    headers = {
        "Cookie": f"PVEAuthCookie={ticket}",
        "CSRFPreventionToken": csrf_token,
    }
    
    url = f"https://{PROXMOX_HOST}:8006/api2/json/nodes/{NODE}/{vm_type}/{vmid}/status/{action}"
    
    response = requests.post(url, headers=headers, verify=False)
    response.raise_for_status()
    
    return response.json()

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
    print(get_vm_type(105))