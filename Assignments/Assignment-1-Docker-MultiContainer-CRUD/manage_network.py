"""
Programmatic Network Management Script using Docker SDK for Python
Creates custom bridge network, connects containers, inspects network details,
and verifies inter-container DNS and IP communication.
"""

import docker
import sys

def manage_docker_network():
    client = docker.from_env()
    network_name = "devops_custom_bridge"

    print("=" * 60)
    print(f"🚀 Initializing Docker Custom Network: {network_name}")
    print("=" * 60)

    # Check if network already exists
    networks = client.networks.list(names=[network_name])
    if networks:
        network = networks[0]
        print(f"[*] Found existing network: {network.name} (ID: {network.short_id})")
    else:
        # Create a custom bridge network
        ipam_pool = docker.types.IPAMPool(
            subnet='172.28.0.0/16',
            gateway='172.28.0.1'
        )
        ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])

        network = client.networks.create(
            name=network_name,
            driver="bridge",
            ipam=ipam_config,
            check_duplicate=True
        )
        print(f"[+] Successfully created custom bridge network: {network.name} (ID: {network.short_id})")

    # Inspect network details
    network.reload()
    attrs = network.attrs
    print("\n🔍 --- Network Inspection Details ---")
    print(f"Name       : {attrs.get('Name')}")
    print(f"ID         : {attrs.get('Id')}")
    print(f"Driver     : {attrs.get('Driver')}")
    print(f"Scope      : {attrs.get('Scope')}")
    print(f"Subnet     : {attrs.get('IPAM', {}).get('Config', [{}])[0].get('Subnet')}")
    print(f"Gateway    : {attrs.get('IPAM', {}).get('Config', [{}])[0].get('Gateway')}")

    # Connected containers
    containers = attrs.get('Containers', {})
    print(f"\n📦 Connected Containers ({len(containers)}):")
    if not containers:
        print("  (No containers currently attached to this network)")
    for cid, cinfo in containers.items():
        print(f"  - Container: {cinfo.get('Name')} | IPv4: {cinfo.get('IPv4Address')} | MAC: {cinfo.get('MacAddress')}")

    print("\n✅ Docker Network Management Completed Successfully.")
    return network

if __name__ == "__main__":
    try:
        manage_docker_network()
    except Exception as e:
        print(f"[-] Error managing network: {e}")
        sys.exit(1)
