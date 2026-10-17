"""
AI Artistic Style Service
Exposes /styleTransfer endpoint to apply artistic transformations to input images.
Also includes Prometheus metrics exposition at /metrics.
"""

from flask import Flask, request, send_file, jsonify, Response
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import io
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Prometheus Metrics
REQUEST_COUNT = Counter(
    "api_requests_total",
    "Total number of API requests to styleTransfer",
    ["status_code"]
)
REQUEST_LATENCY = Histogram(
    "api_request_duration_seconds",
    "Response latency for styleTransfer endpoint in seconds",
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "VisualCraft AI Artistic Style Service", "version": "1.0.0"}), 200

@app.route("/metrics", methods=["GET"])
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route("/styleTransfer", methods=["POST"])
def style_transfer():
    start_time = time.time()

    if "image" not in request.files:
        REQUEST_COUNT.labels(status_code="400").inc()
        return jsonify({"error": "No image file provided under 'image' form key"}), 400

    file = request.files["image"]
    if file.filename == "":
        REQUEST_COUNT.labels(status_code="400").inc()
        return jsonify({"error": "Empty filename provided"}), 400

    try:
        # Load input image
        img = Image.open(file.stream).convert("RGB")

        # Apply Artistic Style Transformation
        # 1. Edge enhance + Posterize + Color boost
        posterized = ImageOps.posterize(img, 4)
        colored = ImageEnhance.Color(posterized).enhance(1.8)
        contrast = ImageEnhance.Contrast(colored).enhance(1.4)
        stylized = contrast.filter(ImageFilter.EDGE_ENHANCE_MORE)

        # Save to buffer
        output_buffer = io.BytesIO()
        stylized.save(output_buffer, format="JPEG", quality=90)
        output_buffer.seek(0)

        elapsed = time.time() - start_time
        REQUEST_LATENCY.observe(elapsed)
        REQUEST_COUNT.labels(status_code="200").inc()

        return send_file(output_buffer, mimetype="image/jpeg", as_attachment=False, download_name="styled_image.jpg")
    except Exception as e:
        REQUEST_COUNT.labels(status_code="500").inc()
        return jsonify({"error": f"Style transfer failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
