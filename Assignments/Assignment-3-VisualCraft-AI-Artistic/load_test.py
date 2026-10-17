"""
VisualCraft API Load Generator
Sends concurrent style transfer requests to populate Prometheus metrics and Grafana panels.
"""

import requests
import time
import os
import sys

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5001"
TEST_IMG = os.path.join(os.path.dirname(__file__), "test.jpg")

def run_load_generator(iterations=25, delay=0.5):
    print("=" * 60)
    print(f"🚀 VisualCraft API Load Generator")
    print(f"Target URL : {BASE_URL}")
    print(f"Requests   : {iterations}")
    print("=" * 60)

    if not os.path.exists(TEST_IMG):
        print(f"[-] Error: Test image '{TEST_IMG}' not found.")
        return

    success_count = 0
    error_count = 0

    for i in range(1, iterations + 1):
        print(f"[{i}/{iterations}] Sending POST /styleTransfer request...", end=" ")
        t0 = time.time()
        try:
            with open(TEST_IMG, "rb") as f:
                res = requests.post(f"{BASE_URL}/styleTransfer", files={"image": f}, timeout=10)
            latency = (time.time() - t0) * 1000

            if res.status_code == 200:
                print(f"✅ 200 OK ({latency:.1f} ms)")
                success_count += 1
            else:
                print(f"⚠️ Status {res.status_code} ({latency:.1f} ms)")
                error_count += 1
        except Exception as e:
            print(f"❌ Error: {e}")
            error_count += 1

        # Occasionally send bad request to populate 400 status panel
        if i % 5 == 0:
            try:
                requests.post(f"{BASE_URL}/styleTransfer", timeout=3) # Missing image
            except Exception:
                pass

        time.sleep(delay)

    print("\n" + "=" * 60)
    print(f"Finished: {success_count} successful, {error_count} failed")
    print("View metrics in Grafana at http://localhost:3000")
    print("=" * 60)

if __name__ == "__main__":
    run_load_generator()
