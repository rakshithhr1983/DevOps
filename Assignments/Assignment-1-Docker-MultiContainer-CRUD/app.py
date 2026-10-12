from flask import Flask, request, jsonify, render_template_string
import os
import pymongo
from bson import ObjectId

app = Flask(__name__)

# Connect to MongoDB container
MONGO_URI = os.getenv("MONGO_URI", "mongodb://db:27017/devops_crud")
client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client.get_database()
items_collection = db["items"]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DevOps Multi-Container CRUD</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; background: #0f172a; color: #f8fafc; }
        h1 { color: #38bdf8; border-bottom: 2px solid #334155; padding-bottom: 12px; }
        .card { background: #1e293b; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        input, textarea, button { border-radius: 6px; padding: 10px 14px; font-size: 14px; margin: 6px 0; border: 1px solid #475569; }
        input, textarea { width: 100%; box-sizing: border-box; background: #0f172a; color: #f8fafc; }
        button { background: #0284c7; color: white; cursor: pointer; border: none; font-weight: 600; }
        button:hover { background: #0369a1; }
        .item-row { display: flex; justify-content: space-between; align-items: center; padding: 12px; border-bottom: 1px solid #334155; }
        .badge { background: #0369a1; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
    </style>
</head>
<body>
    <h1>🚀 DevOps Multi-Container CRUD Application</h1>
    <div class="card">
        <h3>Add New Item</h3>
        <input type="text" id="title" placeholder="Item Title">
        <textarea id="desc" placeholder="Item Description"></textarea>
        <button onclick="addItem()">Create Item</button>
    </div>
    <div class="card">
        <h3>Stored Items (MongoDB Persistent Volume)</h3>
        <div id="items-list">Loading...</div>
    </div>

    <script>
        async function fetchItems() {
            const res = await fetch('/api/items');
            const data = await res.json();
            const list = document.getElementById('items-list');
            if (data.length === 0) { list.innerHTML = '<p>No items found. Create one above!</p>'; return; }
            list.innerHTML = data.map(item => `
                <div class="item-row">
                    <div>
                        <strong>${item.title}</strong><br>
                        <small style="color: #94a3b8">${item.description || 'No description'}</small>
                    </div>
                    <div>
                        <button onclick="deleteItem('${item.id}')" style="background:#ef4444;">Delete</button>
                    </div>
                </div>
            `).join('');
        }

        async function addItem() {
            const title = document.getElementById('title').value;
            const description = document.getElementById('desc').value;
            if (!title) return alert('Title is required');
            await fetch('/api/items', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, description })
            });
            document.getElementById('title').value = '';
            document.getElementById('desc').value = '';
            fetchItems();
        }

        async function deleteItem(id) {
            await fetch('/api/items/' + id, { method: 'DELETE' });
            fetchItems();
        }

        fetchItems();
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/health", methods=["GET"])
def health():
    try:
        client.admin.command('ping')
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 503

@app.route("/api/items", methods=["GET"])
def get_items():
    try:
        items = list(items_collection.find())
        result = [{"id": str(i["_id"]), "title": i.get("title"), "description": i.get("description")} for i in items]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/items", methods=["POST"])
def create_item():
    try:
        data = request.get_json(force=True)
        if not data or "title" not in data:
            return jsonify({"error": "Title is required"}), 400
        res = items_collection.insert_one({"title": data["title"], "description": data.get("description", "")})
        return jsonify({"id": str(res.inserted_id), "title": data["title"], "description": data.get("description", "")}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/items/<item_id>", methods=["PUT"])
def update_item(item_id):
    try:
        data = request.get_json(force=True)
        update_fields = {}
        if "title" in data: update_fields["title"] = data["title"]
        if "description" in data: update_fields["description"] = data["description"]
        res = items_collection.update_one({"_id": ObjectId(item_id)}, {"$set": update_fields})
        if res.matched_count == 0:
            return jsonify({"error": "Item not found"}), 404
        return jsonify({"message": "Item updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/items/<item_id>", methods=["DELETE"])
def delete_item(item_id):
    try:
        res = items_collection.delete_one({"_id": ObjectId(item_id)})
        if res.deleted_count == 0:
            return jsonify({"error": "Item not found"}), 404
        return jsonify({"message": "Item deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
