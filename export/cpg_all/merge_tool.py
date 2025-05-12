import json
import os

# --- Configuration ---
PMD_REPORT_PATH = "pmd_report.json"
JOERN_EXPORT_PATH = "export.json"
MERGED_OUTPUT_PATH = "merged_graph.json"

# --- Helper Functions ---
def normalize_path(path_str):
    """
    Normalizes a path string:
    1. Replaces backslashes with forward slashes.
    2. Converts to lowercase (optional, but good for robust matching if case might differ).
    3. Uses os.path.normpath to canonicalize (e.g., resolve '..').
    """
    if path_str is None:
        return None
    path_str = path_str.replace("\\", "/")
    # For this specific problem, lowercase might be too aggressive if Joern/PMD are case-sensitive
    # But if there's a chance of case mismatch, uncomment:
    # path_str = path_str.lower()
    return os.path.normpath(path_str)

# --- Main Script ---
def merge_reports():
    print(f"Starting merge process...")
    print(f"Loading PMD report from: {PMD_REPORT_PATH}")
    try:
        with open(PMD_REPORT_PATH, 'r') as f:
            pmd_data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: PMD report file not found at {PMD_REPORT_PATH}")
        print("Ensure 'pmd_report.json' exists in the same directory as the script.")
        return
    except json.JSONDecodeError as e:
        print(f"ERROR: Could not decode JSON from PMD report at {PMD_REPORT_PATH}: {e}")
        return

    print(f"Loading Joern GraphSON export from: {JOERN_EXPORT_PATH}")
    try:
        with open(JOERN_EXPORT_PATH, 'r') as f:
            joern_graph_data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Joern export file not found at {JOERN_EXPORT_PATH}")
        print("Ensure 'export.json' exists in the same directory as the script.")
        return
    except json.JSONDecodeError as e:
        print(f"ERROR: Could not decode JSON from Joern export at {JOERN_EXPORT_PATH}: {e}")
        return

    # 1. Process PMD data into a dictionary for easy lookup
    # Key: normalized filename, Value: list of violations
    pmd_violations_map = {}
    pmd_file_count = 0
    if "files" in pmd_data:
        for file_report in pmd_data.get("files", []):
            original_filename = file_report.get("filename")
            if not original_filename:
                print(f"Warning: PMD file report found without a 'filename' field. Skipping.")
                continue

            normalized_filename = normalize_path(original_filename)
            violations = file_report.get("violations", [])

            if normalized_filename in pmd_violations_map:
                # This case shouldn't happen with standard PMD output but good to handle
                pmd_violations_map[normalized_filename].extend(violations)
            else:
                pmd_violations_map[normalized_filename] = violations
            pmd_file_count += 1
        print(f"Processed {pmd_file_count} file entries from PMD report.")
    else:
        print("Warning: 'files' key not found in PMD report. No PMD violations to merge.")
        # Decide if you want to stop or proceed without PMD data
        # return # Uncomment to stop if PMD data is essential

    # 2. Iterate through Joern graph vertices and merge
    if "graph" not in joern_graph_data or "vertices" not in joern_graph_data["graph"]:
        print("ERROR: Joern graph data is not in the expected format (missing 'graph' or 'graph.vertices').")
        return

    vertices = joern_graph_data["graph"]["vertices"]
    matched_pmd_files = set()
    joern_file_nodes_found = 0
    joern_file_nodes_matched = 0

    for vertex in vertices:
        if vertex.get("label") == "FILE":
            joern_file_nodes_found += 1
            properties = vertex.get("properties", {})
            name_prop = properties.get("NAME", {})

            # The NAME property contains an object with "@type" and "@value" (which is a list)
            if isinstance(name_prop, dict) and "@value" in name_prop and isinstance(name_prop["@value"], list) and len(name_prop["@value"]) > 0:
                joern_filepath_original = name_prop["@value"][0]
                joern_filepath_normalized = normalize_path(joern_filepath_original)

                if joern_filepath_normalized in pmd_violations_map:
                    print(f"  Match found: Joern FILE '{joern_filepath_original}' <-> PMD file.")
                    # Ensure 'properties' exists if it didn't
                    if "properties" not in vertex:
                        vertex["properties"] = {}

                    # Add or update the pmd_violations property
                    vertex["properties"]["pmd_violations"] = pmd_violations_map[joern_filepath_normalized]
                    matched_pmd_files.add(joern_filepath_normalized)
                    joern_file_nodes_matched += 1
                else:
                    # Optional: Add an empty list if you always want the property present
                    # if "properties" not in vertex:
                    #     vertex["properties"] = {}
                    # vertex["properties"]["pmd_violations"] = []
                    pass # No action needed if no match and you don't want an empty list

            else:
                print(f"Warning: Joern FILE node (ID: {vertex.get('_id', 'N/A')}) found without a valid NAME property. Skipping.")


    print(f"\n--- Merge Summary ---")
    print(f"Total Joern FILE nodes found: {joern_file_nodes_found}")
    print(f"Joern FILE nodes matched with PMD data: {joern_file_nodes_matched}")

    # 3. Report PMD files that couldn't be matched
    unmatched_pmd_files_count = 0
    if pmd_file_count > 0: # Only report if there was PMD data to begin with
        print("\nPMD File Match Report:")
        all_pmd_files_in_report = set(pmd_violations_map.keys())
        unmatched_pmd_files = all_pmd_files_in_report - matched_pmd_files

        if not unmatched_pmd_files:
            print("  All PMD files with violations were successfully matched and merged!")
        else:
            unmatched_pmd_files_count = len(unmatched_pmd_files)
            for pmd_filename_normalized in unmatched_pmd_files:
                # Try to find the original filename for better reporting
                original_unmatched_path = "Unknown (normalized only)"
                for file_report in pmd_data.get("files", []):
                    if normalize_path(file_report.get("filename")) == pmd_filename_normalized:
                        original_unmatched_path = file_report.get("filename")
                        break
                print(f"  - Unmatched PMD file: '{original_unmatched_path}' (normalized: '{pmd_filename_normalized}')")
                print(f"    Reason: No corresponding FILE node found in Joern's GraphSON with this path.")
            print(f"  Total {unmatched_pmd_files_count} PMD file(s) could not be matched.")


    # 4. Save the merged graph
    try:
        with open(MERGED_OUTPUT_PATH, 'w') as f:
            json.dump(joern_graph_data, f, indent=2) # indent for readability
        print(f"\nSuccessfully merged data saved to: {MERGED_OUTPUT_PATH}")
    except IOError as e:
        print(f"ERROR: Could not write merged data to {MERGED_OUTPUT_PATH}: {e}")

    # 5. Confirm number of PMD files merged
    print(f"\nConfirmation: {len(matched_pmd_files)} unique PMD file paths had their violations merged into Joern FILE nodes.")
    if pmd_file_count > 0:
        if len(matched_pmd_files) == pmd_file_count:
            print(f"All {pmd_file_count} files listed in the PMD report were processed. Violations (if any) were merged into corresponding Joern FILE nodes.")
        else:
            print(f"Note: {len(matched_pmd_files)} out of {pmd_file_count} PMD files listed in the report had matching Joern FILE nodes and were merged. See unmatched report above.")


if __name__ == "__main__":
    # --- Dummy file creation removed ---
    # The script will now expect pmd_report.json and export.json
    # to already exist in the same directory.

    print("Attempting to merge existing 'pmd_report.json' and 'export.json'...")
    merge_reports()