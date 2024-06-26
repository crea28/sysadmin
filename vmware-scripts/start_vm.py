# start_vm.py

import sys
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect

# VMWare settings
vcenter_host = ""
vcenter_user = ""
vcenter_password = ""

def get_vm_by_name(si, vm_name):
    content = si.RetrieveContent()
    vm_container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)

    for vm in vm_container.view:
        if vm.name == vm_name:
            return vm

    return None

def main():
    # VM Name in args
    vm_name = sys.argv[1]

    try:
        # Connection
        si = SmartConnect(
            host=vcenter_host,
            user=vcenter_user,
            pwd=vcenter_password,
            port=443,
            sslContext=None
        )
        if not si:
            raise SystemExit("vCenter Connection problem.")

        # Get the VM Name
        vm = get_vm_by_name(si, vm_name)
        if not vm:
            print(f"VM '{vm_name}' doesn't exist.")
            return

        # Check VM State
        if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOff:
            print(f"VM '{vm_name}' stopped and will be up into few minutes")
            task = vm.PowerOn()
            task_info = task.info
            if task_info.state == vim.TaskInfo.State.success:
                print(f"VM '{vm_name}' is UP.")
        elif vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
            print(f"VM '{vm_name}' already UP.")
        else:
            print(f"VM '{vm_name}' unknown state.")

    except Exception as e:
        print(f"Error: {str(e)}")

    finally:
        Disconnect(si)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python start_vm.py vm_name")
        sys.exit(1)
    main()