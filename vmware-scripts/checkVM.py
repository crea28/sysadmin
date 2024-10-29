# https://vdc-repo.vmware.com/vmwb-repository/dcr-public/1ef6c336-7bef-477d-b9bb-caa1767d7e30/82521f49-9d9a-42b7-b19b-9e6cd9b30db1/index-properties.html

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl
import sys
import argparse

# vm_name in arg
parser = argparse.ArgumentParser(description='Get informations on virtual machine : ')
parser.add_argument('vm_name', type=str, help='vm name')
args = parser.parse_args()

# Credentials
vcenter_host = ""
vcenter_user = ""
vcenter_password = ""

# Connection
si = SmartConnect(
    host=vcenter_host,
    user=vcenter_user,
    pwd=vcenter_password,
    sslContext=ssl._create_unverified_context()
)

def get_vm_info(vm_object):
    vm_info = {
        "Name": vm_object.name,
        "CPU": vm_object.summary.config.numCpu,
        "Memory (GB)": vm_object.summary.config.memorySizeMB / 1024,
    }

    # Init total disk capacity
    total_disk_capacity_gb = 0
    
    # Get informations
    for device in vm_object.config.hardware.device:
        if isinstance(device, vim.vm.device.VirtualDisk):
            disk_capacity_gb = round(device.capacityInBytes / (1024 ** 3), 2)
            total_disk_capacity_gb += disk_capacity_gb

            disk_info = {
                "Disk capacity (GB)": disk_capacity_gb,
            }      

    # Total of disk capacity
    vm_info["Disk capacity (GB)"] = total_disk_capacity_gb

    # Add informations (snapshot)
    snapshot_info = get_snapshot_info(vm_object)
    vm_info["Snapshots"] = snapshot_info

    return vm_info

def get_snapshot_info(vm_object):
    # Check if snapshots are present
    if vm_object.snapshot is None or vm_object.snapshot.rootSnapshotList is None:
        return []

    # Get snapshots informations
    snapshot_info = []
    for snapshot in vm_object.snapshot.rootSnapshotList:
        # Formating Date
        formatted_create_time = snapshot.createTime.strftime("%d/%m/%Y %H:%M:%S")

        snapshot_info.append({
            "Snapshot name": snapshot.name,
            "Description": snapshot.description,
            "Creation Date ": formatted_create_time,
        })

    return snapshot_info

def display_info(info, indentation=0):
    for key, value in info.items():
        if isinstance(value, dict):
            print(f"{' ' * indentation}{key}:")
            display_info(value, indentation + 2)
        elif isinstance(value, list):
            print(f"{' ' * indentation}{key}:")
            for item in value:
                print(f"{' ' * (indentation + 2)}-")
                display_info(item, indentation + 4)
        else:
            print(f"{' ' * indentation}{key}: {value}")

def main():
    vm_name = args.vm_name
    if not si:
        print("Connexion on vCenter impossible.")
        sys.exit(1)

    # Get VM views
    content = si.RetrieveContent()
    vm_container = content.viewManager.CreateContainerView(
        content.rootFolder, [vim.VirtualMachine], True
    )

    # Search VM by name
    vm_object = None
    for vm in vm_container.view:
        if vm.name == vm_name:
            vm_object = vm
            break

    if not vm_object:
        print(f"VM '{vm_name}' doesn't exist.")
        sys.exit(1)

    # Get VM Informations
    vm_info = get_vm_info(vm_object)

    # Print informations
    print("VM Description :")
    display_info(vm_info)

    # Déconnecter
    vm_container.Destroy()
    Disconnect(si)

if __name__ == "__main__":
    main()
