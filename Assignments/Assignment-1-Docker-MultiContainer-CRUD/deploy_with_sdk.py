"""
End-to-End Deployment Script using Docker SDK for Python
Creates custom bridge network, spins up MongoDB with persistent volume,
builds Flask app image, and starts container attached to the custom network.
"""

import docker
import os
import sys

def deploy():
    client = docker.from_env()
    print("🚀 Starting Automated Docker Deployment with Python SDK...")

    # 1. Custom Network
    net_name = "devops_bridge_net"
    try:
        network = client.networks.get(net_name)
        print(f"[*] Network '{net_name}' already exists.")
    except docker.errors.NotFound:
        network = client.networks.create(net_name, driver="bridge")
        print(f"[+] Created custom network '{net_name}'.")

    # 2. Volume
    vol_name = "devops_mongo_data"
    try:
        volume = client.volumes.get(vol_name)
        print(f"[*] Volume '{vol_name}' already exists.")
    except docker.errors.NotFound:
        volume = client.volumes.create(vol_name)
        print(f"[+] Created volume '{vol_name}'.")

    # 3. MongoDB Container
    db_container_name = "devops-mongo-db"
    try:
        old_db = client.containers.get(db_container_name)
        print(f"[*] Stopping and removing existing DB container...")
        old_db.stop()
        old_db.remove()
    except docker.errors.NotFound:
        pass

    print("[+] Launching MongoDB container...")
    db_container = client.containers.run(
        image="mongo:6.0",
        name=db_container_name,
        network=net_name,
        volumes={vol_name: {"bind": "/data/db", "mode": "rw"}},
        ports={"27017/tcp": 27017},
        detach=True,
        restart_policy={"Name": "always"}
    )
    print(f"[+] MongoDB running: {db_container.short_id}")

    # 4. Build Flask App Image
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"[+] Building Flask Docker image from {current_dir}...")
    image, build_logs = client.images.build(path=current_dir, tag="devops-crud-flask:latest", rm=True)
    print(f"[+] Built image: {image.tags}")

    # 5. Run Flask Container
    app_container_name = "devops-crud-app"
    try:
        old_app = client.containers.get(app_container_name)
        print(f"[*] Stopping and removing existing App container...")
        old_app.stop()
        old_app.remove()
    except docker.errors.NotFound:
        pass

    print("[+] Launching Flask Application container...")
    app_container = client.containers.run(
        image="devops-crud-flask:latest",
        name=app_container_name,
        network=net_name,
        environment={"MONGO_URI": f"mongodb://{db_container_name}:27017/devops_crud"},
        ports={"5000/tcp": 5000},
        detach=True,
        restart_policy={"Name": "always"}
    )
    print(f"[+] Flask App running: {app_container.short_id} on http://localhost:5000")
    print("🎉 Deployment completed successfully!")

if __name__ == "__main__":
    deploy()
