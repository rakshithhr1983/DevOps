"""
TreasureBook Graph API
Inspired by Facebook TAO (The Associations and Objects) Social Graph Architecture.
Manages Objects (Nodes: Treasures, Locations, Maps) and Associations (Edges: Trail, Hidden-At, Leads-to).
"""

from flask import Flask, request, jsonify, render_template_string
import os
import pymongo
from bson import ObjectId
import math

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/treasurebook")
client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client.get_database()
nodes_col = db["nodes"]
edges_col = db["edges"]

def format_doc(doc):
    if not doc:
        return None
    doc["id"] = str(doc.pop("_id"))
    return doc

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>TreasureBook - Social Graph Platform</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 950px; margin: 30px auto; padding: 20px; background: #0b1120; color: #e2e8f0; }
        h1 { color: #f59e0b; font-size: 28px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .card { background: #1e293b; padding: 20px; border-radius: 8px; border: 1px solid #334155; }
        input, select, textarea, button { width: 100%; box-sizing: border-box; padding: 10px; margin: 8px 0; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: white; }
        button { background: #f59e0b; color: #0f172a; font-weight: bold; cursor: pointer; border: none; }
        button:hover { background: #d97706; }
        .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; background: #334155; }
        .tag-treasure { background: #f59e0b; color: #000; }
        .tag-location { background: #10b981; color: #000; }
        .tag-map { background: #3b82f6; color: #fff; }
        pre { background: #0f172a; padding: 12px; border-radius: 6px; overflow-x: auto; color: #38bdf8; font-size: 13px; }
    </style>
</head>
<body>
    <h1>🗺️ TreasureBook: Graph-Based Adventure Platform</h1>
    <p>Inspired by Facebook TAO - Connecting Treasures, Locations, Maps, and Trails.</p>

    <div class="grid">
        <div class="card">
            <h3>Add Graph Node (Object)</h3>
            <select id="node-type">
                <option value="Treasures">Type: Treasure (e.g., Golden Crown)</option>
                <option value="Location">Type: Location (e.g., Cave of Wonders)</option>
                <option value="Map">Type: Map (e.g., Mystic Map)</option>
            </select>
            <input type="text" id="node-name" placeholder="Name (e.g. Golden Crown)">
            <input type="text" id="node-desc" placeholder="Details / Clues">
            <button onclick="createNode()">Create Node</button>
        </div>

        <div class="card">
            <h3>Add Graph Edge (Association)</h3>
            <select id="edge-type">
                <option value="Trail">Type: Trail (connects two Locations)</option>
                <option value="Hidden-At">Type: Hidden-At (maps Treasure to Location)</option>
                <option value="Leads-to">Type: Leads-to (links Map to Treasure)</option>
            </select>
            <input type="text" id="from-id" placeholder="From Node ID or Name">
            <input type="text" id="to-id" placeholder="To Node ID or Name">
            <button onclick="createEdge()">Create Edge</button>
        </div>
    </div>

    <div class="card" style="margin-top: 20px;">
        <h3>Graph State (Live TAO Graph)</h3>
        <button onclick="loadGraph()" style="width: auto; padding: 6px 14px; background: #3b82f6; color: white;">Refresh Graph</button>
        <pre id="graph-data">Loading graph...</pre>
    </div>

    <script>
        async function createNode() {
            const type = document.getElementById('node-type').value;
            const name = document.getElementById('node-name').value;
            const details = document.getElementById('node-desc').value;
            if (!name) return alert('Name is required');
            await fetch('/node', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ Type: type, name, details })
            });
            document.getElementById('node-name').value = '';
            document.getElementById('node-desc').value = '';
            loadGraph();
        }

        async function createEdge() {
            const type = document.getElementById('edge-type').value;
            const from_node = document.getElementById('from-id').value;
            const to_node = document.getElementById('to-id').value;
            if (!from_node || !to_node) return alert('Both From and To nodes are required');
            await fetch('/edge', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ Type: type, from_node, to_node })
            });
            document.getElementById('from-id').value = '';
            document.getElementById('to-id').value = '';
            loadGraph();
        }

        async function loadGraph() {
            const res = await fetch('/graph');
            const data = await res.json();
            document.getElementById('graph-data').textContent = JSON.stringify(data, null, 2);
        }

        loadGraph();
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(DASHBOARD_HTML)

@app.route("/health", methods=["GET"])
def health():
    try:
        client.admin.command('ping')
        return jsonify({"status": "healthy", "service": "TreasureBook Graph API", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 503

# ----------------- NODE (Object) ENDPOINTS -----------------

@app.route("/node", methods=["POST"])
def create_node():
    """
    Creates a node in the graph:
    - Type: 'Treasures', 'Location', 'Map'
    - name: e.g., 'Golden Crown', 'Cave of Wonders', 'Mystic Map'
    """
    try:
        data = request.get_json(force=True)
        node_type = data.get("Type")
        name = data.get("name")

        if not node_type or not name:
            return jsonify({"error": "Fields 'Type' and 'name' are required"}), 400

        valid_types = ["Treasures", "Location", "Map"]
        if node_type not in valid_types:
            return jsonify({"error": f"Invalid Type. Must be one of {valid_types}"}), 400

        node_doc = {
            "Type": node_type,
            "name": name,
            "details": data.get("details", "")
        }
        res = nodes_col.insert_one(node_doc)
        node_doc["id"] = str(res.inserted_id)
        node_doc.pop("_id", None)
        return jsonify({"message": "Node created successfully", "node": node_doc}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/nodes", methods=["GET"])
def get_nodes():
    try:
        node_type = request.args.get("Type")
        query = {"Type": node_type} if node_type else {}
        nodes = [format_doc(doc) for doc in nodes_col.find(query)]
        return jsonify({"count": len(nodes), "nodes": nodes}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/node/<node_id>", methods=["GET"])
def get_node(node_id):
    try:
        doc = nodes_col.find_one({"_id": ObjectId(node_id)})
        if not doc:
            return jsonify({"error": "Node not found"}), 404
        return jsonify(format_doc(doc)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------- EDGE (Association) ENDPOINTS -----------------

@app.route("/edge", methods=["POST"])
def create_edge():
    """
    Creates an association between nodes:
    - Type: 'Trail' (e.g. Forest of Secrets -> Mystic Lake)
    - Type: 'Hidden-At' (e.g. Golden Crown -> Cave of Wonders)
    - Type: 'Leads-to' (e.g. Mystic Map -> Cursed Diamond)
    """
    try:
        data = request.get_json(force=True)
        edge_type = data.get("Type")
        from_node = data.get("from_node")
        to_node = data.get("to_node")

        if not edge_type or not from_node or not to_node:
            return jsonify({"error": "Fields 'Type', 'from_node', and 'to_node' are required"}), 400

        valid_edge_types = ["Trail", "Hidden-At", "Leads-to"]
        if edge_type not in valid_edge_types:
            return jsonify({"error": f"Invalid Type. Must be one of {valid_edge_types}"}), 400

        edge_doc = {
            "Type": edge_type,
            "from_node": from_node,
            "to_node": to_node,
            "metadata": data.get("metadata", {})
        }
        res = edges_col.insert_one(edge_doc)
        edge_doc["id"] = str(res.inserted_id)
        edge_doc.pop("_id", None)
        return jsonify({"message": "Edge created successfully", "edge": edge_doc}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/edges", methods=["GET"])
def get_edges():
    try:
        edge_type = request.args.get("Type")
        query = {"Type": edge_type} if edge_type else {}
        edges = [format_doc(doc) for doc in edges_col.find(query)]
        return jsonify({"count": len(edges), "edges": edges}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/graph", methods=["GET"])
def get_graph():
    """Returns the full Social Graph of all Nodes and Edges."""
    try:
        nodes = [format_doc(doc) for doc in nodes_col.find()]
        edges = [format_doc(doc) for doc in edges_col.find()]
        return jsonify({
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "nodes": nodes,
            "edges": edges
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/cpu-burn", methods=["GET"])
def cpu_burn():
    """Simulates CPU load for testing Kubernetes Horizontal Pod Autoscaler (HPA)."""
    iterations = int(request.args.get("iterations", 300000))
    val = 0.0
    for i in range(iterations):
        val += math.sqrt(i) * math.sin(i)
    return jsonify({"status": "load_computed", "iterations": iterations, "result": val}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
