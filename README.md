# ProxmoxManager

## Overview
ProxmoxManager is a simple web-based Proxmox VM management tool. This project is in its early stages, aiming to provide a lightweight interface for interacting with Proxmox virtual machines.

## TODO

### VM Creation Enhancements
- [ ] Add BIOS selection option (**UEFI** or **SeaBIOS**)  
- [x] Add machine type selection (**Q35** or **i440fx**) --------- instad setting q35 to all because its newer and better 
- [ ] Implement UI elements for selecting BIOS and machine type in `/admin/createvm`  

### VM Management Features
- [ ] Display BIOS type for each VM in `/admin/vms`  
- [x] Add an option to start the VM immediately after creation in `/admin/createvm`  --- set on by default
- [ ] Implement auto-start setting in `/admin/createvm` (so VMs boot with the host)  
- [ ] Display & allow modification of VM auto-start settings in `/admin/vms`  
