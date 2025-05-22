import os
import sys
import subprocess
import argparse
import time
import requests

DEFAULT_EXPORT_BASE_DIR = "./export"
DEFAULT_PMD_REPORT_REL = "lint/pmd_report.json"
DEFAULT_JOERN_EXPORT_REL = "cpg_all/export.json"
DEFAULT_MERGED_OUTPUT_REL = "merged_graph.json"
DEFAULT_MERGE_SCRIPT = "./merge_tool.py"
DEFAULT_TARGET_URL = "http://localhost:5001/api/upload-graph"
DEFAULT_COMPOSE_FILE = "./docker-compose.yml"


def run_command(command_list, cwd=None, check=True, capture=True, env=None, stream_output=False):
    """Runs an external command, handles errors, optionally streams output."""
    print(f"\nRunning command: {' '.join(command_list)}")
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
            print("stdout:\n", process.stdout)
        if not stream_output and capture and process.stderr:
            print("stderr:\n", process.stderr)
        return True, process
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed with exit code {e.returncode}")
        if not stream_output and capture:
            if e.stdout: print("stdout:\n", e.stdout)
            if e.stderr: print("stderr:\n", e.stderr)
        return False, e
    except FileNotFoundError:
        print(f"ERROR: Command not found: '{command_list[0]}'. Is it installed and in PATH?")
        return False, None
    except Exception as e:
        print(f"An unexpected error occurred running command: {e}")
        return False, e


def attempt_joern_repair(export_dir):
    print("Attempting self-repair for Joern (primarily by script re-run)...")
    print("Joern script should clear its own temp cpg.bin. Please retry.")
    return True


def verify_step(success, step_name, repair_func=None, repair_args=None, exit_on_fail=True):
    if success:
        print(f"--- Step '{step_name}' completed successfully. ---")
        return True

    print(f"--- Step '{step_name}' FAILED. ---")
    if repair_func:
        print("Attempting repair...")
        repaired = repair_func(**(repair_args or {}))
        if repaired:
            print("Repair suggestion made (e.g., re-run).")
        else:
            print("Repair function did not indicate a fix or no action taken.")
    else:
        print("No repair function specified for this step.")

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
            print(f"ERROR: {step_name} with command '{' '.join(command)}' failed.")
        return success

    def __enter__(self):
        print("\n--- Starting mock_receiver service (Context Manager) ---")
        if not self._run_compose_command(["up", "-d", "--build", "mock_receiver"], "Starting mock_receiver"):
            raise RuntimeError("Failed to start mock_receiver service.")

        print("Waiting a few seconds for mock_receiver to initialize...")
        time.sleep(5)
        check_running_cmd = ["docker-compose", "-f", self.compose_file_name, "ps", "-q", "mock_receiver"]
        success_ps, ps_process = run_command(check_running_cmd, cwd=self.script_dir, capture=True, check=False)
        if not success_ps or not ps_process.stdout.strip():
            print("ERROR: mock_receiver container does not appear to be running after 'up -d'.")
            logs_cmd = ["docker-compose", "-f", self.compose_file_name, "logs", "--tail=50", "mock_receiver"]
            run_command(logs_cmd, cwd=self.script_dir, stream_output=True, check=False)
            raise RuntimeError("mock_receiver container failed to start or stay running.")

        self.is_running = True
        print("--- mock_receiver service confirmed running. ---")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("\n--- Stopping mock_receiver service (Context Manager) ---")
        if self.is_running:
            stop_success = self._run_compose_command(["stop", "mock_receiver"], "Stopping mock_receiver")
            self._run_compose_command(["rm", "-f", "mock_receiver"], "Removing mock_receiver")
            if not stop_success:
                print("Warning: mock_receiver might not have stopped cleanly.")
        else:
            print("INFO: mock_receiver was not marked as running, attempting cleanup anyway.")
            self._run_compose_command(["rm", "-f", "mock_receiver"], "Removing mock_receiver (cleanup attempt)")

        self.is_running = False
        print("--- mock_receiver service cleanup finished. ---")


DEFAULT_EXPORT_BASE_DIR = "./export"
DEFAULT_COMPOSE_FILE = "./docker-compose.yml"


def run_analysis_containers(compose_file_name, script_dir, pmd_report_path, joern_export_path, export_base_dir):
    """Runs Joern and Linters using Docker Compose. Assumes CWD is script_dir."""
    print("\n--- Running Joern and Linter services ---")
    command = [
        "docker-compose", "-f", compose_file_name, "up",
        "--build",
        "--abort-on-container-exit",
        "--exit-code-from", "lint",
        "joern", "lint"
    ]
    success, process = run_command(command, check=False, capture=False, stream_output=True, cwd=script_dir)
    if not success and process is None:
        print("ERROR: Failed to execute docker-compose command (e.g., not found).")
        return False

    exit_code = process.returncode if hasattr(process, 'returncode') else 1
    if exit_code != 0:
        print(f"ERROR: Docker Compose (for joern/lint) exited with non-zero status code: {exit_code}")
        return False

    if not os.path.exists(pmd_report_path) or os.path.getsize(pmd_report_path) == 0:
        print(f"ERROR: Expected PMD report file not found or is empty after docker-compose run: {pmd_report_path}")
        return False
    if not os.path.exists(joern_export_path) or os.path.getsize(joern_export_path) == 0:
        print(f"ERROR: Expected Joern export file not found or is empty after docker-compose run: {joern_export_path}")
        return False
    return True


def run_merge_script(script_path, pmd_input, joern_input, output_path):
    command = [
        sys.executable,
        script_path,
        "--pmd-input", pmd_input,
        "--joern-input", joern_input,
        "--output", output_path
    ]
    success, _ = run_command(command)
    if success and (not os.path.exists(output_path) or os.path.getsize(output_path) == 0):
        print(f"ERROR: Merge script reported success, but output file not found or is empty: {output_path}")
        return False
    return success


def send_data(file_path, target_url):
    print(f"\nSending file '{file_path}' to {target_url}...")
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        print(f"ERROR: File to send not found or is empty: {file_path}")
        return False
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    timeout_seconds = 120
    try:
        with open(file_path, 'rb') as f:
            response = requests.post(target_url, data=f, headers=headers, timeout=timeout_seconds)
        response.raise_for_status()
        print(f"Data sent successfully. Status: {response.status_code}")
        print("Server response:", response.json())
        return True
    except requests.exceptions.Timeout:
        print(f"ERROR: Request timed out after {timeout_seconds} seconds.")
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR: Could not connect to the server at {target_url}. Is it running? Details: {e}")
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to send data: {e}")
        if e.response is not None:
            print(f"Server responded with Status Code: {e.response.status_code}")
            try:
                print(f"Server response body: {e.response.text}")
            except Exception:
                pass
    except IOError as e:
        print(f"ERROR: Could not read file {file_path}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during sending: {e}")
    return False


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(description="Orchestrate Joern/PMD analysis, merge results, and upload.")
    parser.add_argument("--export-dir", default=os.path.join(script_dir, DEFAULT_EXPORT_BASE_DIR),
                        help="Base directory for analysis outputs.")
    parser.add_argument("--pmd-report",
                        help=f"Relative path to PMD JSON report within export-dir (default: {DEFAULT_PMD_REPORT_REL}).")
    parser.add_argument("--joern-export",
                        help=f"Relative path to Joern GraphSON export within export-dir (default: {DEFAULT_JOERN_EXPORT_REL}).")
    parser.add_argument("--merged-output",
                        help=f"Relative path for the merged output file within export-dir (default: {DEFAULT_MERGED_OUTPUT_REL}).")
    parser.add_argument("--merge-script", default=os.path.join(script_dir, DEFAULT_MERGE_SCRIPT),
                        help="Path to the merge_tool.py script.")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL, help="URL to send the merged results to.")
    parser.add_argument("--skip-docker", action="store_true", help="Skip the docker-compose step for joern/lint.")
    parser.add_argument("--skip-upload", action="store_true", help="Skip the final upload step.")
    parser.add_argument("--compose-file", default=os.path.join(script_dir, DEFAULT_COMPOSE_FILE),
                        help="Path to the docker-compose file.")
    parser.add_argument("--java-project-dir", default=os.path.abspath(os.path.join(script_dir, "..", "project")),
                        help="Path to the Java project directory to be analyzed.")
    args = parser.parse_args()

    export_base_dir = os.path.abspath(args.export_dir)
    pmd_report_path = os.path.join(export_base_dir, args.pmd_report or DEFAULT_PMD_REPORT_REL)
    joern_export_path = os.path.join(export_base_dir, args.joern_export or DEFAULT_JOERN_EXPORT_REL)
    merged_output_path = os.path.join(export_base_dir, args.merged_output or DEFAULT_MERGED_OUTPUT_REL)

    print("--- Starting Analysis Workflow ---")
    print(f"Script Directory: {script_dir}")
    print(f"Java Project Directory to analyze: {args.java_project_dir}")
    print(f"Export Directory: {export_base_dir}")

    if not args.skip_docker and not os.path.isdir(args.java_project_dir):
        print(f"ERROR: Java project directory not found at: {args.java_project_dir}")
        sys.exit(1)

    os.makedirs(os.path.dirname(pmd_report_path), exist_ok=True)
    os.makedirs(os.path.dirname(joern_export_path), exist_ok=True)
    os.makedirs(os.path.dirname(merged_output_path), exist_ok=True)
    print("Ensured local export directories exist.")


    def perform_core_workflow():
        original_cwd = os.getcwd()
        if original_cwd != script_dir:
            os.chdir(script_dir)
            print(f"Changed CWD to: {script_dir} for docker-compose context.")

        try:
            # Step 1: Run Docker Compose Analysis (joern & lint)
            if not args.skip_docker:
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
            else:
                print("--- Skipping Docker Compose (Joern/Lint) step as requested. ---")
                if not os.path.exists(pmd_report_path) or os.path.getsize(pmd_report_path) == 0:
                    print(f"ERROR: --skip-docker specified, but PMD report not found or empty at {pmd_report_path}")
                    sys.exit(1)
                if not os.path.exists(joern_export_path) or os.path.getsize(joern_export_path) == 0:
                    print(f"ERROR: --skip-docker specified, but Joern export not found or empty at {joern_export_path}")
                    sys.exit(1)

            # Step 2: Run Merge Script
            merge_success = run_merge_script(
                args.merge_script,
                pmd_report_path,
                joern_export_path,
                merged_output_path
            )
            verify_step(merge_success, "Merge Reports")

            # Step 3: Send Data (only if not skipped and if receiver is managed)
            # The actual call to send_data will happen here if the 'with' block for receiver is active
            if not args.skip_upload:
                upload_success = send_data(merged_output_path, args.target_url)
                verify_step(upload_success, "Send Data")

        finally:
            if original_cwd != script_dir and os.getcwd() == script_dir:
                os.chdir(original_cwd)
                print(f"Restored CWD to: {original_cwd}")


    if not args.skip_upload:
        print("Upload is enabled. Managing mock_receiver lifecycle.")
        with MockReceiverManager(os.path.basename(args.compose_file), script_dir):
            perform_core_workflow()
    else:
        print("--- Skipping Upload, mock_receiver will not be started. ---")
        perform_core_workflow()

    print("\n--- Workflow Completed Successfully ---")
