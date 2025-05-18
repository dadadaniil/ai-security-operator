import java.io.File;
import java.io.IOException;
import java.util.*;

public class TestsValidator {
    private static final Map<String, String> extensionToScript = new HashMap<>();

    static {
        extensionToScript.put("py", "validate_python.sh");
        extensionToScript.put("c", "validate_c.sh");
        extensionToScript.put("cs", "validate_csharp.sh");
        extensionToScript.put("java", "validate_java.sh");
        extensionToScript.put("js", "validate_js.sh");
        extensionToScript.put("json", "validate_json.sh");
    }

    public static void main(String[] args) {
        if (args.length == 0) {
            System.out.println("Usage: java Validator <file1> <file2> ...");
            return;
        }

        Map<String, List<String>> filesByExt = new HashMap<>();

        for (String filePath : args) {
            File file = new File(filePath);
            String ext = getExtension(file.getName());
            if (ext != null && extensionToScript.containsKey(ext)) {
                filesByExt.computeIfAbsent(ext, k -> new ArrayList<>()).add(filePath);
            } else {
                System.out.println("Unsupported file: " + filePath);
            }
        }

        for (String ext : filesByExt.keySet()) {
            String script = "./" + extensionToScript.get(ext);
            List<String> files = filesByExt.get(ext);
            List<String> cmd = new ArrayList<>();
            cmd.add(script);
            cmd.addAll(files);

            try {
                ProcessBuilder pb = new ProcessBuilder(cmd);
                pb.inheritIO();
                Process proc = pb.start();
                int code = proc.waitFor();
                if (code != 0) {
                    System.out.println("Validation failed for ." + ext + " files.");
                    return;
                }
            } catch (IOException | InterruptedException e) {
                System.err.println("Error running script for ." + ext + ": " + e.getMessage());
            }
        }

        System.out.println("All files validated successfully.");
    }

    private static String getExtension(String filename) {
        int idx = filename.lastIndexOf('.');
        return (idx > 0) ? filename.substring(idx + 1).toLowerCase() : null;
    }
}
