import os
import sys
import subprocess
import argparse
import time
import requests
import mimetypes
import base64
import json

DEFAULT_EXPORT_BASE_DIR = "./export"
DEFAULT_PMD_REPORT_REL = "lint/pmd_report.json"
DEFAULT_JOERN_EXPORT_REL = "cpg_all/export.json"
DEFAULT_TARGET_URL = "http://localhost:5001/api/upload-graph"
DEFAULT_COMPOSE_FILE = "./docker-compose.yml"


def run_command(command_list, cwd=None, check=True, capture=True, env=None, stream_output=False):
    """Runs an external command, handles errors, optionally streams output."""
    print(f"\nRunning command: {' '.join(command_list)}", flush=True)
    stdout_pipe = None if stream_output else subprocess.PIPE
    stderr_pipe = None if stream_output else subprocess.PIPE
    try:
        process = subprocess.run(
            command_list,
            check=check,
            stdout=stdout_pipe,
            stderr=stderr_pipe,
            text=True,
            cwd=cwd,
            env=env
        )
        if not stream_output and capture and process.stdout:
            print("stdout:\n", process.stdout, flush=True)
        if not stream_output and capture and process.stderr:
            print("stderr:\n", process.stderr, flush=True)
        return True, process
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed with exit code {e.returncode}", flush=True)
        if not stream_output and capture:
            if e.stdout: print("stdout:\n", e.stdout, flush=True)
            if e.stderr: print("stderr:\n", e.stderr, flush=True)
        return False, e
    except FileNotFoundError:
        print(f"ERROR: Command not found: '{command_list[0]}'. Is it installed and in PATH?", flush=True)
        return False, None
    except Exception as e:
        print(f"An unexpected error occurred running command: {e}", flush=True)
        return False, e


def attempt_joern_repair(export_dir):
    print("Attempting self-repair for Joern (primarily by script re-run)...", flush=True)
    print("Joern script should clear its own temp cpg.bin. Please retry.", flush=True)
    return True


def verify_step(success, step_name, repair_func=None, repair_args=None, exit_on_fail=True):
    if success:
        print(f"--- Step '{step_name}' completed successfully. ---", flush=True)
        return True

    print(f"--- Step '{step_name}' FAILED. ---", flush=True)
    if repair_func:
        print("Attempting repair...", flush=True)
        repaired = repair_func(**(repair_args or {}))
        if repaired:
            print("Repair suggestion made (e.g., re-run).", flush=True)
        else:
            print("Repair function did not indicate a fix or no action taken.", flush=True)
    else:
        print("No repair function specified for this step.", flush=True)

    if exit_on_fail:
        sys.exit(1)
    return False


class MockReceiverManager:
    def __init__(self, compose_file_name, script_dir):
        self.compose_file_name = compose_file_name
        self.script_dir = script_dir
        self.is_running = False

    def _run_compose_command(self, args_list, step_name="MockReceiver operation"):
        command = ["docker-compose", "-f", self.compose_file_name] + args_list
        success, _ = run_command(command, stream_output=True, cwd=self.script_dir, check=False)
        if not success:
            print(f"ERROR: {step_name} with command '{' '.join(command)}' failed.", flush=True)
        return success

    def __enter__(self):
        print("\n--- Starting mock_receiver service (Context Manager) ---", flush=True)
        if not self._run_compose_command(["up", "-d", "--build", "mock_receiver"], "Starting mock_receiver"):
            raise RuntimeError("Failed to start mock_receiver service.")

        print("Waiting a few seconds for mock_receiver to initialize...", flush=True)
        time.sleep(5)
        check_running_cmd = ["docker-compose", "-f", self.compose_file_name, "ps", "-q", "mock_receiver"]
        success_ps, ps_process = run_command(check_running_cmd, cwd=self.script_dir, capture=True, check=False)
        if not success_ps or not ps_process.stdout.strip():
            print("ERROR: mock_receiver container does not appear to be running after 'up -d'.", flush=True)
            logs_cmd = ["docker-compose", "-f", self.compose_file_name, "logs", "--tail=50", "mock_receiver"]
            run_command(logs_cmd, cwd=self.script_dir, stream_output=True, check=False)
            raise RuntimeError("mock_receiver container failed to start or stay running.")

        self.is_running = True
        print("--- mock_receiver service confirmed running. ---", flush=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("\n--- Stopping mock_receiver service (Context Manager) ---", flush=True)
        if self.is_running:
            stop_success = self._run_compose_command(["stop", "mock_receiver"], "Stopping mock_receiver")
            self._run_compose_command(["rm", "-f", "mock_receiver"], "Removing mock_receiver")
            if not stop_success:
                print("Warning: mock_receiver might not have stopped cleanly.", flush=True)
        else:
            print("INFO: mock_receiver was not marked as running, attempting cleanup anyway.", flush=True)
            self._run_compose_command(["rm", "-f", "mock_receiver"], "Removing mock_receiver (cleanup attempt)")

        self.is_running = False
        print("--- mock_receiver service cleanup finished. ---", flush=True)


def run_analysis_containers(compose_file_name, script_dir, pmd_report_path, joern_export_path, export_base_dir):
    """Runs Joern and Linters using Docker Compose. Assumes CWD is script_dir."""
    print("\n--- Running Joern and Linter services ---", flush=True)
    command = [
        "docker-compose", "-f", compose_file_name, "up",
        "--build",
        "joern", "lint"
    ]
    success, process = run_command(command, check=False, capture=False, stream_output=True, cwd=script_dir)
    
    if process is None:
        print("ERROR: Failed to execute docker-compose command (e.g., not found).", flush=True)
        return False

    exit_code = process.returncode if hasattr(process, 'returncode') else 1
    if exit_code != 0:
        print(f"ERROR: Docker Compose (for joern/lint) exited with non-zero status code: {exit_code}. This usually means joern or lint container failed.", flush=True)
        return False

    if not os.path.exists(pmd_report_path) or os.path.getsize(pmd_report_path) == 0:
        print(f"ERROR: Expected PMD report file not found or is empty after docker-compose run: {pmd_report_path}", flush=True)
        return False
    if not os.path.exists(joern_export_path) or os.path.getsize(joern_export_path) == 0:
        print(f"ERROR: Expected Joern export file not found or is empty after docker-compose run: {joern_export_path}", flush=True)
        return False
    return True


def send_data(file_path, target_url, content_type_override=None, additional_headers=None, force_json_payload=False):
    print(f"\nSending file '{os.path.basename(file_path)}' (from '{file_path}') to {target_url}...", flush=True)
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        print(f"ERROR: File to send not found or is empty: {file_path}", flush=True)
        return False

    actual_content_type = None
    data_to_send = None
    is_file_stream = False

    if force_json_payload:
        try:
            with open(file_path, 'rb') as f_bytes:
                encoded_content = base64.b64encode(f_bytes.read()).decode('utf-8')
            
            payload = {
                "original_filename": os.path.basename(file_path),
                "file_content_base64": encoded_content
            }
            if additional_headers:
                if 'X-File-Path-In-Project' in additional_headers:
                    payload['x_file_path_in_project'] = additional_headers['X-File-Path-In-Project']
                if 'X-File-Type' in additional_headers:
                    payload['x_file_type'] = additional_headers['X-File-Type']

            data_to_send = json.dumps(payload)
            actual_content_type = 'application/json'
            print(f"Prepared base64 JSON payload for {os.path.basename(file_path)}.", flush=True)
        except Exception as e:
            print(f"ERROR: Could not read and encode file {file_path} for JSON payload: {e}", flush=True)
            return False
    else:
        actual_content_type = content_type_override
        if not actual_content_type:
            guessed_type, _ = mimetypes.guess_type(file_path)
            actual_content_type = guessed_type or 'application/octet-stream'
            print(f"Guessed Content-Type: {actual_content_type} for file {os.path.basename(file_path)}", flush=True)
        is_file_stream = True

    headers = {'Accept': 'application/json'}
    headers['Content-Type'] = actual_content_type
    if additional_headers:
        headers.update(additional_headers)

    timeout_seconds = 120
    try:
        if is_file_stream:
            with open(file_path, 'rb') as f_stream:
                response = requests.post(target_url, data=f_stream, headers=headers, timeout=timeout_seconds)
        else:
            response = requests.post(target_url, data=data_to_send, headers=headers, timeout=timeout_seconds)
        
        response.raise_for_status()
        print(f"Data sent successfully. Status: {response.status_code}", flush=True)
        try:
            print("Server response:", response.json(), flush=True)
        except requests.exceptions.JSONDecodeError:
            print("Server response (not JSON):", response.text, flush=True)
        return True
    except requests.exceptions.Timeout:
        print(f"ERROR: Request timed out after {timeout_seconds} seconds.", flush=True)
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR: Could not connect to the server at {target_url}. Is it running? Details: {e}", flush=True)
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to send data: {e}", flush=True)
        if e.response is not None:
            print(f"Server responded with Status Code: {e.response.status_code}", flush=True)
            try:
                print(f"Server response body: {e.response.text}", flush=True)
            except Exception:
                pass
    except IOError as e:
        print(f"ERROR: Could not read file {file_path}: {e}", flush=True)
    except Exception as e:
        print(f"An unexpected error occurred during sending: {e}", flush=True)
    return False


def send_all_project_files(project_dir_path, target_url_base, cli_args):
    print(f"\n--- Starting to send all project files from '{project_dir_path}' ---", flush=True)
    overall_success = True
    file_count = 0
    error_count = 0

    if not os.path.isdir(project_dir_path):
        print(f"ERROR: Project directory not found: {project_dir_path}", flush=True)
        return False

    for root, _, files in os.walk(project_dir_path):
        for filename in files:
            file_abs_path = os.path.join(root, filename)
            file_rel_path = os.path.relpath(file_abs_path, project_dir_path)
            
            normalized_file_rel_path = file_rel_path.replace('\\', '/')

            print(f"\nAttempting to send project file: {normalized_file_rel_path} (from: {file_abs_path})", flush=True)
            
            additional_hdrs = {
                'X-File-Path-In-Project': normalized_file_rel_path,
                'X-File-Type': 'project-source-file'
            }

            success = send_data(
                file_abs_path,
                target_url_base,
                additional_headers=additional_hdrs,
                force_json_payload=True
            )
            if not success:
                print(f"ERROR: Failed to send project file: {normalized_file_rel_path}", flush=True)
                overall_success = False
                error_count += 1
            else:
                file_count += 1
    
    if error_count > 0:
        print(f"--- Finished sending project files: {file_count} sent successfully, {error_count} failed. ---", flush=True)
    elif file_count > 0:
        print(f"--- Successfully sent {file_count} project files. ---", flush=True)
    else:
        print(f"--- No project files found or sent from '{project_dir_path}'. ---", flush=True)
    return overall_success


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(description="Orchestrate Joern/PMD analysis, and upload results and project files.")
    parser.add_argument("--export-dir", default=os.path.join(script_dir, DEFAULT_EXPORT_BASE_DIR),
                        help="Base directory for analysis outputs.")
    parser.add_argument("--pmd-report",
                        help=f"Relative path to PMD JSON report within export-dir (default: {DEFAULT_PMD_REPORT_REL}).")
    parser.add_argument("--joern-export",
                        help=f"Relative path to Joern GraphSON export within export-dir (default: {DEFAULT_JOERN_EXPORT_REL}).")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL, help="URL to send the results and files to.")
    parser.add_argument("--skip-docker", action="store_true", help="Skip the docker-compose step for joern/lint.")
    parser.add_argument("--skip-upload", action="store_true", help="Skip all upload steps.")
    parser.add_argument("--compose-file", default=os.path.join(script_dir, DEFAULT_COMPOSE_FILE),
                        help="Path to the docker-compose file.")
    parser.add_argument("--java-project-dir", default=os.path.abspath(os.path.join(script_dir, "..", "project")),
                        help="Path to the Java project directory to be analyzed and uploaded.")
    args = parser.parse_args()

    export_base_dir = os.path.abspath(args.export_dir)
    pmd_report_path = os.path.join(export_base_dir, args.pmd_report or DEFAULT_PMD_REPORT_REL)
    joern_export_path = os.path.join(export_base_dir, args.joern_export or DEFAULT_JOERN_EXPORT_REL)

    print("--- Starting Analysis and Upload Workflow ---", flush=True)
    print(f"Script Directory: {script_dir}", flush=True)
    print(f"Java Project Directory to analyze/upload: {args.java_project_dir}", flush=True)
    print(f"Export Directory: {export_base_dir}", flush=True)

    if not args.skip_docker and not os.path.isdir(args.java_project_dir):
        print(f"ERROR: Java project directory not found at: {args.java_project_dir}", flush=True)
        sys.exit(1)

    os.makedirs(os.path.dirname(pmd_report_path), exist_ok=True)
    os.makedirs(os.path.dirname(joern_export_path), exist_ok=True)
    print("Ensured local export directories exist.", flush=True)


    def perform_core_workflow():
        original_cwd = os.getcwd()
        if original_cwd != script_dir:
            os.chdir(script_dir)
            print(f"Changed CWD to: {script_dir} for docker-compose context.", flush=True)

        try:
            # Step 1: Run Docker Compose Analysis (joern & lint)
            if not args.skip_docker:
                print("--- Starting Docker-based analysis (Joern/Lint)... ---", flush=True)
                docker_success = run_analysis_containers(
                    os.path.basename(args.compose_file),
                    script_dir,
                    pmd_report_path,
                    joern_export_path,
                    export_base_dir
                )
                verify_step(docker_success, "Docker Compose Analysis (Joern/Lint)",
                            repair_func=attempt_joern_repair,
                            repair_args={'export_dir': export_base_dir})
                print("--- Docker-based analysis finished. ---", flush=True)
            else:
                print("--- Skipping Docker Compose (Joern/Lint) step as requested. ---", flush=True)
                if not os.path.exists(pmd_report_path) or os.path.getsize(pmd_report_path) == 0:
                    print(f"ERROR: --skip-docker specified, but PMD report not found or empty at {pmd_report_path}", flush=True)
                    sys.exit(1)
                if not os.path.exists(joern_export_path) or os.path.getsize(joern_export_path) == 0:
                    print(f"ERROR: --skip-docker specified, but Joern export not found or empty at {joern_export_path}", flush=True)
                    sys.exit(1)

            # Step 2: Upload results if not skipped
            if not args.skip_upload:
                print("--- Starting Upload sequence... ---", flush=True)
                # Send Joern Export - REMOVED AS PER USER REQUEST
                print("--- Skipping Joern CPG upload as per new requirements. ---", flush=True)

                # Send PMD Report
                if os.path.exists(pmd_report_path):
                    pmd_headers = {'X-File-Type': 'pmd-report', 'X-Original-Filename': os.path.basename(pmd_report_path)}
                    pmd_upload_success = send_data(
                        pmd_report_path,
                        args.target_url,
                        content_type_override='application/json',
                        additional_headers=pmd_headers
                    )
                    verify_step(pmd_upload_success, f"Send PMD Report ({os.path.basename(pmd_report_path)})")
                else:
                    print(f"WARNING: PMD report not found at {pmd_report_path}. Skipping PMD upload.", flush=True)
                    verify_step(False, "Send PMD Report (File Not Found)", exit_on_fail=False) # Don't exit if just PMD is missing unless critical


                # Send All Project Files
                if os.path.isdir(args.java_project_dir):
                    project_files_upload_success = send_all_project_files(args.java_project_dir, args.target_url, args)
                    verify_step(project_files_upload_success, "Send All Project Files")
                else:
                    print(f"ERROR: Java project directory not found at: {args.java_project_dir}. Skipping sending project files.", flush=True)
                    verify_step(False, "Send All Project Files (Directory Not Found)", exit_on_fail=True)
                print("--- Upload sequence finished. ---", flush=True)

            else:
                print("--- Skipping all Upload steps as requested. ---", flush=True)

        finally:
            if original_cwd != script_dir and os.getcwd() == script_dir:
                os.chdir(original_cwd)
                print(f"Restored CWD to: {original_cwd}", flush=True)


    if not args.skip_upload:
        print("Upload is enabled. Managing mock_receiver lifecycle.", flush=True)
        with MockReceiverManager(os.path.basename(args.compose_file), script_dir):
            perform_core_workflow()
    else:
        print("--- Skipping Upload, mock_receiver will not be started. ---", flush=True)
        perform_core_workflow()

    print("\n--- Workflow Completed Successfully ---", flush=True)
