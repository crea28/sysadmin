from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl
import sys

vcenter_host = ""
vcenter_user = ""
vcenter_password = ""

def modify_vm(vm_name, num_cpu, memory_mb):
    si = SmartConnect(
        host=vcenter_host,
        user=vcenter_user,
        pwd=vcenter_password,
        port=443,
        sslContext=None
    )

    vm = None
    content = si.RetrieveContent()
    for vm_obj in content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True).view:
        if vm_obj.name == vm_name:
            vm = vm_obj
            break

    if not vm:
        print(f"VM '{vm_name}' doesn't exist.")
        Disconnect(si)
        return

    # Crate a specific configuration
    vm_config_spec = vim.vm.ConfigSpec()
    vm_config_spec.numCPUs = num_cpu
    vm_config_spec.memoryMB = memory_mb

    # Update configuration
    task = vm.ReconfigVM_Task(vm_config_spec)
    print(f"Update '{vm_name}' in progress...")

    while task.info.state == vim.TaskInfo.State.running:
        continue

    if task.info.state == vim.TaskInfo.State.success:
        print("VM updated")
    else:
        print("Error in update process")

    Disconnect(si)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage python updateVM.py <vm_name> <CPU_number> <MB_RAM_number>")
        sys.exit(1)

    vm_name = sys.argv[1]
    num_cpu = int(sys.argv[2])
    memory_mb = int(sys.argv[3])

    modify_vm(vm_name, num_cpu, memory_mb)
