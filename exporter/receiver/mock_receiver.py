import os
from flask import Flask, request, jsonify

app = Flask(__name__)
UPLOAD_FOLDER = '/uploads'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/api/upload-graph', methods=['POST'])
def upload_graph():
    if 'application/json' not in request.content_type:
        return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 415

    if not request.data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    file_size = len(request.data)
    print(f"Received file. Content-Type: {request.content_type}, Size: {file_size} bytes")

    try:
        save_path = os.path.join(UPLOAD_FOLDER, 'received_graph.json')
        with open(save_path, 'wb') as f:
            f.write(request.data)
        print(f"Saved received file to {save_path}")
    except IOError as e:
        print(f"Error saving received file: {e}")
        return jsonify({"status": "error", "message": f"Could not save file on server: {e}"}), 500

    return jsonify({
        "status": "received",
        "size": file_size,
        "message": "Graph data received successfully."
    }), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
