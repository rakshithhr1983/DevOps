"""
TreasureBook Traffic Simulator & Load Generator
Simulates concurrent adventurers interacting with the graph platform:
- Creating Nodes (Treasures, Locations, Maps)
- Establishing Edges (Trails, Hidden-At, Leads-to)
- Querying the TAO Social Graph
- Triggering CPU load to observe Kubernetes Horizontal Pod Autoscaler (HPA) scaling
"""

import requests
import concurrent.futures
import time
import random
import sys

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"

TREASURES = ["Golden Crown", "Cursed Diamond", "Emerald Scepter", "Pirate Chest", "Ruby of Doom", "Ancient Chalice"]
LOCATIONS = ["Cave of Wonders", "Forest of Secrets", "Mystic Lake", "Dragon Peak", "Lost Atlantis", "Shadow Ruins"]
MAPS = ["Mystic Map", "Parchment of Elders", "Sunken Compass Chart", "Starfall Cartograph"]

stats = {
    "total_requests": 0,
    "success": 0,
    "errors": 0,
    "latencies": []
}

def seed_initial_graph():
    print(f"[*] Seeding initial graph data into {BASE_URL}...")
    try:
        # Create Nodes
        n1 = requests.post(f"{BASE_URL}/node", json={"Type": "Treasures", "name": "Golden Crown", "details": "Encrusted with rubies"}).json()
        n2 = requests.post(f"{BASE_URL}/node", json={"Type": "Location", "name": "Cave of Wonders", "details": "Deep inside the desert dunes"}).json()
        n3 = requests.post(f"{BASE_URL}/node", json={"Type": "Map", "name": "Mystic Map", "details": "Glowing ancient ink"}).json()
        n4 = requests.post(f"{BASE_URL}/node", json={"Type": "Location", "name": "Forest of Secrets", "details": "Misty enchanted woods"}).json()
        n5 = requests.post(f"{BASE_URL}/node", json={"Type": "Location", "name": "Mystic Lake", "details": "Crystal clear enchanted waters"}).json()
        n6 = requests.post(f"{BASE_URL}/node", json={"Type": "Treasures", "name": "Cursed Diamond", "details": "Brings peril to who touches it"}).json()

        # Create Edges
        requests.post(f"{BASE_URL}/edge", json={"Type": "Hidden-At", "from_node": "Golden Crown", "to_node": "Cave of Wonders"})
        requests.post(f"{BASE_URL}/edge", json={"Type": "Trail", "from_node": "Forest of Secrets", "to_node": "Mystic Lake"})
        requests.post(f"{BASE_URL}/edge", json={"Type": "Leads-to", "from_node": "Mystic Map", "to_node": "Cursed Diamond"})

        print("[+] Seeded TAO Social Graph successfully.")
    except Exception as e:
        print(f"[-] Note during seed: {e}")

def simulate_adventurer(worker_id, duration_seconds=30):
    start_time = time.time()
    while time.time() - start_time < duration_seconds:
        action = random.choice(["create_node", "create_edge", "query_graph", "burn_cpu"])
        t0 = time.time()
        try:
            if action == "create_node":
                ntype = random.choice(["Treasures", "Location", "Map"])
                name = f"{random.choice(TREASURES if ntype=='Treasures' else (LOCATIONS if ntype=='Location' else MAPS))} #{random.randint(100, 999)}"
                resp = requests.post(f"{BASE_URL}/node", json={"Type": ntype, "name": name, "details": "Simulated exploration discovery"}, timeout=5)
            elif action == "create_edge":
                etype = random.choice(["Trail", "Hidden-At", "Leads-to"])
                from_n = random.choice(LOCATIONS if etype=="Trail" else (TREASURES if etype=="Hidden-At" else MAPS))
                to_n = random.choice(LOCATIONS if etype in ["Trail", "Hidden-At"] else TREASURES)
                resp = requests.post(f"{BASE_URL}/edge", json={"Type": etype, "from_node": from_n, "to_node": to_n}, timeout=5)
            elif action == "query_graph":
                resp = requests.get(f"{BASE_URL}/graph", timeout=5)
            else:
                resp = requests.get(f"{BASE_URL}/cpu-burn?iterations=150000", timeout=5)

            lat = (time.time() - t0) * 1000
            stats["total_requests"] += 1
            stats["latencies"].append(lat)
            if resp.status_code in [200, 201]:
                stats["success"] += 1
            else:
                stats["errors"] += 1
        except Exception:
            stats["total_requests"] += 1
            stats["errors"] += 1

def run_traffic_simulation(concurrency=15, duration=30):
    print("=" * 65)
    print(f"⚔️  TreasureBook Traffic Simulation Starting")
    print(f"Target URL   : {BASE_URL}")
    print(f"Concurrency  : {concurrency} virtual adventurers")
    print(f"Duration     : {duration} seconds")
    print("=" * 65)

    seed_initial_graph()

    print(f"\n🚀 Launching {concurrency} concurrent adventurer threads...")
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(simulate_adventurer, i, duration) for i in range(concurrency)]
        concurrent.futures.wait(futures)

    total_time = time.time() - start_time
    avg_latency = sum(stats["latencies"]) / len(stats["latencies"]) if stats["latencies"] else 0
    rps = stats["total_requests"] / total_time if total_time > 0 else 0

    print("\n" + "=" * 65)
    print("📊 Traffic Simulation Results")
    print("=" * 65)
    print(f"Total Requests Processed : {stats['total_requests']}")
    print(f"Successful Requests (2xx): {stats['success']}")
    print(f"Failed Requests          : {stats['errors']}")
    print(f"Total Duration           : {total_time:.2f} seconds")
    print(f"Throughput (Requests/sec): {rps:.2f} req/s")
    print(f"Average Response Latency : {avg_latency:.2f} ms")
    if stats["latencies"]:
        sorted_lat = sorted(stats["latencies"])
        p95 = sorted_lat[int(len(sorted_lat) * 0.95)]
        p99 = sorted_lat[int(len(sorted_lat) * 0.99)]
        print(f"P95 Latency              : {p95:.2f} ms")
        print(f"P99 Latency              : {p99:.2f} ms")
    print("=" * 65)
    print("Tip: Run 'kubectl get hpa treasurebook-api-hpa --watch' to observe pod scaling!")

if __name__ == "__main__":
    run_traffic_simulation()
