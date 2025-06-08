import os
import json
import base64
import mimetypes

class PayloadParser:
    """
    Parses incoming request data, potentially decoding it from a
    base64-encoded JSON wrapper, and saves the original file content.
    """

    def __init__(self, upload_folder):
        self.upload_folder = upload_folder
        os.makedirs(self.upload_folder, exist_ok=True)

    def parse_and_save(self, request_data_bytes, content_type_header, http_headers=None):
        filename_to_save = "unknown_file"
        content_to_write = None
        is_base64_encoded_json_wrapper = False

        main_content_type = content_type_header.split(';')[0].strip().lower()

        if main_content_type == 'application/json':
            try:
                payload_str = request_data_bytes.decode('utf-8')
                data = json.loads(payload_str)

                if isinstance(data, dict) and \
                   'file_content_base64' in data and \
                   'original_filename' in data:
                    is_base64_encoded_json_wrapper = True
                    filename_to_save = data['original_filename']
                    base64_content = data['file_content_base64']
                    try:
                        content_to_write = base64.b64decode(base64_content)
                        print(f"Parser: Detected base64 encoded file in JSON: {filename_to_save}")
                    except base64.BinasciiError as b64_error:
                        msg = f"Invalid base64 data for {filename_to_save}: {b64_error}"
                        print(f"Parser: ERROR: {msg}")
                        return False, filename_to_save, 0, msg
                else:
                    content_to_write = request_data_bytes
                    if http_headers and 'X-Original-Filename' in http_headers:
                        filename_to_save = http_headers['X-Original-Filename']
                    else:
                        filename_to_save = "received_payload.json"
                    print(f"Parser: Detected raw JSON payload, will save as: {filename_to_save}")

            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                msg = f"Content-Type is application/json but failed to parse as JSON: {e}. Saving raw data."
                print(f"Parser: WARNING: {msg}")
                content_to_write = request_data_bytes # Save the raw bytes
                if http_headers and 'X-Original-Filename' in http_headers:
                    filename_to_save = http_headers['X-Original-Filename']
                else:
                    filename_to_save = "received_malformed_json.bin"

        else:
            content_to_write = request_data_bytes
            if http_headers and 'X-Original-Filename' in http_headers:
                filename_to_save = http_headers['X-Original-Filename']
            else:
                guessed_extension = mimetypes.guess_extension(main_content_type)
                filename_to_save = f"received_file{guessed_extension or '.dat'}"
            print(f"Parser: Detected non-JSON content-type '{main_content_type}', will save as: {filename_to_save}")

        if content_to_write is None:
            return False, None, 0, "Parser: Could not determine content to write."

        safe_basename = os.path.basename(filename_to_save)
        if not safe_basename or safe_basename in ('.', '..'):
            safe_basename = "default_safe_filename"
            if is_base64_encoded_json_wrapper:
                 original_ext = os.path.splitext(filename_to_save)[1]
                 safe_basename += original_ext
            elif main_content_type == 'application/json' and not is_base64_encoded_json_wrapper:
                 safe_basename += ".json"


        save_path = os.path.join(self.upload_folder, safe_basename)

        try:
            with open(save_path, 'wb') as f:
                f.write(content_to_write)
            file_size = len(content_to_write)
            msg = f"File '{safe_basename}' (Size: {file_size} bytes) saved successfully to {save_path}."
            print(f"Parser: {msg}")
            return True, safe_basename, file_size, msg
        except IOError as e:
            msg = f"Could not save file '{safe_basename}' to '{save_path}': {e}"
            print(f"Parser: ERROR: {msg}")
            return False, safe_basename, 0, msg
        except Exception as e:
            msg = f"An unexpected error occurred while saving '{safe_basename}': {e}"
            print(f"Parser: ERROR: {msg}")
            return False, safe_basename, 0, msg