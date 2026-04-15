#!/usr/bin/env python3
# Version 1.1
# createSnapshots.py

import requests
import json
from urllib.parse import urljoin
import urllib3
import argparse
import sys
from datetime import datetime

# Desactivate SSL Warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ProxmoxAPI:
    def __init__(self, host, user, password, verify_ssl=False):
        self.host = host
        self.user = user
        self.password = password
        self.verify_ssl = verify_ssl
        self.base_url = f"https://{host}/api2/json"
        self.session = requests.Session()
        self.session.verify = verify_ssl
        self.ticket = None
        self.token = None
        
    def authenticate(self):
        """ Auth and Get token """
        auth_url = urljoin(self.base_url + "/", "access/ticket")
        auth_data = {
            'username': self.user,
            'password': self.password
        }
        
        try:
            response = self.session.post(auth_url, data=auth_data)
            response.raise_for_status()
            
            auth_result = response.json()
            self.ticket = auth_result['data']['ticket']
            self.token = auth_result['data']['CSRFPreventionToken']
            
            # Set headers
            self.session.cookies.set('PVEAuthCookie', self.ticket)
            self.session.headers.update({'CSRFPreventionToken': self.token})
            
            print(f"Authentication success for {self.user}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Authentication Error: {e}")
            return False
    
    def get_nodes(self):
        """ Get cluster node list """
        try:
            nodes_url = urljoin(self.base_url + "/", "nodes")
            response = self.session.get(nodes_url)
            response.raise_for_status()
            
            nodes_data = response.json()
            return [node['node'] for node in nodes_data['data']]
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur retrieving nodes: {e}")
            return []
    
    def find_vm(self, vm_identifier):
        """ Find a VM with VMID or name """
        nodes = self.get_nodes()
        
        for node in nodes:
            try:
                vms_url = urljoin(self.base_url + "/", f"nodes/{node}/qemu")
                response = self.session.get(vms_url)
                response.raise_for_status()
                
                vms_data = response.json()
                
                for vm in vms_data['data']:
                    # Check by VMID
                    if str(vm['vmid']) == str(vm_identifier):
                        return node, vm['vmid'], vm.get('name', f'VM-{vm["vmid"]}')
                    
                    # Check by Name
                    vm_name = vm.get('name', '')
                    if vm_name.lower() == vm_identifier.lower():
                        return node, vm['vmid'], vm_name
                        
            except requests.exceptions.RequestException as e:
                print(f"Error while searching the node {node}: {e}")
                continue
        
        return None, None, None
    
    def get_vm_status(self, node, vmid):
        """ Get VM status """
        try:
            status_url = urljoin(self.base_url + "/", f"nodes/{node}/qemu/{vmid}/status/current")
            response = self.session.get(status_url)
            response.raise_for_status()
            
            status_data = response.json()
            return status_data['data']
            
        except requests.exceptions.RequestException as e:
            print(f"Error while getting status: {e}")
            return None
    
    def create_snapshot(self, node, vmid, snapshot_name, description=None, include_ram=False):
        """ Create a VM snapshot """
        try:
            snapshot_url = urljoin(self.base_url + "/", f"nodes/{node}/qemu/{vmid}/snapshot")
            
            # Preparing snapshot datas
            snapshot_data = {
                'snapname': snapshot_name,
                'vmstate': '1' if include_ram else '0'
            }
            
            if description:
                snapshot_data['description'] = description
            
            print(f" Snapshot creation : '{snapshot_name}' for VM {vmid}...")
            if include_ram:
                print("Inclusion of RAM status...")
            
            response = self.session.post(snapshot_url, data=snapshot_data)
            response.raise_for_status()
            
            # Get the Task ID (Unique Process ID)
            result = response.json()
            upid = result.get('data')
            
            if upid:
                print(f"Starting task (UPID: {upid})")
                
                # Waiting ending task
                if self.wait_for_task(node, upid):
                    print(f"✅ Snapshot '{snapshot_name}' created with success !")
                    return True
                else:
                    print(f"⚠️ Cannot check the status task")
                    return False
            else:
                print(f"Snapshot '{snapshot_name}' created with success !")
                return True
                
        except requests.exceptions.RequestException as e:
            print(f"Error in creating snapshot: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    if 'errors' in error_detail:
                        for field, error in error_detail['errors'].items():
                            print(f"   {field}: {error}")
                except:
                    print(f"   Error : {e.response.text}")
            return False
    
    def wait_for_task(self, node, upid, timeout=300):
        """ Waiting ending proxmox task """
        import time
        
        try:
            task_url = urljoin(self.base_url + "/", f"nodes/{node}/tasks/{upid}/status")
            start_time = time.time()
            
            print("Waiting ending task...")
            
            while time.time() - start_time < timeout:
                response = self.session.get(task_url)
                response.raise_for_status()
                
                task_data = response.json()['data']
                status = task_data.get('status')
                exitstatus = task_data.get('exitstatus')
                
                # Ending task with success
                if status == 'stopped' and exitstatus == 'OK':
                    return True
                # Ending task with error
                elif status == 'stopped' and exitstatus != 'OK':
                    print(f"Log ending task failed: {exitstatus}")
                    return False
                # Task in progress
                elif status == 'running':
                    print(".", end="", flush=True)
                    time.sleep(2)
                    continue
                else:
                    time.sleep(2)
                    continue
            
            print("\n Timeout during the task")
            return False
            
        except requests.exceptions.RequestException as e:
            print(f"Error while task: {e}")
            return False

def generate_snapshot_name(vm_name, custom_name=None):
    """Generate a snapshot name"""
    if custom_name:
        return custom_name
    
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    return f"snap-{timestamp}"

def main():
    parser = argparse.ArgumentParser(description='Create a snapshot (Proxmox VM)')
    parser.add_argument('vm', help='VMID or name')
    parser.add_argument('--name', help='Snapshot name')
    parser.add_argument('--description', help='Snapshot description')
    parser.add_argument('--include-ram', action='store_true', 
                       help='Add the RAM status')
    parser.add_argument('--force', action='store_true', 
                       help='Create snapshot even if the VM is stopped')
    
    args = parser.parse_args()
    
    print("Creation script for Proxmox")
    print("=" * 45)
    
    # Configuration
    PROXMOX_HOST = ""
    PROXMOX_USER = ""
    PROXMOX_PASSWORD = ""
    
    # Create API instance and auth
    api = ProxmoxAPI(PROXMOX_HOST, PROXMOX_USER, PROXMOX_PASSWORD)
    
    if not api.authenticate():
        sys.exit(1)
    
    # Search VM
    print(f"\n🔍 Searching VM : {args.vm}")
    node, vmid, vm_name = api.find_vm(args.vm)
    
    if not node:
        print(f"VM '{args.vm}' not found")
        sys.exit(1)
    
    print(f"VM found: {vm_name} (ID: {vmid}) on node {node}")
    
    # Check the VM status
    vm_status = api.get_vm_status(node, vmid)
    if vm_status:
        status = vm_status.get('status', 'unknown')
        print(f"VM status: {status}")
        
        if status == 'stopped' and not args.force:
            print("VM stopped")
            confirm = input("Continue ? (y/N): ").strip().lower()
            if confirm != 'y':
                print(" Task canceled")
                sys.exit(0)
        
        if status == 'running' and args.include_ram:
            print("The VM is running—the RAM status will be included")
    
    # Generate snapshot
    snapshot_name = generate_snapshot_name(vm_name, args.name)
    description = args.description or f"Snapshot created : {datetime.now().strftime('%Y-%m-%d à %H:%M:%S')}"
    
    print(f"Snapshot name: {snapshot_name}")
    print(f"Description: {description}")
    
    # Create snapshot
    success = api.create_snapshot(
        node=node,
        vmid=vmid,
        snapshot_name=snapshot_name,
        description=description,
        include_ram=args.include_ram
    )
    
    if success:
        print(f"\n🎉 Snapshot created!")
        print(f"   VM: {vm_name} (ID: {vmid})")
        print(f"   Snapshot: {snapshot_name}")
        print(f"   Node: {node}")
    else:
        print(f"\n❌ Failed to create the snapshot")
        sys.exit(1)

if __name__ == "__main__":
    main()
