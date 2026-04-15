#!/usr/bin/env python3
# Version 1.1
# listSnapshots.py

import requests
import json
from urllib.parse import urljoin
import urllib3
from datetime import datetime
import argparse

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
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Erreur d'authentification: {e}")
            return False
    
    def get_nodes(self):
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
        try:
            vms_url = urljoin(self.base_url + "/", f"nodes/{node}/qemu")
            response = self.session.get(vms_url)
            response.raise_for_status()
            
            vms_data = response.json()
            return vms_data['data']
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Erreur lors de la récupération des VMs du nœud {node}: {e}")
            return []
    
    def get_vm_snapshots(self, node, vmid):
        try:
            snapshots_url = urljoin(self.base_url + "/", f"nodes/{node}/qemu/{vmid}/snapshot")
            response = self.session.get(snapshots_url)
            response.raise_for_status()
            
            snapshots_data = response.json()
            # Filtrer pour exclure le snapshot 'current' qui n'est pas un vrai snapshot
            return [snap for snap in snapshots_data['data'] if snap['name'] != 'current']
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Erreur lors de la récupération des snapshots VM {vmid}: {e}")
            return []
    
    def get_snapshot_details(self, node, vmid, snapshot_name):
        try:
            snapshot_url = urljoin(self.base_url + "/", f"nodes/{node}/qemu/{vmid}/snapshot/{snapshot_name}/config")
            response = self.session.get(snapshot_url)
            response.raise_for_status()
            
            return response.json()['data']
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Erreur lors de la récupération des détails du snapshot {snapshot_name}: {e}")
            return {}
    
    def list_all_snapshots(self, vm_filter=None):
        if not self.authenticate():
            return []
        
        nodes = self.get_nodes()
        if not nodes:
            print("✗ Aucun nœud trouvé dans le cluster")
            return []
        
        all_snapshots = []
        
        for node in nodes:
            vms = self.get_vms_on_node(node)
            
            for vm in vms:
                vmid = vm['vmid']
                vm_name = vm.get('name', f'VM-{vmid}')
                
                # Filtrer par VM si spécifié
                if vm_filter and str(vmid) != str(vm_filter) and vm_name.lower() != vm_filter.lower():
                    continue
                
                snapshots = self.get_vm_snapshots(node, vmid)
                
                for snapshot in snapshots:
                    snapshot_info = {
                        'node': node,
                        'vmid': vmid,
                        'vm_name': vm_name,
                        'snapshot_name': snapshot['name'],
                        'description': snapshot.get('description', 'Pas de description'),
                        'snaptime': snapshot.get('snaptime', 0),
                        'parent': snapshot.get('parent', ''),
                        'vmstate': snapshot.get('vmstate', 0)
                    }
                                        
                    all_snapshots.append(snapshot_info)
        
        return all_snapshots
    
    def display_snapshots(self, snapshots):
        if not snapshots:
            print("\n❌ Aucun snapshot trouvé dans le cluster")
            return
        
        print(f"\n{len(snapshots)} snapshot(s) found")
        print("=" * 120)
        
        # En-tête du tableau unique
        print(f"{'Node':<20} {'VM':<20} {'Snapshot':<20} {'Date de création':<20} {'Description':<40}")
        print("-" * 120)
        
        # Trier tous les snapshots par nœud, puis par VM, puis par date
        sorted_snapshots = sorted(snapshots, key=lambda x: (x['node'], x['vm_name'], x['snaptime'] if x['snaptime'] else 0), reverse=False)
        
        for snap in sorted_snapshots:
            node = snap['node'][:11]
            vm_name = snap['vm_name'][:19]
            snap_name = snap['snapshot_name'][:19]
            
            # Convertir timestamp en date lisible
            if snap['snaptime']:
                snap_date = datetime.fromtimestamp(snap['snaptime']).strftime('%Y-%m-%d %H:%M')
            else:
                snap_date = 'Date inconnue'
            
            description = snap['description'][:39] if snap['description'] != 'Pas de description' else '-'
            
            print(f"{node:<20} {vm_name:<20} {snap_name:<20} {snap_date:<20} {description:<40}")
        
        print()
    
    def display_snapshots_summary(self, snapshots):
        if not snapshots:
            return
        
        # Statistiques générales
        total_snapshots = len(snapshots)
        vms_with_snapshots = len(set(snap['vmid'] for snap in snapshots))
        snapshots_with_ram = len([snap for snap in snapshots if snap['vmstate']])
        
        # Snapshots les plus récents et plus anciens
        sorted_snaps = sorted(snapshots, key=lambda x: x['snaptime'] if x['snaptime'] else 0)
        oldest_snap = sorted_snaps[0] if sorted_snaps and sorted_snaps[0]['snaptime'] else None
        newest_snap = sorted_snaps[-1] if sorted_snaps and sorted_snaps[-1]['snaptime'] else None
        
        print(f"\n RÉSUMÉ DES SNAPSHOTS")
        print("=" * 50)
        print(f"Total des snapshots: {total_snapshots}")
        print(f"VMs avec snapshots: {vms_with_snapshots}")
        print(f"Snapshots avec RAM: {snapshots_with_ram}")
        
        if oldest_snap and oldest_snap['snaptime']:
            oldest_date = datetime.fromtimestamp(oldest_snap['snaptime']).strftime('%Y-%m-%d %H:%M')
            print(f"Plus ancien: {oldest_snap['snapshot_name']} ({oldest_date})")
        
        if newest_snap and newest_snap['snaptime']:
            newest_date = datetime.fromtimestamp(newest_snap['snaptime']).strftime('%Y-%m-%d %H:%M')
            print(f"Plus récent: {newest_snap['snapshot_name']} ({newest_date})")

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description='Lister les snapshots des VMs Proxmox')
    parser.add_argument('--vm', help='Filtrer par VMID ou nom de VM spécifique')
    parser.add_argument('--summary', action='store_true', help='Afficher uniquement le résumé')
    
    args = parser.parse_args()
    
    print("Script de listage des snapshots Proxmox")
    print("=" * 45)
    
    # Configuration
    PROXMOX_HOST = ""
    PROXMOX_USER = ""
    PROXMOX_PASSWORD = ""
    
    # Créer l'instance API et lister les snapshots
    api = ProxmoxAPI(PROXMOX_HOST, PROXMOX_USER, PROXMOX_PASSWORD)
    snapshots = api.list_all_snapshots(vm_filter=args.vm)
    
    if args.summary:
        api.display_snapshots_summary(snapshots)
    else:
        api.display_snapshots(snapshots)
        api.display_snapshots_summary(snapshots)

if __name__ == "__main__":
    main()
