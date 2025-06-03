import os
from flask import Flask, request, jsonify
from payload_parser import PayloadParser

app = Flask(__name__)
UPLOAD_FOLDER = '/uploads'


payload_file_parser = PayloadParser(upload_folder=UPLOAD_FOLDER)

@app.route('/api/upload-graph', methods=['POST'])
def upload_graph():
    if 'application/json' not in request.content_type:
        return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 415

    if not request.data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    success, saved_filename, file_size, message = payload_file_parser.parse_and_save(
        request_data_bytes=request.data,
        content_type_header=request.content_type,
        http_headers=request.headers
    )

    if success:
        print(f"Receiver: Successfully processed and saved file: {saved_filename}, Size: {file_size} bytes")
        return jsonify({
            "status": "received_and_processed",
            "saved_filename": saved_filename,
            "size": file_size,
            "message": message # Message from parser
        }), 200
    else:
        print(f"Receiver: Error processing/saving file. Parser message: {message}")
        return jsonify({
            "status": "error",
            "message": f"Server error during processing: {message}"
        }), 500


if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    print(f"Mock receiver started. Uploads will be saved to: {os.path.abspath(UPLOAD_FOLDER)}")
    app.run(debug=True, host='0.0.0.0', port=5000)