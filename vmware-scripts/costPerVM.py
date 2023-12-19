from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl
import sys
import csv
import datetime

# VMWare settings
vcenter_hosts = [
    {"host": "vmware-1", "user": "", "password": ""},
    {"host": "vmware-2", "user": "", "password": ""},
    {"host": "vmware-3", "user": "", "password": ""},
]

## Datastore Cost per Go
datastore_capacity_vmware1 = 1000
datastore_cost_per_gb_vmware1 = 0.01
datastore_cost_vmware1 = 100

datastore_capacity_vmware2 = 1000
datastore_cost_per_gb_vmware2 = 0.01
datastore_cost_vmware2 = 100

## Host Cost
host_cost_vmware1 = 1000
host_cost_vmware2 = 1000

def calculate_vm_storage_cost(vm_object, datastore_cost_per_gb):
    # Sum of the entire VM disk capacity
    total_disk_capacity_gb = 0
    
    # Get the disk informations
    for device in vm_object.config.hardware.device:
        if isinstance(device, vim.vm.device.VirtualDisk):
            disk_capacity_gb = round(device.capacityInBytes / (1024 ** 3), 2)
            total_disk_capacity_gb += disk_capacity_gb

            disk_info = {
                "Total Capacity (Go)": disk_capacity_gb,
            }      

    # Calculate the VM storage cost
    vm_storage_cost = disk_capacity_gb * datastore_cost_per_gb
    # Get the VM state
    vm_power_state = vm_object.summary.runtime.powerState

    return {
        "name": vm_object.name,
        "storage_cost": vm_storage_cost,
        "allocated_storage_size_gb" : total_disk_capacity_gb,
        "allocated_cpu_mhz": vm_object.summary.config.numCpu,
        "allocated_memory_gb": vm_object.summary.config.memorySizeMB / 1024,
        "power_state": vm_power_state
    }

def calculate_total_storage_cost(vm_storage_costs):
    total_cost = sum(vm_info["storage_cost"] for vm_info in vm_storage_costs)
    return total_cost

def calculate_total_storage_size(vm_storage_costs):
    total_size_gb = sum(vm_info["allocated_storage_size_gb"] for vm_info in vm_storage_costs)
    return total_size_gb

def main():
    all_vm_storage_info = []

    for vcenter_info in vcenter_hosts:
        si = SmartConnect(
            host=vcenter_info["host"],
            user=vcenter_info["user"],
            pwd=vcenter_info["password"],
            sslContext=ssl._create_unverified_context()
        )

        if not si:
            print(f"Connexion failed to {vcenter_info['host']}.")
            continue

        # Get the name vcenter_info
        host_name = vcenter_info["host"]
        host_name_lower = host_name.lower()

        if "vmware-1" in host_name_lower:
            vcenter_info["datastore_cost_per_gb"] = datastore_cost_per_gb_vmware1
            vcenter_info["datastore_cost"] = datastore_cost_vmware1
            vcenter_info["host_cost"] = host_cost_vmware1
            vcenter_info["datastore_capacity"] = datastore_capacity_vmware1
        elif "vmware-2" in host_name_lower:
            vcenter_info["datastore_cost_per_gb"] = datastore_cost_per_gb_vmware2
            vcenter_info["host_cost"] = host_cost_vmware2
            vcenter_info["datastore_cost"] = datastore_cost_vmware2
            vcenter_info["datastore_capacity"] = datastore_capacity_vmware2
        else:
            vcenter_info["datastore_cost_per_gb"] = 0

        print(f"\n{vcenter_info['host']}...")

        # Get the host and VMs views
        content = si.RetrieveContent()
        vm_container = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.VirtualMachine], True
        )
        host_container = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.HostSystem], True
        )

        vm_storage_costs = []
        
        # Calculate the cost per VM
        num_vms = len(vm_container.view)
        host_cost_per_vm = vcenter_info["host_cost"] / num_vms

        for vm_object in vm_container.view:
            vm_storage_info = calculate_vm_storage_cost(vm_object, vcenter_info["datastore_cost_per_gb"])
            # Add host cost per VM to total cost
            vm_storage_info["vcenter_host"] = host_name_lower
            vm_storage_info["host_cost"] = host_cost_per_vm
            vm_storage_info["vm_total_cost"] = vm_storage_info["storage_cost"] + host_cost_per_vm
            vm_storage_info["vm_total_cost_per_year"] = vm_storage_info["vm_total_cost"] * 12
            vm_storage_info["storage_cost"] = vm_storage_info["storage_cost"]
            vm_storage_info["allocated_storage_size_gb"] = vm_storage_info["allocated_storage_size_gb"]
            vm_storage_costs.append(vm_storage_info)

        all_vm_storage_info.extend(vm_storage_costs)

        # Cost
        print("\tCost")
        total_cost = vcenter_info["datastore_cost"] + vcenter_info["host_cost"]
        print(f"\t\tDatastore cost : {vcenter_info['datastore_cost']} euros")
        print(f"\t\tHost cost : {vcenter_info['host_cost']} euros")
        print(f"\t\tTotal cost : {total_cost} euros")

        # Calculate the total storage cost
        total_storage_cost = calculate_total_storage_cost(vm_storage_costs)

        # Print the datastore capacity
        print(f"\tTotal datastore capacity : {vcenter_info['datastore_capacity']} Go")
        
    # CSV Export
    current_datetime = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    csv_file_path = f"{current_datetime}_vm_storage_info_cost.csv"
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as csv_file:
        fieldnames = [
            "vcenter_host", "name", "allocated_cpu_mhz", "allocated_memory_gb",
            "allocated_storage_size_gb", "storage_cost", "host_cost", "vm_total_cost", "vm_total_cost_per_year", "power_state"
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for vm_info in all_vm_storage_info:
            writer.writerow(vm_info)

    print(f"\nCSV : {csv_file_path}")

    # Deconnexion
    vm_container.Destroy()
    host_container.Destroy()
    Disconnect(si)

if __name__ == "__main__":
    main()