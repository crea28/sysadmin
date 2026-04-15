#!/usr/bin/env python3
# Version 1.1
# listVMs.py

import requests
import json
from urllib.parse import urljoin
import urllib3

# Désactiver les avertissements SSL si nécessaire (pour les certificats auto-signés)
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
        """Authentification et récupération du ticket/token"""
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
            
            # Configurer les headers pour les futures requêtes
            self.session.cookies.set('PVEAuthCookie', self.ticket)
            self.session.headers.update({'CSRFPreventionToken': self.token})
            
            #print(f"✓ Authentification réussie pour {self.user}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Erreur d'authentification: {e}")
            return False
    
    def get_nodes(self):
        """Récupère la liste des nœuds du cluster"""
        try:
            nodes_url = urljoin(self.base_url + "/", "nodes")
            response = self.session.get(nodes_url)
            response.raise_for_status()
            
            nodes_data = response.json()
            return [node['node'] for node in nodes_data['data']]
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Erreur lors de la récupération des nœuds: {e}")
            return []
    
    def get_vms_on_node(self, node):
        """Récupère les VMs d'un nœud spécifique"""
        try:
            vms_url = urljoin(self.base_url + "/", f"nodes/{node}/qemu")
            response = self.session.get(vms_url)
            response.raise_for_status()
            
            vms_data = response.json()
            return vms_data['data']
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Erreur lors de la récupération des VMs du nœud {node}: {e}")
            return []
    
    def list_all_vms(self):
        """Liste toutes les VMs du cluster"""
        if not self.authenticate():
            return []
        
        nodes = self.get_nodes()
        if not nodes:
            print("✗ Aucun nœud trouvé dans le cluster")
            return []
        
        all_vms = []
        
        for node in nodes:
            vms = self.get_vms_on_node(node)
            
            for vm in vms:
                vm['node'] = node
                all_vms.append(vm)
        
        return all_vms
    
    def display_vms(self, vms):
        if not vms:
            print("\n❌ Aucune VM trouvée dans le cluster")
            return
        
        print(f"\n {len(vms)} VM(s) found")
        print("=" * 90)
        
        # En-tête du tableau
        print(f"{'ID':<6} {'Name':<30} {'Node':<15} {'Status':<15} {'CPU':<6} {'Memory':<10}")
        print("-" * 90)
        
        for vm in sorted(vms, key=lambda x: x['vmid']):
            vmid = vm.get('vmid', 'N/A')
            name = vm.get('name', 'N/A')[:25]
            node = vm.get('node', 'N/A')
            status = vm.get('status', 'N/A')
            cpus = vm.get('cpus', 'N/A')
            memory = vm.get('maxmem', 0)
            
            # Convertir la mémoire en GB si elle existe
            if isinstance(memory, int) and memory > 0:
                memory_gb = f"{memory / (1024**3):.1f}GB"
            else:
                memory_gb = "N/A"
            
            # Colorer le statut
            status_display = status
            if status == 'running':
                status_display = f"🟢 {status}"
            elif status == 'stopped':
                status_display = f"🔴 {status}"
            else:
                status_display = f"🟡 {status}"
            
            print(f"{vmid:<6} {name:<30} {node:<15} {status_display:<15} {cpus:<6} {memory_gb:<10}")

def main():  
    # Credentials
    PROXMOX_HOST = ""
    PROXMOX_USER = ""
    PROXMOX_PASSWORD = ""
    
    # Create instance and VMs listing
    api = ProxmoxAPI(PROXMOX_HOST, PROXMOX_USER, PROXMOX_PASSWORD)
    vms = api.list_all_vms()
    api.display_vms(vms)

if __name__ == "__main__":
    main()
