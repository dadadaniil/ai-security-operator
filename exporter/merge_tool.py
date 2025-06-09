import json
import os
import argparse
import sys


def normalize_path(path_str):
    """Normalize file paths to use forward slashes and OS-normalized separators."""
    if path_str is None:
        return None
    path_str = path_str.replace("\\", "/")
    return os.path.normpath(path_str)


def merge_reports(pmd_report_path, joern_export_path, merged_output_path):
    print(f"Starting merge process...")

    print(f"Loading PMD report from: {pmd_report_path}")
    try:
        with open(pmd_report_path, 'r', encoding='utf-8') as f:
            pmd_data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: PMD report file not found at {pmd_report_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"ERROR: Could not decode JSON from PMD report at {pmd_report_path}: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error loading PMD report {pmd_report_path}: {e}")
        return False

    print(f"Loading Joern GraphSON export from: {joern_export_path}")
    raw_joern_data = None
    try:
        with open(joern_export_path, 'r', encoding='utf-8') as f:
            raw_joern_data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Joern export file not found at {joern_export_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"ERROR: Could not decode JSON from Joern export at {joern_export_path}: {e}")
        try:
            with open(joern_export_path, 'r', encoding='utf-8') as f_err:
                print(f"--- Start of Joern file content (first 500 chars) ---")
                print(f_err.read(500))
                print(f"--- End of Joern file content snippet ---")
        except Exception as read_err:
            print(f"Could not read Joern file for debugging: {read_err}")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error loading Joern export {joern_export_path}: {e}")
        return False

    joern_graph_components = None

    if isinstance(raw_joern_data, dict) and \
            raw_joern_data.get("@type") == "tinker:graph" and \
            "@value" in raw_joern_data and \
            isinstance(raw_joern_data["@value"], dict):

        print("INFO: Detected TinkerPop 'tinker:graph' wrapper. Extracting graph components from '@value'.")
        joern_graph_components = raw_joern_data["@value"]

    elif isinstance(raw_joern_data, dict) and "graph" in raw_joern_data and isinstance(raw_joern_data["graph"], dict):
        print("INFO: Assuming loaded Joern data has a top-level 'graph' key.")
        joern_graph_components = raw_joern_data["graph"]

    else:
        print(f"ERROR: Joern data from {joern_export_path} is not in a recognized GraphSON format.")
        print(
            f"Top-level keys found: {list(raw_joern_data.keys()) if isinstance(raw_joern_data, dict) else 'Not a dictionary'}")
        print(f"Raw data type: {type(raw_joern_data)}")
        return False

    if not isinstance(joern_graph_components, dict):
        print(f"ERROR: Processed Joern graph components data is not a dictionary.")
        return False

    if "vertices" not in joern_graph_components or not isinstance(joern_graph_components.get("vertices"), list):
        print("ERROR: Joern graph data is missing 'vertices' list or it's not a list.")
        print(f"Keys found in processed Joern graph components: {list(joern_graph_components.keys())}")
        return False

    pmd_violations_map = {}
    pmd_file_count = 0
    if "files" in pmd_data and isinstance(pmd_data.get("files"), list):
        for file_report in pmd_data.get("files", []):
            original_filename = file_report.get("filename")
            if not original_filename:
                print(f"Warning: PMD file report found without a 'filename' field. Skipping.")
                continue

            normalized_filename = normalize_path(original_filename)
            violations = file_report.get("violations", [])

            if normalized_filename not in pmd_violations_map:
                pmd_violations_map[normalized_filename] = []
            if isinstance(violations, list):
                pmd_violations_map[normalized_filename].extend(violations)
            else:
                print(
                    f"Warning: PMD violations for '{original_filename}' is not a list. Skipping violations for this file.")

            pmd_file_count += 1
        print(f"Processed {pmd_file_count} file entries from PMD report.")
    else:
        print("Warning: 'files' key not found or not a list in PMD report. No PMD violations to merge.")

    # --- Iterate Joern Graph Vertices and Merge ---
    vertices = joern_graph_components["vertices"]
    matched_pmd_files = set()
    joern_file_nodes_found = 0
    joern_file_nodes_matched = 0
    processed_pmd_files_for_reporting = set(pmd_violations_map.keys())

    for vertex in vertices:
        if not isinstance(vertex, dict):
            print(f"Warning: Found a non-dictionary item in Joern vertices list. Skipping: {vertex}")
            continue

        if vertex.get("label") == "FILE":
            joern_file_nodes_found += 1
            properties = vertex.get("properties", {})
            if not isinstance(properties, dict):
                print(
                    f"Warning: FILE node (ID: {vertex.get('id', 'N/A')}) has 'properties' not as a dictionary. Skipping properties.")
                continue

            name_prop_wrapper = properties.get("NAME", {})
            joern_filepath_original = None
            if isinstance(name_prop_wrapper, dict) and \
                    name_prop_wrapper.get("@type") == "g:VertexProperty" and \
                    "@value" in name_prop_wrapper and \
                    isinstance(name_prop_wrapper["@value"], dict) and \
                    name_prop_wrapper["@value"].get("@type") == "g:List" and \
                    "@value" in name_prop_wrapper["@value"] and \
                    isinstance(name_prop_wrapper["@value"]["@value"], list) and \
                    len(name_prop_wrapper["@value"]["@value"]) > 0 and \
                    isinstance(name_prop_wrapper["@value"]["@value"][0], str):
                joern_filepath_original = name_prop_wrapper["@value"]["@value"][0]

            if joern_filepath_original:
                joern_path_for_matching = joern_filepath_original

                if joern_path_for_matching == "<unknown>":
                    continue

                if ".class" in joern_path_for_matching:
                    if "/tmp/" in joern_path_for_matching and "jimple2cpg" in joern_path_for_matching:
                        # Try to find the start of the package structure (e.g., "org/", "com/")
                        package_start_index = -1
                        for pkg_root in ["org/", "com/", "net/", "io/"]:  # Add other common roots
                            idx = joern_path_for_matching.rfind(pkg_root)
                            if idx != -1:
                                # Check if this is not part of a longer word like "sourceforge"
                                if idx == 0 or joern_path_for_matching[idx - 1] == '/':
                                    package_start_index = idx
                                    break
                        if package_start_index != -1:
                            relative_path = joern_path_for_matching[package_start_index:]
                            # PMD reports paths relative to /sources (which is project root)
                            # Assuming standard Maven structure src/main/java
                            pmd_like_base = "/sources/src/main/java/"
                            joern_path_for_matching = pmd_like_base + relative_path
                        else:
                            print(
                                f"DEBUG: Could not determine relative path for Joern .class file: {joern_filepath_original}")

                    joern_path_for_matching = joern_path_for_matching.replace(".class", ".java")

                joern_filepath_normalized = normalize_path(joern_path_for_matching)

                if joern_filepath_normalized in pmd_violations_map:
                    print(
                        f"  MATCH FOUND: Joern (orig: '{joern_filepath_original}', match_as: '{joern_path_for_matching}') "
                        f"<-> PMD file.")
                    vertex["properties"]["pmd_violations"] = pmd_violations_map[joern_filepath_normalized]
                    matched_pmd_files.add(joern_filepath_normalized)
                    joern_file_nodes_matched += 1
            else:
                vertex_id_repr = vertex.get('id', 'N/A')
                if isinstance(vertex_id_repr, dict):
                    vertex_id_repr = vertex_id_repr.get('@value', 'N/A_dict')
                print(
                    f"Warning: Joern FILE node (ID: {vertex_id_repr}) could not extract a valid original path string. NAME property: {name_prop_wrapper}")

    print(f"\n--- Merge Summary ---")
    print(f"Total Joern FILE nodes found: {joern_file_nodes_found}")
    print(f"Joern FILE nodes matched with PMD data: {joern_file_nodes_matched}")

    unmatched_pmd_files_count = 0
    print("\nPMD File Match Report:")
    if not processed_pmd_files_for_reporting:
        print("  No files were processed from the PMD report.")
    else:
        for pmd_filename_normalized in processed_pmd_files_for_reporting:
            if pmd_filename_normalized not in matched_pmd_files:
                unmatched_pmd_files_count += 1
                original_unmatched_path = "Unknown (normalized only)"
                if "files" in pmd_data and isinstance(pmd_data.get("files"), list):
                    for file_report in pmd_data.get("files", []):
                        if normalize_path(file_report.get("filename")) == pmd_filename_normalized:
                            original_unmatched_path = file_report.get("filename")
                            break
                print(f"  - Unmatched PMD file: '{original_unmatched_path}' (normalized: '{pmd_filename_normalized}')")
                print(
                    f"    Reason: No corresponding Joern FILE node (after path transformation) matched this PMD path.")

        if unmatched_pmd_files_count == 0 and pmd_file_count > 0:
            print("  All files listed in PMD report were matched/accounted for in Joern FILE nodes!")
        elif pmd_file_count == 0:
            print("  No files in PMD report to match.")
        else:
            print(f"  Total {unmatched_pmd_files_count} PMD file path(s) could not be matched to a Joern FILE node.")

    # --- Save Merged Graph ---
    data_to_save = None
    if isinstance(raw_joern_data, dict) and raw_joern_data.get("@type") == "tinker:graph":
        raw_joern_data["@value"] = joern_graph_components
        data_to_save = raw_joern_data
        print("INFO: Re-wrapping modified graph components into 'tinker:graph' structure for saving.")
    elif isinstance(raw_joern_data, dict) and "graph" in raw_joern_data:
        raw_joern_data["graph"] = joern_graph_components
        data_to_save = raw_joern_data
        print("INFO: Re-inserting modified graph components into original 'graph' structure for saving.")
    else:
        print("ERROR: Cannot determine original Joern data structure for saving. Saving processed components directly.")
        data_to_save = joern_graph_components

    try:
        output_dir = os.path.dirname(merged_output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        with open(merged_output_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=2)
        print(f"\nSuccessfully merged data saved to: {merged_output_path}")
        return True
    except IOError as e:
        print(f"ERROR: Could not write merged data to {merged_output_path}: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during saving merged file: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge PMD JSON report into Joern GraphSON.")
    parser.add_argument("--pmd-input", required=True, help="Path to the PMD JSON report file.")
    parser.add_argument("--joern-input", required=True, help="Path to the Joern GraphSON export file.")
    parser.add_argument("--output", required=True, help="Path for the merged GraphSON output file.")
    args = parser.parse_args()

    if merge_reports(args.pmd_input, args.joern_input, args.output):
        print("Merge script finished successfully.")
        sys.exit(0)
    else:
        print("Merge script failed.")
        sys.exit(1)
