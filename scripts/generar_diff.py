import sys
import os

def make_diff(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    diff_lines = []
    diff_lines.append(f"--- /dev/null\n")
    diff_lines.append(f"+++ b/{os.path.basename(file_path)}\n")
    diff_lines.append("@@ -0,0 +1,1000 @@\n")
    for line in content.splitlines():
        diff_lines.append(f"+{line}\n")
    return "".join(diff_lines)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python generar_diff.py <path_de_entrada> <path_de_salida_diff>")
        sys.exit(1)
    
    diff_content = make_diff(sys.argv[1])
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(diff_content)
    print(f"Diff generado en {sys.argv[2]} para el archivo {sys.argv[1]}")
