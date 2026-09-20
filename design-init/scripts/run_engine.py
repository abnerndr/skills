#!/usr/bin/env python3
"""
run_engine.py — Wrapper end-to-end: engine ui-ux-pro-max → DESIGN.md completo.

Importa DesignSystemGenerator e csv_to_design_md_yaml em memória — sem serialização
JSON intermediária. Produz o DESIGN.md completo (YAML front matter + 8 seções canônicas).

Uso:
    python3 run_engine.py --keywords "automotivo, concessionária" --product-type "e-commerce" --out /tmp/design.md

Exit codes:
    0  Sucesso
    1  Dict inválido retornado pelo engine
    2  Erro de I/O
    3  Python < 3.8 ou dependência ausente
"""

import sys

if sys.version_info < (3, 8):
    sys.stderr.write("run_engine.py requer Python >= 3.8\n")
    sys.exit(3)

import argparse
import os
from pathlib import Path

# Resolve o path do engine a partir da localização deste script:
# scripts/ → design-init/ → skills/ → ui-ux-pro-max/scripts/
_SCRIPT_DIR = Path(__file__).parent.resolve()
_ENGINE_SCRIPTS = _SCRIPT_DIR.parent.parent / "ui-ux-pro-max" / "scripts"

if str(_ENGINE_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_ENGINE_SCRIPTS))

if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

try:
    from design_system import DesignSystemGenerator
except ImportError as e:
    sys.stderr.write(f"[run_engine] Não foi possível importar design_system.py: {e}\n")
    sys.stderr.write(f"  Esperado em: {_ENGINE_SCRIPTS}\n")
    sys.exit(3)

try:
    from adapter import csv_to_design_md_yaml, build_design_md, validate_engine_output
except ImportError as e:
    sys.stderr.write(f"[run_engine] Não foi possível importar adapter.py: {e}\n")
    sys.exit(3)


def main():
    parser = argparse.ArgumentParser(description="run_engine.py — gera DESIGN.md completo")
    parser.add_argument("--keywords", default="", help="Keywords de indústria separadas por vírgula")
    parser.add_argument("--product-type", default="", help="Tipo de produto (ex: e-commerce, SaaS)")
    parser.add_argument("--out", required=True, help="Path de saída para o DESIGN.md")
    args = parser.parse_args()

    # Monta query para o engine: combina product-type e keywords
    query_parts = [p.strip() for p in [args.product_type, args.keywords] if p.strip()]
    query = ", ".join(query_parts) if query_parts else "web application"
    project_name = args.product_type.strip().title() if args.product_type.strip() else "Project"

    # Inicializa engine e gera dict interno
    generator = DesignSystemGenerator()
    try:
        engine_output = generator.generate(query, project_name)
    except Exception as e:
        sys.stderr.write(f"[run_engine] Erro no engine: {e}\n")
        sys.exit(1)

    # Valida campos obrigatórios
    error = validate_engine_output(engine_output)
    if error:
        sys.stderr.write(f"[run_engine] Dict inválido do engine: {error}\n")
        sys.exit(1)

    # Monta DESIGN.md completo via adapter (in-process, sem subprocess)
    design_md_content = build_design_md(engine_output, args.product_type, args.keywords)

    # Escreve arquivo de saída
    try:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(design_md_content)
    except (OSError, PermissionError) as e:
        sys.stderr.write(f"[run_engine] Erro de I/O ao escrever --out: {e}\n")
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
