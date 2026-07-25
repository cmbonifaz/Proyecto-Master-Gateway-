import sys
import os
import ast
import re

# Asegurar UTF-8 en stdout para compatibilidad con emojis en Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import joblib
import numpy as np
from scipy.sparse import hstack
from typing import Dict, List

# =============================================================================
# RE-IMPLEMENTACIÓN DEL ASTFeatureExtractor
# (Extraído de la Fase 1 para mantener el script autocontenido)
# VERSIÓN 2.0 — Soporte para Cat. 1-6 de vulnerabilidades
# =============================================================================

# Patrones de nombres de variables que indican secretos hardcodeados.
# Se usarán en visit_Assign para detectar credenciales en el código fuente.
_SECRET_NAME_PATTERNS = re.compile(
    r"(secret|api[_\-]?key|password|passwd|token|credential|auth[_\-]?key|"
    r"private[_\-]?key|access[_\-]?key|llave[_\-]?api|contrasena|clave)",
    re.IGNORECASE,
)

# Regex para detectar strings que parecen secretos reales (no placeholders)
_SECRET_VALUE_PATTERN = re.compile(
    r"(AIza[A-Za-z0-9_\-]{20,}|"          # Google API key
    r"sk-[A-Za-z0-9]{20,}|"               # OpenAI key
    r"ghp_[A-Za-z0-9]{20,}|"             # GitHub token
    r"[A-Za-z0-9+/]{20,}={0,2}|"         # Base64-like
    r"[A-Fa-f0-9]{32,})"                  # Hex secrets (MD5/SHA hashes como clave)
)


class ASTFeatureExtractor(ast.NodeVisitor):
    """
    Extractor de features de seguridad del AST de Python.
    Versión 2.0: detecta Cat. 1–6 de vulnerabilidades.

    Categorías detectadas:
      Cat. 1 — SQL Injection: string concat + keywords SQL
      Cat. 2 — Command Injection: eval, exec, os.system, subprocess
      Cat. 3 — Deserialización insegura: pickle.loads, yaml.load
      Cat. 4 — Path Traversal: open(concat), os.path.join(concat)
      Cat. 5 — Hardcoded secrets: vars con nombre SECRET/KEY/etc. + valor literal
               Criptografía débil: hashlib.md5, hashlib.sha1
      Cat. 6 — XSS: string concat con tags HTML
               SSRF: requests.get/post/put con variable
    """

    # ── FUNCIONES PELIGROSAS SIMPLES (ast.Name) ───────────────────────────────
    # Detecta cuando se llama directamente (ej: from pickle import loads; loads(data))
    _SIMPLE_DANGEROUS: set = {
        "eval",       # Cat. 2 — Code injection
        "exec",       # Cat. 2 — Code injection
        "loads",      # Cat. 3 — pickle.loads / yaml.load importado directamente
        "load",       # Cat. 3 — yaml.load importado directamente
        "system",     # Cat. 2 — os.system importado directamente
        "Popen",      # Cat. 2 — subprocess.Popen importado directamente
        "call",       # Cat. 2 — subprocess.call importado directamente
    }

    # ── FUNCIONES PELIGROSAS COMPUESTAS (module.func) — ast.Attribute ─────────
    _COMPOUND_DANGEROUS: set = {
        # Cat. 2 — Command Injection
        ("subprocess", "Popen"),
        ("subprocess", "call"),
        ("subprocess", "run"),
        ("os", "system"),
        ("os", "popen"),
        ("os", "execv"),
        ("os", "execve"),
        ("commands", "getoutput"),
        # Cat. 3 — Deserialización insegura
        ("pickle", "loads"),
        ("pickle", "load"),
        ("yaml", "load"),           # yaml.load SIN SafeLoader es RCE
        ("marshal", "loads"),
        ("marshal", "load"),
        # Cat. 5 — Criptografía débil
        ("hashlib", "md5"),
        ("hashlib", "sha1"),
        ("hashlib", "new"),         # hashlib.new('md5', ...) también es débil
        # Cat. 6 — SSRF
        ("requests", "get"),
        ("requests", "post"),
        ("requests", "put"),
        ("requests", "delete"),
        ("requests", "request"),
        ("urllib", "urlopen"),
        ("urllib2", "urlopen"),
        ("httpx", "get"),
        ("httpx", "post"),
    }

    # ── ATRIBUTOS PELIGROSOS (cualquier módulo) ────────────────────────────────
    _DANGEROUS_ATTRS: set = {
        "system", "Popen", "popen", "execv", "execve",  # Cat. 2
        "loads", "load",                                  # Cat. 3
        "md5", "sha1",                                    # Cat. 5 (crypto débil)
    }

    def __init__(self):
        self._reset()

    def _reset(self):
        self.ast_depth: int = 0
        self.dangerous_func_count: int = 0
        self.total_calls: int = 0
        self.num_imports: int = 0
        self.has_string_concat: int = 0
        self.num_exception_handlers: int = 0
        self.has_hardcoded_secret: int = 0      # Cat. 5 — nuevo feature
        self.found_dangerous_details: List[str] = []
        self.vulnerability_categories: List[str] = []  # Categorías detectadas

    def _compute_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        max_depth = current_depth
        for child in ast.iter_child_nodes(node):
            child_depth = self._compute_depth(child, current_depth + 1)
            max_depth = max(max_depth, child_depth)
        return max_depth

    def visit_Call(self, node: ast.Call):
        self.total_calls += 1

        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in self._SIMPLE_DANGEROUS:
                self.dangerous_func_count += 1
                lineno = getattr(node, "lineno", "?")
                detail = f"{func_name}() (línea ~{lineno})"
                self.found_dangerous_details.append(detail)
                self._classify_simple(func_name, lineno)
            elif func_name == "open":
                # Cat. 4 — Path Traversal (ruta dinámica)
                if node.args and not isinstance(node.args[0], ast.Constant):
                    self.dangerous_func_count += 1
                    lineno = getattr(node, "lineno", "?")
                    detail = f"open() con ruta dinámica (línea ~{lineno})"
                    self.found_dangerous_details.append(detail)

        elif isinstance(node.func, ast.Attribute):
            attr = node.func.attr

            # Intentar obtener el nombre del módulo/objeto llamante
            module_name = None
            if isinstance(node.func.value, ast.Name):
                module_name = node.func.value.id
            elif isinstance(node.func.value, ast.Attribute):
                # Maneja casos como os.path.join o urllib.request.urlopen
                module_name = node.func.value.attr

            lineno = getattr(node, "lineno", "?")

            # Verificar en _COMPOUND_DANGEROUS
            if module_name and (module_name, attr) in self._COMPOUND_DANGEROUS:
                # FIX: subprocess.run/call/Popen sin shell=True es seguro.
                # Verificamos ANTES de contar para evitar falsos positivos.
                if module_name == "subprocess" and attr in {"run", "call", "Popen"}:
                    shell_kwarg = next(
                        (kw for kw in node.keywords if kw.arg == "shell"), None
                    )
                    shell_is_true = (
                        shell_kwarg is not None and
                        isinstance(shell_kwarg.value, ast.Constant) and
                        shell_kwarg.value.value is True
                    )
                    if not shell_is_true:
                        self.generic_visit(node)
                        return  # shell=False o no especificado → seguro, ignorar
                elif module_name in {"requests", "httpx", "urllib", "urllib2"} and attr in {"get", "post", "put", "delete", "request", "urlopen"}:
                    url_arg = None
                    if node.args:
                        url_arg = node.args[0]
                    else:
                        url_arg = next((kw.value for kw in node.keywords if kw.arg == "url"), None)
                    if url_arg and isinstance(url_arg, ast.Constant):
                        self.generic_visit(node)
                        return  # URL estática → segura, ignorar

                self.dangerous_func_count += 1
                detail = f"{module_name}.{attr}() (línea ~{lineno})"
                self.found_dangerous_details.append(detail)
                self._classify_compound(module_name, attr, lineno, node)
            elif attr in self._DANGEROUS_ATTRS:
                # Excluir json.load/loads — JSON no ejecuta código arbitrario (no RCE)
                if attr in {"load", "loads"} and module_name == "json":
                    pass  # json.load() es seguro, no marcar
                else:
                    # Detecta alias: o.system(), obj.loads(), etc.
                    self.dangerous_func_count += 1
                    detail = f"(alias).{attr}() (línea ~{lineno})"
                    self.found_dangerous_details.append(detail)
                    self._classify_attr(attr, lineno)
            elif attr == "format":
                self.has_string_concat = 1

        self.generic_visit(node)

    def _classify_simple(self, func_name: str, lineno):
        """Clasifica la categoría de vulnerabilidad para funciones simples."""
        cat2 = {"eval", "exec", "system", "Popen", "call"}
        cat3 = {"loads", "load"}
        if func_name in cat2:
            cat = f"Cat.2 — Inyección de Comandos/Código: {func_name}() (línea ~{lineno})"
            if cat not in self.vulnerability_categories:
                self.vulnerability_categories.append(cat)
        elif func_name in cat3:
            cat = f"Cat.3 — Deserialización Insegura: {func_name}() (línea ~{lineno})"
            if cat not in self.vulnerability_categories:
                self.vulnerability_categories.append(cat)

    def _classify_compound(self, module: str, attr: str, lineno, node: ast.Call):
        """Clasifica la categoría de vulnerabilidad para llamadas compuestas."""
        cat2_modules = {"subprocess", "os", "commands"}
        cat3_modules = {"pickle", "yaml", "marshal"}
        cat5_crypto = {("hashlib", "md5"), ("hashlib", "sha1"), ("hashlib", "new")}
        cat6_ssrf = {"requests", "httpx", "urllib", "urllib2"}

        if module in cat2_modules:
            # FIX: subprocess.run/call/Popen sin shell=True es seguro
            # Solo se considera peligroso si shell=True está explícitamente en los kwargs
            if module == "subprocess" and attr in {"run", "call", "Popen"}:
                shell_kwarg = next(
                    (kw for kw in node.keywords if kw.arg == "shell"), None
                )
                shell_is_true = (
                    shell_kwarg is not None and
                    isinstance(shell_kwarg.value, ast.Constant) and
                    shell_kwarg.value.value is True
                )
                if not shell_is_true:
                    return  # shell=False o no especificado → patrón seguro
            cat = f"Cat.2 — Inyección de Comandos: {module}.{attr}() (línea ~{lineno})"
        elif module in cat3_modules:
            # Para yaml.load, verificar si usa SafeLoader
            if module == "yaml" and attr == "load":
                args = node.args + [kw.value for kw in node.keywords]
                uses_safe = any(
                    (isinstance(a, ast.Attribute) and "safe" in a.attr.lower()) or
                    (isinstance(a, ast.Name) and "safe" in a.id.lower())
                    for a in args
                )
                if uses_safe:
                    return  # yaml.load(data, Loader=SafeLoader) es seguro
            cat = f"Cat.3 — Deserialización Insegura: {module}.{attr}() (línea ~{lineno})"
        elif (module, attr) in cat5_crypto:
            cat = f"Cat.5 — Criptografía Débil: {module}.{attr}() (línea ~{lineno})"
        elif module in cat6_ssrf:
            cat = f"Cat.6 — SSRF Potencial: {module}.{attr}() con entrada de usuario (línea ~{lineno})"
        else:
            return

        if cat not in self.vulnerability_categories:
            self.vulnerability_categories.append(cat)

    def _classify_attr(self, attr: str, lineno):
        """Clasifica por atributo cuando el módulo está aliasado."""
        cat2 = {"system", "Popen", "popen", "execv", "execve"}
        cat3 = {"loads", "load"}
        cat5 = {"md5", "sha1"}
        if attr in cat2:
            cat = f"Cat.2 — Inyección de Comandos (alias): .{attr}() (línea ~{lineno})"
        elif attr in cat3:
            cat = f"Cat.3 — Deserialización Insegura (alias): .{attr}() (línea ~{lineno})"
        elif attr in cat5:
            cat = f"Cat.5 — Criptografía Débil (alias): .{attr}() (línea ~{lineno})"
        else:
            return
        if cat not in self.vulnerability_categories:
            self.vulnerability_categories.append(cat)

    def visit_Assign(self, node: ast.Assign):
        """
        Detecta secretos hardcodeados (Cat. 5).
        Busca patrones como: LLAVE_API = "AIzaSy...", PASSWORD = "s3cr3t"
        """
        lineno = getattr(node, "lineno", "?")
        for target in node.targets:
            var_name = ""
            if isinstance(target, ast.Name):
                var_name = target.id
            elif isinstance(target, ast.Attribute):
                var_name = target.attr

            if var_name and _SECRET_NAME_PATTERNS.search(var_name):
                # El nombre de variable huele a secreto — verificar si el valor
                # es un string literal no vacío (no un env var)
                value_node = node.value
                if isinstance(value_node, ast.Constant) and isinstance(value_node.value, str):
                    secret_value = value_node.value.strip()
                    # Ignorar valores que son claramente placeholders
                    placeholders = {
                        "", "your_key", "your_secret", "your_password",
                        "changeme", "placeholder", "xxxxx", "...", "none",
                        "null", "todo", "fixme",
                    }
                    if secret_value.lower() not in placeholders and len(secret_value) >= 4:
                        self.has_hardcoded_secret = 1
                        self.dangerous_func_count += 1
                        detail = f"Secreto hardcodeado: {var_name} = '...' (línea ~{lineno})"
                        self.found_dangerous_details.append(detail)
                        cat = f"Cat.5 — Secreto Hardcodeado: '{var_name}' con valor literal (línea ~{lineno})"
                        if cat not in self.vulnerability_categories:
                            self.vulnerability_categories.append(cat)

        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        self.num_imports += len(node.names)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        self.num_imports += len(node.names) if node.names else 1
        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp):
        if isinstance(node.op, (ast.Add, ast.Mod)):
            self.has_string_concat = 1
            # Cat. 6 — XSS (concatenación con HTML)
            lineno = getattr(node, "lineno", "?")
            html_tags = {"<html", "<body", "<script", "<div", "<h1", "<p"}
            for child in (node.left, node.right):
                if isinstance(child, ast.Constant) and isinstance(child.value, str):
                    if any(tag in child.value.lower() for tag in html_tags):
                        self.dangerous_func_count += 1
                        cat = f"Cat.6 — XSS Potencial: Concatenación de HTML (línea ~{lineno})"
                        if cat not in self.vulnerability_categories:
                            self.vulnerability_categories.append(cat)
                        break
        self.generic_visit(node)

    def visit_JoinedStr(self, node: ast.JoinedStr):
        # f-strings también son concatenación
        self.has_string_concat = 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        self.num_exception_handlers += 1
        self.generic_visit(node)

    def extract(self, code_snippet: str) -> Dict:
        self._reset()
        try:
            tree = ast.parse(code_snippet)
            self.ast_depth = self._compute_depth(tree)
            self.visit(tree)
        except (SyntaxError, IndentationError):
            self.ast_depth = -1
        except Exception:
            self.ast_depth = -1

        return {
            "ast_depth": self.ast_depth,
            "dangerous_func_count": self.dangerous_func_count,
            "total_calls": self.total_calls,
            "num_imports": self.num_imports,
            "has_string_concat": self.has_string_concat,
            "num_exception_handlers": self.num_exception_handlers,
            "has_hardcoded_secret": self.has_hardcoded_secret,
            "found_dangerous_details": self.found_dangerous_details,
            "vulnerability_categories": self.vulnerability_categories,
        }


# =============================================================================
# DETECCIÓN HEURÍSTICA ADICIONAL (nivel de texto)
# Complementa el AST para detectar patrones que el modelo ML podría perder
# =============================================================================

# Heurísticas de texto por categoría de vulnerabilidad
HEURISTIC_RULES = [
    # Cat. 2 — Command Injection
    # NOTA: subprocess.run/call/Popen se omiten aquí porque el AST ya
    # los detecta correctamente verificando shell=True. Las heurísticas de
    # texto no pueden distinguir shell=True de shell=False de forma confiable.
    {
        "category": "Cat.2 — Inyección de Comandos/Código",
        "patterns": ["eval(", "exec(", "os.system(", "os.popen(",
                     "subprocess.popen(\"" , "subprocess.run(\"" , "subprocess.call(\"",
                     "commands.getoutput"],
    },
    # Cat. 3 — Deserialización insegura
    {
        "category": "Cat.3 — Deserialización Insegura",
        "patterns": ["pickle.loads", "pickle.load(", "yaml.load(", "marshal.loads",
                     "marshal.load("],
    },
    # Cat. 4 — Path Traversal
    {
        "category": "Cat.4 — Path Traversal",
        # FIX: se eliminó "os.path.join(" (muy común en código seguro → falso positivo)
        # y "send_file(" (Flask/FastAPI usan send_file con rutas validadas habitualmente).
        # La detección de Path Traversal real se hace vía AST (detect_path_traversal_ast).
        "patterns": ["../", "..\\", "open(ruta", "open(path", "open(filename",
                     "open(file_", "open(f_", 'open("uploads/', "open('uploads/"],
    },
    # Cat. 5 — Hardcoded secrets
    {
        "category": "Cat.5 — Secreto Hardcodeado / Criptografía Débil",
        "patterns": ["hashlib.md5(", "hashlib.sha1(", ".md5(", ".sha1(",
                     'aizasy', 'sk-', 'ghp_', 'secret_key =', 'api_key =',
                     'password =', 'passwd =', 'token =', 'llave_api'],
    },
    # Cat. 6 — XSS / SSRF
    {
        "category": "Cat.6 — XSS / SSRF",
        "patterns": ["requests.get(", "requests.post(", "requests.put(",
                     "urllib.urlopen", "httpx.get(", "<html>", "<script>",
                     "<body>", "innerHTML", "document.write"],
    },
    # Palabras clave genéricas de ataque (solo patrones muy específicos
    # que no aparecen en comentarios normales de código seguro)
    {
        "category": "Palabras clave de vulnerabilidad detectadas",
        "patterns": ["sqli", "drop table", "' or '1'='1",
                     "payload malicioso", "exploit("],
    },
]

# Lista plana de todas las heurísticas para búsqueda de líneas culpables
ALL_SUSPICIOUS_PATTERNS = [
    p for rule in HEURISTIC_RULES for p in rule["patterns"]
]


def detect_heuristic_categories(code_snippet: str) -> List[str]:
    """Detecta categorías de vulnerabilidad mediante búsqueda de texto."""
    code_lower = code_snippet.lower()
    detected = []
    for rule in HEURISTIC_RULES:
        for pattern in rule["patterns"]:
            if pattern.lower() in code_lower:
                cat = rule["category"]
                if cat not in detected:
                    detected.append(cat)
                break  # Una coincidencia por regla es suficiente
    return detected


def detect_path_traversal_ast(code_snippet: str) -> List[str]:
    """
    Detecta Path Traversal (Cat. 4) mediante análisis AST.
    Busca open() cuyo primer argumento contiene concatenación de strings.
    """
    findings = []
    try:
        tree = ast.parse(code_snippet)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            # Detectar open() y variantes
            func_name = ""
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr

            if func_name not in {"open", "send_file", "send_from_directory"}:
                continue

            if not node.args:
                continue

            first_arg = node.args[0]
            lineno = getattr(node, "lineno", "?")

            # El primer argumento es una concatenación (BinOp con Add)
            if isinstance(first_arg, ast.BinOp) and isinstance(first_arg.op, ast.Add):
                findings.append(f"Cat.4 — Path Traversal: {func_name}(concat) (línea ~{lineno})")

            # El primer argumento es un f-string con variables
            elif isinstance(first_arg, ast.JoinedStr) and any(
                isinstance(v, ast.FormattedValue) for v in first_arg.values
            ):
                findings.append(f"Cat.4 — Path Traversal: {func_name}(f-string) (línea ~{lineno})")
    except Exception:
        pass
    return findings


# =============================================================================
# FUNCIONES DE APOYO
# =============================================================================

def parse_diff(diff_path: str):
    """Extrae únicamente las líneas añadidas del archivo .diff y detecta los archivos con sus líneas."""
    added_lines = []
    modified_files = set()
    current_file = "Desconocido"
    current_line = 0
    file_lines_added = {}

    with open(diff_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("+++ b/"):
                current_file = line[6:].strip()
            elif line.startswith("@@"):
                parts = line.split(" ")
                if len(parts) >= 3 and parts[2].startswith("+"):
                    c_d = parts[2][1:].split(",")
                    try:
                        current_line = int(c_d[0])
                    except ValueError:
                        current_line = 0
            elif line.startswith("+++"):
                continue
            elif line.startswith("+"):
                code_line = line[1:]
                if current_file.endswith(".py"):
                    modified_files.add(current_file)
                    added_lines.append(code_line)
                    if current_file not in file_lines_added:
                        file_lines_added[current_file] = []
                    file_lines_added[current_file].append((current_line, code_line))
                current_line += 1
            elif line.startswith(" "):
                current_line += 1

    return "".join(added_lines), list(modified_files), file_lines_added


def robust_ast_extract(code_snippet: str, extractor: ASTFeatureExtractor) -> Dict:
    """Extrae features AST, envolviendo el código en un wrapper si hay error sintáctico."""
    features = extractor.extract(code_snippet)

    if features["ast_depth"] == -1:
        wrapped_code = "def wrapper():\n" + "\n".join(
            ["    " + line for line in code_snippet.split("\n")]
        )
        features = extractor.extract(wrapped_code)

    return features


# =============================================================================
# FLUJO PRINCIPAL DE INFERENCIA
# =============================================================================

def main():
    if len(sys.argv) < 2:
        print("Uso: python analizador_ci.py <ruta_al_diff>")
        sys.exit(1)

    diff_path = sys.argv[1]
    if not os.path.exists(diff_path):
        print(f"Error: No se encontró el archivo diff en {diff_path}")
        sys.exit(1)

    # 1. Parsear diff
    code_snippet, modified_files, file_lines_added = parse_diff(diff_path)
    if not code_snippet.strip():
        print("No se encontraron adiciones de código en el PR. Omitiendo análisis.")
        sys.exit(0)

    # 2. Cargar Modelos
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(base_dir, "pipeline", "models")
    rf_model_path = os.path.join(models_dir, "rf_vulnerability_detector.joblib")
    tfidf_path = os.path.join(models_dir, "tfidf_vectorizer.joblib")

    if not os.path.exists(rf_model_path) or not os.path.exists(tfidf_path):
        error_msg = f"Error: No se encontraron los modelos .joblib en la carpeta {models_dir}"
        print(error_msg)
        with open("reporte_seguridad.txt", "w", encoding="utf-8") as f:
            f.write(f"🚨 **ERROR INTERNO DEL PIPELINE** 🚨\n\n{error_msg}")
        sys.exit(1)

    rf_model = joblib.load(rf_model_path)
    tfidf = joblib.load(tfidf_path)

    # 3. Vectorización TF-IDF
    tfidf_features = tfidf.transform([code_snippet])

    # 4. Extracción AST
    extractor = ASTFeatureExtractor()
    ast_features_dict = robust_ast_extract(code_snippet, extractor)

    # Asegurar orden exacto de las columnas numéricas (compatible con modelo actual)
    ast_features_array = np.array([[
        ast_features_dict["ast_depth"],
        ast_features_dict["dangerous_func_count"],
        ast_features_dict["total_calls"],
        ast_features_dict["num_imports"],
        ast_features_dict["has_string_concat"],
        ast_features_dict["num_exception_handlers"],
        ast_features_dict["has_hardcoded_secret"],
    ]])

    # 5. Concatenación Final (TF-IDF primero, AST después)
    final_features = hstack([tfidf_features, ast_features_array])

    # 6. Predicción del modelo ML
    prediction = rf_model.predict(final_features)[0]
    probabilities = rf_model.predict_proba(final_features)[0]
    vuln_prob = probabilities[1] * 100

    # 7. Detección heurística de texto (Cat. 3-6)
    heuristic_categories = detect_heuristic_categories(code_snippet)

    # 8. Detección AST de Path Traversal (Cat. 4)
    path_traversal_findings = detect_path_traversal_ast(code_snippet)

    # 9. Categorías detectadas por el ASTFeatureExtractor ampliado
    ast_vuln_categories = ast_features_dict.get("vulnerability_categories", [])

    # 10. Decisión final
    # ══════════════════════════════════════════════════════════════════════
    # ARQUITECTURA DE DECISIÓN (3 capas):
    #
    # CAPA 1 — Modelo ML (GATE PRINCIPAL):
    #   prediction == 1 → el RandomForest votó mayoría vulnerable
    #   vuln_prob >= 50% → probabilidad alta (umbral conservador para evitar FP)
    #
    # CAPA 2 — AST real (GATE SECUNDARIO):
    #   dangerous_func_count > 0 → se encontraron LLAMADAS REALES a funciones
    #   peligrosas en el AST (pickle.loads, yaml.load, eval, etc.)
    #   path_traversal_findings → open(concat) real detectado
    #
    # CAPA 3 — Heurísticas de texto (SOLO CONTEXTO, NO GATE):
    #   Solo añaden detalle al reporte cuando alguna de las capas anteriores
    #   ya disparó. NUNCA bloquean por sí solas (evita falsos positivos cuando
    #   el diff modifica scripts de seguridad que discuten vulnerabilidades).
    # ══════════════════════════════════════════════════════════════════════

    # El bloqueo requiere que el ML o un hallazgo crítico del AST real lo confirmen
    has_ml_signal = (prediction == 1 or vuln_prob >= 50.0)
    
    # Todas las categorías detectadas directamente por el AST se consideran señales fuertes de bloqueo
    critical_ast_categories = ast_vuln_categories
    
    has_ast_signal = (
        len(critical_ast_categories) > 0 or
        len(path_traversal_findings) > 0
    )
    has_heuristic_signal = len(heuristic_categories) > 0  # Solo para el reporte

    # El bloqueo requiere que el ML o un hallazgo crítico del AST real lo confirmen
    is_vulnerable = has_ml_signal or has_ast_signal

    report_file = "reporte_seguridad.txt"

    if is_vulnerable:
        # ── CONSTRUIR LISTA DE ANOMALÍAS ─────────────────────────────────────
        anomalies = []

        # Anomalías detectadas por AST (con categoría específica)
        if ast_vuln_categories:
            for cat in ast_vuln_categories:
                anomalies.append(f"- 🔴 {cat}")

        # Anomalías detectadas por heurística de texto (que no estén ya en AST)
        existing_prefixes = {a.split("—")[0].strip("- 🔴 ") for a in anomalies}
        for cat in heuristic_categories:
            prefix = cat.split("—")[0].strip()
            if prefix not in existing_prefixes:
                anomalies.append(f"- 🟠 {cat} (detectado por análisis de texto)")

        # Path Traversal detectado por AST especializado
        for finding in path_traversal_findings:
            anomalies.append(f"- 🔴 {finding}")

        # Concatenación de strings (posible SQLi/XSS)
        if ast_features_dict["has_string_concat"] == 1 and not anomalies:
            anomalies.append("- 🟡 Concatenación de strings detectada (posible riesgo de inyección).")

        # Si el modelo ML disparó pero las heurísticas no encontraron nada específico
        if not anomalies and has_ml_signal:
            anomalies.append(
                "- 🟠 El modelo ML identificó patrones asociados con código inseguro "
                f"(probabilidad: {vuln_prob:.1f}%)."
            )

        anomalies_text = "\n".join(anomalies) if anomalies else (
            "- El modelo identificó patrones comúnmente asociados con código inseguro."
        )

        # ── BUSCAR LÍNEAS CULPABLES ───────────────────────────────────────────
        culprit_lines = []
        all_patterns = ALL_SUSPICIOUS_PATTERNS + [
            "eval", "exec", "subprocess", "os.system", "system", "Popen",
            "pickle", "yaml.load", "requests.get", "requests.post",
            "hashlib.md5", "hashlib.sha1", "md5(", "sha1(",
            "secret", "api_key", "password", "token", "llave_api",
            "open(", "../", "..\\",
        ]

        for f_name, lines in file_lines_added.items():
            for l_num, l_text in lines:
                l_lower = l_text.lower()
                matched = False
                for pattern in all_patterns:
                    if pattern.lower() in l_lower:
                        culprit_lines.append(
                            f"  - `{f_name}` (Línea {l_num}): `{l_text.strip()[:80]}`"
                        )
                        matched = True
                        break
                if not matched and ast_features_dict["has_string_concat"] == 1:
                    if ("%" in l_text or "+" in l_text or ".format" in l_text
                            or 'f"' in l_text or "f'" in l_text):
                        sql_words = ["select", "insert", "update", "delete", "drop",
                                     "where", "from ", "table"]
                        html_words = ["<html", "<body", "<script", "<div", "innerHTML"]
                        if any(w in l_lower for w in sql_words):
                            culprit_lines.append(
                                f"  - `{f_name}` (Línea {l_num}) [Posible SQLi]: `{l_text.strip()[:80]}`"
                            )
                        elif any(w in l_lower for w in html_words):
                            culprit_lines.append(
                                f"  - `{f_name}` (Línea {l_num}) [Posible XSS]: `{l_text.strip()[:80]}`"
                            )

        lineas_texto = ""
        if culprit_lines:
            lineas_texto = "\n**Líneas Sospechosas Identificadas:**\n" + "\n".join(culprit_lines[:15])
            if len(culprit_lines) > 15:
                lineas_texto += f"\n  - ... (y {len(culprit_lines) - 15} líneas más)"

        archivos_afectados = ", ".join(modified_files) if modified_files else "Desconocido"

        report_content = f"""🚨 **RECHAZO AUTOMÁTICO - REVISIÓN DE SEGURIDAD FALLIDA** 🚨

El análisis estático de seguridad ha detectado código potencialmente **VULNERABLE** en tu Pull Request.

**Detalles del Análisis:**
- **Archivos afectados:** {archivos_afectados}
- **Probabilidad ML de vulnerabilidad:** {vuln_prob:.2f}%
- **Funciones peligrosas detectadas (AST):** {ast_features_dict['dangerous_func_count']}
- **Decisión:** Bloqueo Automático (Revisión requerida)

**Tipos de Vulnerabilidad Detectadas:**
{anomalies_text}
{lineas_texto}

**Guía de Corrección:**
- Cat.2 (Comandos): Usa listas en `subprocess.run([...], shell=False)` en vez de strings
- Cat.3 (Deserialización): Usa `yaml.safe_load()` en vez de `yaml.load()`. Evita `pickle` con datos externos
- Cat.4 (Path Traversal): Valida y normaliza rutas con `os.path.realpath()` y lista blanca
- Cat.5 (Secretos): Usa variables de entorno `os.environ.get('API_KEY')`. Usa `hashlib.sha256()` o `bcrypt`
- Cat.6 (SSRF/XSS): Valida URLs contra lista blanca. Usa `html.escape()` para salida HTML

_Por favor, revisa las líneas indicadas y corrige el código antes de reabrir el PR._
"""
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)

        telegram_msg = (
            f"🚨 ALERTA CRÍTICA: Código Vulnerable Detectado 🚨\n\n"
            f"El análisis de seguridad bloqueó el PR.\n"
            f"Probabilidad ML: {vuln_prob:.2f}%\n\n"
            f"📁 Archivos: {archivos_afectados}\n\n"
            f"🛑 Vulnerabilidades:\n{anomalies_text}"
        )
        with open("telegram_msg.txt", "w", encoding="utf-8") as f:
            f.write(telegram_msg)

        print("🚨 CÓDIGO VULNERABLE DETECTADO. Probabilidad ML:", f"{vuln_prob:.2f}%")
        print(f"   Funciones peligrosas (AST): {ast_features_dict['dangerous_func_count']}")
        print(f"   Categorías detectadas: {len(ast_vuln_categories + heuristic_categories + path_traversal_findings)}")
        print("Reporte generado. Finalizando con código de error (Exit 1).")
        sys.exit(1)

    else:
        # ES SEGURO
        report_content = (
            f"✅ REVISIÓN DE SEGURIDAD APROBADA: El código es estadísticamente seguro.\n"
            f"Probabilidad ML de vulnerabilidad: {vuln_prob:.2f}%"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)

        print("✅ REVISIÓN DE SEGURIDAD APROBADA: Código seguro detectado. Probabilidad de riesgo:", f"{vuln_prob:.2f}%")
        print("Reporte generado. Finalizando con éxito (Exit 0).")
        sys.exit(0)


if __name__ == "__main__":
    main()
