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
        return
    except json.JSONDecodeError:
        print(f"ERROR: Could not decode JSON from PMD report at {PMD_REPORT_PATH}")
        return

    print(f"Loading Joern GraphSON export from: {JOERN_EXPORT_PATH}")
    try:
        with open(JOERN_EXPORT_PATH, 'r') as f:
            joern_graph_data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Joern export file not found at {JOERN_EXPORT_PATH}")
        return
    except json.JSONDecodeError:
        print(f"ERROR: Could not decode JSON from Joern export at {JOERN_EXPORT_PATH}")
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
        return # Or proceed without PMD data if that's desired

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

                    vertex["properties"]["pmd_violations"] = pmd_violations_map[joern_filepath_normalized]
                    matched_pmd_files.add(joern_filepath_normalized)
                    joern_file_nodes_matched += 1
                else:
                    # This Joern file node had no corresponding PMD entry
                    # print(f"  Info: Joern FILE node '{joern_filepath_original}' has no PMD violations listed in the report.")
                    pass # No action needed if no match
            else:
                print(f"Warning: Joern FILE node (ID: {vertex.get('id', 'N/A')}) found without a valid NAME property. Skipping.")

    print(f"\n--- Merge Summary ---")
    print(f"Total Joern FILE nodes found: {joern_file_nodes_found}")
    print(f"Joern FILE nodes matched with PMD data: {joern_file_nodes_matched}")

    # 3. Report PMD files that couldn't be matched
    unmatched_pmd_files_count = 0
    if pmd_file_count > 0: # Only report if there was PMD data to begin with
        print("\nPMD File Match Report:")
        for pmd_filename_normalized, violations in pmd_violations_map.items():
            if pmd_filename_normalized not in matched_pmd_files:
                unmatched_pmd_files_count += 1
                # Try to find the original filename for better reporting
                original_unmatched_path = "Unknown (normalized only)"
                for file_report in pmd_data.get("files", []):
                    if normalize_path(file_report.get("filename")) == pmd_filename_normalized:
                        original_unmatched_path = file_report.get("filename")
                        break
                print(f"  - Unmatched PMD file: '{original_unmatched_path}' (normalized: '{pmd_filename_normalized}')")
                print(f"    Reason: No corresponding FILE node found in Joern's GraphSON with this path.")

        if unmatched_pmd_files_count == 0:
            print("  All PMD files with violations were successfully matched and merged!")
        else:
            print(f"  Total {unmatched_pmd_files_count} PMD file(s) could not be matched.")

    # 4. Save the merged graph
    try:
        with open(MERGED_OUTPUT_PATH, 'w') as f:
            json.dump(joern_graph_data, f, indent=2) # indent for readability
        print(f"\nSuccessfully merged data saved to: {MERGED_OUTPUT_PATH}")
    except IOError:
        print(f"ERROR: Could not write merged data to {MERGED_OUTPUT_PATH}")

    # 5. Confirm number of PMD files merged
    # This implicitly refers to the number of PMD *entries* that found a match in Joern.
    # The prompt wording "Confirm all 4 files from PMD were properly merged" likely means
    # that for each of the 4 files PMD reported, their violations were added to a Joern node.
    print(f"\nConfirmation: {len(matched_pmd_files)} unique PMD file paths had their violations merged into Joern FILE nodes.")
    if pmd_file_count > 0:
        if len(matched_pmd_files) == pmd_file_count:
            print(f"All {pmd_file_count} files from PMD report were processed and their violations (if any) merged into corresponding Joern FILE nodes.")
        else:
            print(f"Note: {len(matched_pmd_files)} out of {pmd_file_count} PMD files were merged. See unmatched report above.")

if __name__ == "__main__":
    # --- Create dummy input files for testing ---
    # This part is just for self-contained testing.
    # In a real scenario, these files would be generated by PMD and Joern.

    # Dummy pmd_report.json
    dummy_pmd_data = {
        "formatVersion": 0,
        "pmdVersion": "6.55.0",
        "timestamp": "2023-10-27T10:00:00.000Z",
        "files": [
            {
                "filename": "/project/src/main/java/org/example/Purchase.java",
                "violations": [
                    {"beginline": 10, "endline": 10, "begincolumn": 8, "endcolumn": 15, "description": "Avoid using 'var'", "rule": "AvoidVarType", "ruleset": "Best Practices", "priority": 3}
                ]
            },
            {
                "filename": "/project/src/main/java/org/example/Main.java",
                "violations": [
                    {"beginline": 5, "endline": 5, "begincolumn": 1, "endcolumn": 50, "description": "System.out.println is used", "rule": "SystemPrintln", "ruleset": "Best Practices", "priority": 3},
                    {"beginline": 12, "endline": 12, "begincolumn": 1, "endcolumn": 20, "description": "Unused local variable 'x'", "rule": "UnusedLocalVariable", "ruleset": "Best Practices", "priority": 3}
                ]
            },
            {
                "filename": "/project/src/main/java/org/example/Unused.java", # This one won't be in Joern
                "violations": [
                    {"beginline": 3, "endline": 3, "begincolumn": 1, "endcolumn": 10, "description": "Empty method", "rule": "EmptyMethod", "ruleset": "Best Practices", "priority": 3}
                ]
            },
            {
                "filename": "/project/src/main/java/org/example/NoViolationsInPMD.java", # In Joern, but no PMD violations
                "violations": []
            }
        ],
        "suppressedViolations": [],
        "processingErrors": [],
        "configurationErrors": []
    }
    with open(PMD_REPORT_PATH, 'w') as f:
        json.dump(dummy_pmd_data, f, indent=2)

    # Dummy export.json (GraphSON)
    dummy_joern_data = {
        "graph": {
            "vertices": [
                {
                    "id": "0",
                    "label": "METHOD",
                    "properties": {"NAME": {"@type": "g:VertexProperty", "@value": ["<init>"]}}
                },
                {
                    "id": "1",
                    "label": "FILE",
                    "properties": {
                        "NAME": {"@type": "g:VertexProperty", "@value": ["/project/src/main/java/org/example/Purchase.java"]},
                        "CONTENT": {"@type": "g:VertexProperty", "@value": ["package org.example; ..."]}
                    }
                },
                {
                    "id": "2",
                    "label": "FILE",
                    "properties": {
                        "NAME": {"@type": "g:VertexProperty", "@value": ["/project/src/main/java/org/example/Main.java"]},
                        "CONTENT": {"@type": "g:VertexProperty", "@value": ["package org.example; public class Main ..."]}
                    }
                },
                {
                    "id": "3",
                    "label": "NAMESPACE_BLOCK",
                    "properties": {"NAME": {"@type": "g:VertexProperty", "@value": ["org.example"]}}
                },
                {
                    "id": "4", # A file that PMD has no violations for (empty violations array)
                    "label": "FILE",
                    "properties": {
                        "NAME": {"@type": "g:VertexProperty", "@value": ["/project/src/main/java/org/example/NoViolationsInPMD.java"]},
                        "CONTENT": {"@type": "g:VertexProperty", "@value": ["package org.example; ..."]}
                    }
                },
                {
                    "id": "5", # A file that PMD doesn't know about
                    "label": "FILE",
                    "properties": {
                        "NAME": {"@type": "g:VertexProperty", "@value": ["/project/src/test/java/org/example/Test.java"]}, # Different path
                        "CONTENT": {"@type": "g:VertexProperty", "@value": ["package org.example; ..."]}
                    }
                }
            ],
            "edges": [] # Edges not relevant for this task but part of GraphSON
        }
    }
    with open(JOERN_EXPORT_PATH, 'w') as f:
        json.dump(dummy_joern_data, f, indent=2)

    print("Dummy input files created.\n")
    # --- End of dummy file creation ---

    merge_reports()