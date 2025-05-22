## Before you run
For proper work of the module, installed python request library is required. You can install it using the following command:
```bash
pip install requests
```

# Exporter Module Documentation

## 1. Overview

The `exporter` module is responsible for orchestrating a multi-step static analysis and data processing workflow. Its primary goal is to:

1.  Run static analysis tools (PMD for linting, Joern for Code Property Graph (CPG) generation) on a target Java project. These tools are executed within Docker containers managed by Docker Compose.
2.  Merge the outputs from PMD (JSON report) and Joern (GraphSON CPG export) into a single, unified GraphSON file.
3.  Optionally, send this merged graph file to a specified HTTP endpoint for further processing or storage (e.g., by an AI system).
4.  Includes a mock HTTP receiver service for testing the upload functionality.

The module is designed to be run from its own directory (`exporter/`) and expects the Java project to be analyzed to be located in a sibling directory (e.g., `../project/`).


## 2. Core Components

### 2.1. `orchestrate.py`

This is the main entry point and orchestrator of the entire workflow.

**Functionality:**

*   **Argument Parsing:** Accepts command-line arguments to configure paths, skip steps, and specify the target URL for uploads.
    *   `--export-dir`: Base directory for outputs (default: `./export`).
    *   `--pmd-report`, `--joern-export`, `--merged-output`: Relative paths for specific output files within `export-dir`.
    *   `--merge-script`: Path to `merge_tool.py` (default: `./merge_tool.py`).
    *   `--target-url`: Endpoint for uploading the merged graph.
    *   `--skip-docker`: Skips running Joern and PMD via Docker Compose (assumes reports exist).
    *   `--skip-upload`: Skips the final upload step.
    *   `--compose-file`: Path to `docker-compose.yml`.
    *   `--java-project-dir`: Path to the Java project to be analyzed (default: `../project`).
*   **Directory Management:** Ensures necessary output directories (`export/lint`, `export/cpg_all`) exist on the host before running Docker containers or the merge script.
*   **CWD Management:** Changes the Current Working Directory (CWD) to the `exporter/` directory (where `docker-compose.yml` resides) before executing `docker-compose` commands. This ensures correct resolution of relative paths within `docker-compose.yml` (e.g., volume mounts like `../project`). The original CWD is restored upon completion.
*   **Workflow Steps:**
    1.  **(Optional) Start Mock Receiver:** If uploads are not skipped, it uses the `MockReceiverManager` context manager to start the `mock_receiver` Docker service in detached mode.
    2.  **Run Analysis Containers (`run_analysis_containers`):**
        *   Executes `docker-compose -f <compose_file> up --build --abort-on-container-exit --exit-code-from lint joern lint`.
        *   This command builds (if necessary) and runs the `joern` and `lint` services defined in `docker-compose.yml`.
        *   `mock_receiver` is NOT part of this specific `up` command as it's managed separately by the context manager.
        *   The function checks the exit code of the `docker-compose` command and verifies that the expected output files (`pmd_report.json`, `export.json`) are created and non-empty.
    3.  **Run Merge Script (`run_merge_script`):**
        *   Executes `merge_tool.py` as a Python subprocess.
        *   Passes the paths to the PMD report, Joern export, and the desired merged output file as command-line arguments to `merge_tool.py`.
        *   Verifies that the merge script exits successfully and creates a non-empty merged output file.
    4.  **(Optional) Send Data (`send_data`):**
        *   If uploads are not skipped, it sends the `merged_graph.json` file via an HTTP POST request to the configured `--target-url`.
        *   The request uses `Content-Type: application/json`.
        *   Checks for successful HTTP status codes (2xx).
    5.  **(Optional) Stop Mock Receiver:** The `MockReceiverManager`'s `__exit__` method automatically stops and removes the `mock_receiver` container when the `with` block finishes.
*   **Error Handling & Verification (`verify_step`, `attempt_joern_repair`):**
    *   Each major step's success is verified.
    *   If a step fails, the script typically exits.
    *   A basic `attempt_joern_repair` function suggests a manual re-run if Joern-related steps fail, after clearing potential stale `cpg.bin` files (though current Joern script clears its own temp `cpg.bin`).
*   **Helper `run_command`:** A utility function to execute external shell commands, capture their output, and handle errors.

**`MockReceiverManager` Class (within `orchestrate.py`):**
*   A Python context manager (`__enter__`, `__exit__`).
*   `__enter__`: Starts the `mock_receiver` service using `docker-compose up -d --build mock_receiver`. It waits a few seconds for initialization and checks if the container is running.
*   `__exit__`: Stops and removes the `mock_receiver` service using `docker-compose stop mock_receiver` and `docker-compose rm -f mock_receiver`. This ensures cleanup even if errors occur within the `with` block.

### 2.2. `merge_tool.py`

This Python script is responsible for merging the PMD JSON report and the Joern GraphSON export.

**Functionality:**

*   **Argument Parsing:** Accepts `--pmd-input`, `--joern-input`, and `--output` file paths.
*   **Load Data:** Loads and parses the PMD JSON and Joern GraphSON files.
*   **GraphSON Wrapper Handling:**
    *   Detects if the Joern GraphSON is wrapped in a TinkerPop typed structure (e.g., `{"@type": "tinker:graph", "@value": {GRAPH_OBJECTS}}`).
    *   If so, it extracts the core graph components (the object containing `vertices` and `edges`) from the `"@value"` field.
*   **PMD Data Processing:** Converts the PMD report into a dictionary mapping normalized file paths to lists of violations for efficient lookup.
*   **Path Normalization (`normalize_path`):** A helper function to standardize file paths (e.g., replaces backslashes, uses `os.path.normpath`).
*   **Merging Logic:**
    1.  Iterates through the `vertices` in the (potentially unwrapped) Joern graph data.
    2.  Identifies `FILE` labeled nodes.
    3.  **Path Extraction from Joern `FILE` Node:** Correctly extracts the file path string from the potentially nested `properties.NAME.["@value"].["@value"][0]` structure specific to Joern's GraphSON output for `FILE` nodes.
    4.  **Path Transformation:**
        *   Recognizes that Joern (for Java) often reports paths to compiled `.class` files, sometimes in temporary directories (e.g., `/tmp/jimple2cpg.../.../File.class`).
        *   Attempts to transform these Joern paths into a format comparable to PMD's source file paths (`.java` files, e.g., `/sources/src/main/java/.../File.java`). This involves:
            *   Skipping `<unknown>` paths.
            *   If a `.class` path is found and appears to be from `jimple2cpg`'s temporary output:
                *   Heuristically finding the package root (e.g., `org/`, `com/`).
                *   Prepending a base path (`/sources/src/main/java/`) that aligns with PMD's reported paths (this base is currently hardcoded and might need adjustment based on project structure).
                *   Replacing `.class` with `.java`.
        *   Normalizes the transformed Joern path.
    5.  **Matching and Injection:**
        *   If the normalized (and transformed) Joern `FILE` path matches a normalized PMD file path:
            *   A new property `pmd_violations` is added to the `properties` of the Joern `FILE` node.
            *   The value of `pmd_violations` is the array of violation objects from PMD for that file.
            *   If PMD reported no violations for a matched file, `pmd_violations` will be an empty array `[]`.
*   **Reporting:** Prints a summary of found `FILE` nodes, matched nodes, and a list of any PMD files that could not be matched to a Joern `FILE` node (with reasons).
*   **Saving Output:** Saves the modified Joern graph data (with injected PMD violations) to the specified output file. If the input Joern data was wrapped, it re-wraps the modified graph components into the original wrapper structure before saving.

### 2.3. `docker-compose.yml`

This file defines the Docker services used in the workflow. It is located in the `exporter/` directory.

**Services:**

*   **`joern` Service:**
    *   Uses the `ghcr.io/joernio/joern:nightly` image.
    *   **Volumes:**
        *   `../project:/sources`: Mounts the target Java project (located one level up from `exporter/`) into `/sources` inside the container. This is where Joern reads the code from.
        *   `./export:/export`: Mounts the host's `./exporter/export/` directory to `/export` inside the container. Joern writes its output here.
    *   **`working_dir: /app`**: Sets a neutral working directory.
    *   **Entrypoint Script:**
        *   Sets shell options for error handling (`set -euxo pipefail`).
        *   Defines `JAVA_SOURCE_PATH="/sources"`.
        *   Creates a temporary CPG file (`/app/cpg.bin`) by running `joern-parse "$${JAVA_SOURCE_PATH}" --language java --output /app/cpg.bin`. This explicitly uses the Java language frontend.
        *   Defines `JOERN_EXPORT_TARGET_DIR="/export/cpg_all"`.
        *   Removes any existing `JOERN_EXPORT_TARGET_DIR` to ensure `joern-export` can create it cleanly.
        *   Runs `joern-export /app/cpg.bin --repr=all --format=graphson --out="$${JOERN_EXPORT_TARGET_DIR}"`. Joern creates the `cpg_all` directory and places `export.json` (or similar default for GraphSON) inside it.
        *   Verifies that the expected output file (`$${JOERN_EXPORT_TARGET_DIR}/export.json`) exists and is non-empty.
        *   Changes ownership of the output file (`chown`) to match the UID/GID of the `/sources` mount point, attempting to align with host user permissions for easier access.
        *   Exits with `0` on success.
*   **`lint` Service (PMD):**
    *   Uses the `docker.io/pmdcode/pmd:latest` image.
    *   **Volumes:**
        *   `../project:/sources:ro`: Mounts the target Java project read-only.
        *   `./export/lint:/export/lint`: Mounts host's `./exporter/export/lint/` for PMD output.
    *   **`working_dir: /app`**.
    *   **Entrypoint Script:**
        *   Sets shell options (`set -uxo pipefail`).
        *   Defines `JAVA_SOURCE_PATH="/sources"` and output paths.
        *   Runs `pmd check -d "$${JAVA_SOURCE_PATH}" ... --fail-on-violation=false -r /export/lint/pmd_report.json`.
            *   Analyzes code in `/sources`.
            *   `--fail-on-violation=false` is used to prevent PMD from exiting with an error code solely due to finding violations.
        *   Captures PMD's exit code (`PMD_EXIT_CODE=$?`).
        *   Verifies that the output report file exists and is non-empty.
        *   Checks if `PMD_EXIT_CODE` is `0` (success) or `4` (violations found, which is acceptable for this workflow). If any other code, it exits with an error.
        *   Changes ownership of the PMD report file similar to the Joern service.
        *   Exits with `0` if the process is considered successful for the workflow.
*   **`mock_receiver` Service:**
    *   Builds an image using `receiver/Dockerfile.receiver`.
    *   **Ports:** Maps port `5001` on the host to port `5000` in the container (where Flask runs).
    *   **Volumes:** Maps host's `./exporter/uploads/` to `/uploads` in the container, allowing inspection of files received by the mock service.
    *   This service runs a simple Flask application (`receiver/mock_receiver.py`) that listens for POST requests on `/api/upload-graph` and saves the received data.

### 2.4. `receiver/` Sub-module

*   **`mock_receiver.py`:** A minimal Flask web application.
    *   Defines a single endpoint `/api/upload-graph` that accepts POST requests with JSON payloads.
    *   Saves the received request body to a file in the `/uploads` directory (inside the container, mapped to `./exporter/uploads/` on the host).
    *   Returns a JSON response confirming receipt.
    *   Runs on `0.0.0.0:5000` within its container.
*   **`Dockerfile.receiver`:** A simple Dockerfile to build the Flask application image:
    *   Uses a Python base image.
    *   Copies `requirements.txt` (for Flask) and installs dependencies.
    *   Copies `mock_receiver.py`.
    *   Sets Flask environment variables and exposes port `5000`.
    *   Runs the Flask app using `flask run`.
*   **`requirements.txt` (in `receiver/`):** Lists `Flask` as a dependency.

## 4. Workflow Execution (`orchestrate.py`)

1.  **Initialization:**
    *   Parses command-line arguments.
    *   Resolves absolute paths for inputs/outputs based on `script_dir` (location of `orchestrate.py`) and `export_dir`.
    *   Ensures host output directories exist.
2.  **Mock Receiver (if upload is not skipped):**
    *   The `MockReceiverManager` context manager is entered.
    *   `docker-compose up -d --build mock_receiver` starts the receiver in the background. A short pause allows for initialization. The manager verifies the container is running.
3.  **Core Workflow (`perform_core_workflow` function):**
    *   **Set CWD:** The current working directory is changed to `script_dir` (where `docker-compose.yml` is located) to ensure correct path resolution for Docker Compose.
    *   **Run Joern & PMD (if not skipped):**
        *   `run_analysis_containers` executes `docker-compose up ... joern lint`.
        *   This runs the Joern and PMD services sequentially (due to implicit or explicit dependencies if PMD `depends_on` Joern).
        *   The orchestrator waits for `lint` to finish and uses its exit code.
        *   Output files (`export.json`, `pmd_report.json`) are expected in `./exporter/export/cpg_all/` and `./exporter/export/lint/` respectively on the host.
        *   The success of this step is verified.
    *   **Merge Reports:**
        *   `run_merge_script` calls `merge_tool.py`.
        *   `merge_tool.py` reads the Joern and PMD outputs, performs the merge logic (including path transformation and `pmd_violations` injection), and writes `merged_graph.json` to `./exporter/export/`.
        *   The success of this step is verified.
    *   **Send Data (if not skipped and `MockReceiverManager` is active):**
        *   `send_data` POSTs `merged_graph.json` to the `--target-url` (which defaults to the `mock_receiver` at `http://localhost:5001/api/upload-graph`).
        *   The success of this step is verified.
    *   **Restore CWD:** The original CWD is restored.
4.  **Mock Receiver Shutdown (if started):**
    *   The `MockReceiverManager` `__exit__` method is called automatically.
    *   `docker-compose stop mock_receiver` and `docker-compose rm -f mock_receiver` stop and remove the receiver container.
5.  **Completion:** The script prints a final success message or exits with an error code if any step failed.

## 5. Key Assumptions and Configuration Points

*   **Java Project Location:** The script assumes the Java project to be analyzed is accessible at the path specified by `--java-project-dir` (default `../project` relative to `exporter/`).
*   **Joern & PMD Output Locations:** The `docker-compose.yml` and `orchestrate.py` expect Joern and PMD outputs in specific subdirectories of `./exporter/export/`.
*   **Path Transformation in `merge_tool.py`:** The logic to map Joern's `.class` file paths to PMD's `.java` source file paths includes a hardcoded base path (`/sources/src/main/java/`). This might need adjustment if the Java project structure is different or if PMD reports paths relative to a different root within the `/sources` mount.
*   **Joern GraphSON Default Filename:** The scripts assume that when `joern-export --format=graphson --out=/some/dir` is used, Joern creates a file named `export.json` inside `/some/dir`. If this default changes, `EXPECTED_JOERN_OUT_FILE` in `docker-compose.yml` (joern service) would need an update.
*   **Docker and Docker Compose:** Must be installed and runnable by the user executing `orchestrate.py`.

## 6. Running the Module

1.  Ensure Python (3.x) and `pip` are installed.
2.  Navigate to the `exporter/` directory.
3.  (Recommended) Create and activate a Python virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # or .\.venv\Scripts\activate.bat on Windows
    ```
4.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5.  Ensure Docker and Docker Compose are running.
6.  Place the target Java project in the `../project/` directory (or specify its location with `--java-project-dir`).
7.  Execute the orchestrator:
    ```bash
    python orchestrate.py
    ```
    You can use various command-line arguments to customize its behavior (see `python orchestrate.py --help`).

This documentation should provide a comprehensive understanding of the `exporter` module's functionality and design.