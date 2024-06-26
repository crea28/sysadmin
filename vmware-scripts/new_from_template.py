# new_from_template.py

import sys
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect

# VMWare settings
vcenter_host = ""
vcenter_user = ""
vcenter_password = ""

def clone_vm_from_template(template_name, new_vm_name):
    si = SmartConnect(
        host=vcenter_host,
        user=vcenter_user,
        pwd=vcenter_password,
        port=443,
        sslContext=None
    )

    # Get the view
    content = si.RetrieveContent()
    container = content.rootFolder
    view_type = [vim.VirtualMachine]
    recursive = True
    template_view = content.viewManager.CreateContainerView(container, view_type, recursive)
    template_vm = None

    for vm in template_view.view:
        if vm.name == template_name:
            template_vm = vm
            break

    if not template_vm:
        print(f"template '{template_name}' doesn't exist")
        sys.exit(1)

    
    relocation_spec = vim.vm.RelocateSpec()

    clone_spec = vim.vm.CloneSpec()
    clone_spec.location = relocation_spec
    clone_spec.powerOn = False
    clone_spec.template = False

    # Clone processing
    task = template_vm.Clone(folder=template_vm.parent, name=new_vm_name, spec=clone_spec)

    # Wait end of clone
    while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
            continue

    if task.info.state == vim.TaskInfo.State.success:
        print(f"VM '{new_vm_name}' created with success.")
    else:
        print(f"Error in creating VM '{new_vm_name}': {task.info.error}")

    # Exit
    Disconnect(si)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage : python new_from_template.py <template_name> <new_vm_name>")
        sys.exit(1)

    template_name = sys.argv[1]
    new_vm_name = sys.argv[2]

    clone_vm_from_template(template_name, new_vm_name)
