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
TLSVEIFY=False

PASSWORD = os.getenv("PASSWORD")

def get_proxmox_token():
    url = f"https://{PROXMOX_HOST}:8006/api2/json/access/ticket"
    data = {
        "username": USERNAME,
        "password": PASSWORD,
        "realm": REALM,
    }
    
    response = requests.post(url, data=data, verify=TLSVEIFY)
    
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
    response = requests.get(url, headers=headers, verify=TLSVEIFY)
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
    
    qemu_response = requests.get(url + "qemu", headers=headers, verify=TLSVEIFY)
    qemu_vms = qemu_response.json().get("data", [])
    #fix
    lxc_response = requests.get(url + "lxc", headers=headers, verify=TLSVEIFY)
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
    
    response = requests.post(url, headers=headers, verify=TLSVEIFY)
    response.raise_for_status()
    
    return response.json()

def create_vm(vmid, node=NODE, iso=None, storage='local', **kwargs):
    ticket, csrf_token = get_proxmox_token()
    headers = {
        "Cookie": f"PVEAuthCookie={ticket}",
        "CSRFPreventionToken": csrf_token,
    }
    
    url = f"https://{PROXMOX_HOST}:8006/api2/json/nodes/{node}/qemu"
    
    data = {'vmid': vmid}
    
    if iso:
        data['ide2'] = f"{storage}:iso/{iso},media=cdrom"
    
    for key, value in kwargs.items():
        if isinstance(value, bool):
            data[key] = 1 if value else 0
        else:
            data[key] = value
    
    response = requests.post(url, headers=headers, data=data, verify=TLSVEIFY)
    response.raise_for_status()
    
    return response.json()

def get_vm_creation_info(node=NODE):
    ticket, csrf_token = get_proxmox_token()
    headers = {
        "Cookie": f"PVEAuthCookie={ticket}",
        "CSRFPreventionToken": csrf_token,
    }

    iso_url = f"https://{PROXMOX_HOST}:8006/api2/json/nodes/{node}/storage/local/content"
    iso_response = requests.get(iso_url, headers=headers, verify=TLSVEIFY)
    iso_response.raise_for_status()
    isos = [iso['volid'] for iso in iso_response.json()["data"] if iso.get('content') == 'iso']


    node_url = f"https://{PROXMOX_HOST}:8006/api2/json/nodes/{node}/status"
    node_response = requests.get(node_url, headers=headers, verify=TLSVEIFY)
    node_response.raise_for_status()
    node_data = node_response.json()["data"]

    memory_info = node_data.get("memory", {})
    total_ram = memory_info.get("total", 0)
    total_ram_mb = round(total_ram / (1024 * 1024), 2)

    max_cores = None

    storage_url = f"https://{PROXMOX_HOST}:8006/api2/json/nodes/{node}/storage"
    storage_response = requests.get(storage_url, headers=headers, verify=TLSVEIFY)
    storage_response.raise_for_status()
    lvm_storage = []
    for storage in storage_response.json()["data"]:
        if storage.get('type') in ('lvm', 'lvmthin'):
            avail = storage.get('avail')
            if avail is not None:
                free_gb = round(avail / (1024**3), 2)
                free_str = f"{free_gb}GB free"
            else:
                free_str = "N/A"
            lvm_storage.append({
                "name": storage['storage'],
                "free": free_str
            })

    network_url = f"https://{PROXMOX_HOST}:8006/api2/json/nodes/{node}/network"
    network_response = requests.get(network_url, headers=headers, verify=TLSVEIFY)
    network_response.raise_for_status()
    network_data = network_response.json()["data"]
    networks = [network['iface'] for network in network_data if network.get('iface', '').startswith("vmbr")]

    return {
        "isos": isos,
        "max_ram_mb": total_ram_mb,
        "max_cores": max_cores,
        "lvm_storage": lvm_storage,
        "networks": networks
    }

def getbiostype(vmid,node=NODE):

    ticket, csrf_token = get_proxmox_token()
    headers = {
        "Cookie": f"PVEAuthCookie={ticket}",
        "CSRFPreventionToken": csrf_token,
    }

    bios_url = f"https://{PROXMOX_HOST}:8006/api2/json/nodes/{node}/qemu/{vmid}/config"
    bios_response = requests.get(bios_url, headers=headers, verify=TLSVEIFY)
    bios_response.raise_for_status()
    bios_data = bios_response.json()["data"]
    bios_type = bios_data.get('bios', '')
    return bios_type


if __name__ == "__main__":
    #print(list_vms())
    #print(get_vm_type(105))

    print(getbiostype(107))

    #data = get_vm_creation_info()
    #print(data)

#    create_vm(201,
#            iso='archlinux-2025.03.01-x86_64.iso',
#            storage='local',
#            memory=4096,
#            cores=4,
#            ostype='l26',
#            ide0='local-lvm:32',
#            net0='virtio,bridge=vmbr0',
#            boot='order=ide2;virtio0')