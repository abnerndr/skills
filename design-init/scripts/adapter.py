#!/usr/bin/env python3
"""
adapter.py — Converte output do engine ui-ux-pro-max em YAML front matter e corpo do DESIGN.md.

Formato de saída: proprietário google-labs-code/design.md (não W3C DTCG).
W3C DTCG é o formato de export via `npx @google/design.md export --format dtcg`.

Uso CLI:
    python3 adapter.py --engine-output <path_json> --product-type <str> --keywords <str> --out <path_yaml>

Exit codes:
    0  Sucesso
    1  Erro de validação (campo obrigatório ausente no engine output)
    2  Erro de I/O
    3  Python < 3.8 ou dependência ausente
"""

import sys

if sys.version_info < (3, 8):
    sys.stderr.write("adapter.py requer Python >= 3.8\n")
    sys.exit(3)

import argparse
import json
import re
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("[adapter] PyYAML ausente. Instale: pip install pyyaml\n")
    sys.exit(3)


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

SPACING_SCALE = {"xs": "4px", "sm": "8px", "md": "16px", "lg": "24px", "xl": "32px", "2xl": "48px", "3xl": "64px"}

ROUNDED_BY_STYLE = {
    "minimalism":    {"sm": "2px", "md": "4px", "lg": "8px"},
    "flat":          {"sm": "2px", "md": "4px", "lg": "8px"},
    "flat design":   {"sm": "2px", "md": "4px", "lg": "8px"},
    "glassmorphism": {"sm": "8px", "md": "16px", "lg": "24px"},
    "soft":          {"sm": "8px", "md": "16px", "lg": "24px"},
    "neumorphism":   {"sm": "8px", "md": "16px", "lg": "24px"},
    "brutalism":     {"sm": "0px", "md": "0px", "lg": "0px"},
}
ROUNDED_DEFAULT = {"sm": "4px", "md": "8px", "lg": "16px"}

HEX_RE = re.compile(r"^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_valid_hex(value: str) -> bool:
    return bool(value and HEX_RE.match(str(value).strip()))


def style_to_rounded(style_name: str) -> dict:
    key = (style_name or "").lower().strip()
    for pattern, rounded in ROUNDED_BY_STYLE.items():
        if pattern in key:
            return rounded
    return ROUNDED_DEFAULT.copy()


# ---------------------------------------------------------------------------
# Mapeamentos de domínio → YAML front matter
# ---------------------------------------------------------------------------

def map_colors(engine_output: dict) -> dict:
    colors_raw = engine_output.get("colors", {})
    mapped = {
        "primary":    colors_raw.get("primary", "#2563EB"),
        "secondary":  colors_raw.get("secondary", "#3B82F6"),
        "background": colors_raw.get("background", "#F8FAFC"),
        "text":       colors_raw.get("text", "#1E293B"),
    }
    # CTA como surface se presente
    cta = colors_raw.get("cta")
    if cta and is_valid_hex(cta):
        mapped["surface"] = cta

    for field, val in mapped.items():
        if not is_valid_hex(val):
            mapped[field] = "#000000"

    return mapped


def map_typography(engine_output: dict) -> dict:
    typo_raw = engine_output.get("typography", {})
    heading_font = typo_raw.get("heading", "Inter") or "Inter"
    body_font = typo_raw.get("body", "Inter") or "Inter"
    return {
        "heading": {"fontFamily": heading_font.strip(), "fontWeight": 700},
        "body":    {"fontFamily": body_font.strip(), "fontSize": "16px"},
    }


def map_rounded(engine_output: dict) -> dict:
    style_name = engine_output.get("style", {}).get("name", "")
    return style_to_rounded(style_name)


def map_description(engine_output: dict) -> str:
    # Prefer ui-reasoning / overview; fallback to pattern name
    desc = engine_output.get("description", "")
    if not desc:
        pattern_name = engine_output.get("pattern", {}).get("name", "")
        style_name = engine_output.get("style", {}).get("name", "")
        project = engine_output.get("project_name", "")
        desc = f"{project} design system — {style_name} style, {pattern_name} pattern".strip(" —")
    return desc


# ---------------------------------------------------------------------------
# Corpo do DESIGN.md (seções canônicas)
# ---------------------------------------------------------------------------

def build_body_sections(engine_output: dict, product_type: str = "", keywords: str = "") -> str:
    pattern = engine_output.get("pattern", {})
    style = engine_output.get("style", {})
    colors = engine_output.get("colors", {})
    typo = engine_output.get("typography", {})
    effects = engine_output.get("key_effects", "")
    anti_patterns_raw = engine_output.get("anti_patterns", "")
    project = engine_output.get("project_name", "Project")
    category = engine_output.get("category", "")

    lines = []

    # Overview
    lines += [
        "## Overview",
        "",
        f"**{project}** — {category or product_type or 'General'} design system.",
        f"Style: {style.get('name', '')}. {style.get('best_for', '')}",
        "",
    ]

    # Colors
    color_rows = "\n".join([
        "| Role | Hex | CSS Variable |",
        "|------|-----|--------------|",
        f"| Primary    | `{colors.get('primary', '#2563EB')}` | `--color-primary` |",
        f"| Secondary  | `{colors.get('secondary', '#3B82F6')}` | `--color-secondary` |",
        f"| CTA/Accent | `{colors.get('cta') or colors.get('surface', '#F97316')}` | `--color-cta` |",
        f"| Background | `{colors.get('background', '#F8FAFC')}` | `--color-background` |",
        f"| Text       | `{colors.get('text', '#1E293B')}` | `--color-text` |",
    ])
    lines += ["## Colors", "", color_rows, ""]

    # Typography
    heading_font = typo.get("heading", "Inter")
    body_font = typo.get("body", "Inter")
    lines += [
        "## Typography",
        "",
        f"- **Heading:** {heading_font}  (weights: 400, 700)",
        f"- **Body:** {body_font}  (size: 16px)",
        f"- **Mood:** {typo.get('mood', '')}",
        "",
    ]

    # Layout
    pattern_name = pattern.get("name", "")
    sections = pattern.get("sections", "")
    cta_placement = pattern.get("cta_placement", "")
    lines += [
        "## Layout",
        "",
        f"**Pattern:** {pattern_name}",
        f"**Sections:** {sections}",
        f"**Primary CTA Placement:** {cta_placement}",
        "",
    ]

    # Elevation & Depth
    lines += [
        "## Elevation & Depth",
        "",
        "| Level | Shadow | Usage |",
        "|-------|--------|-------|",
        "| sm | `0 1px 2px rgba(0,0,0,0.05)` | Subtle lift |",
        "| md | `0 4px 6px rgba(0,0,0,0.1)` | Cards, buttons |",
        "| lg | `0 10px 15px rgba(0,0,0,0.1)` | Modals, dropdowns |",
        "",
    ]

    # Shapes (rounded)
    rounded = style_to_rounded(style.get("name", ""))
    lines += [
        "## Shapes",
        "",
        f"- **sm:** {rounded['sm']}",
        f"- **md:** {rounded['md']}",
        f"- **lg:** {rounded['lg']}",
        "",
    ]

    # Components placeholder
    lines += [
        "## Components",
        "",
        "<!-- Adicionar componentes específicos do projeto aqui após design-init. -->",
        "",
    ]

    # Do's and Don'ts
    lines += ["## Do's and Don'ts", ""]
    if effects:
        lines.append(f"**Key Effects to Apply:** {effects}")
        lines.append("")
    if anti_patterns_raw:
        anti_list = [a.strip() for a in anti_patterns_raw.split("+") if a.strip()]
        lines.append("**Anti-patterns (do not use):**")
        for anti in anti_list:
            lines.append(f"- {anti}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Função pública: csv_to_design_md_yaml
# ---------------------------------------------------------------------------

def csv_to_design_md_yaml(engine_output: dict, include_body: bool = False, product_type: str = "", keywords: str = "") -> dict:
    """
    Converte o dict retornado por DesignSystemGenerator.generate() em um dict com:
    - 'yaml_frontmatter': dict com campos do formato proprietário google-labs-code/design.md
    - 'body': string markdown com 8 seções canônicas (somente se include_body=True)

    Não produz W3C DTCG — esse formato é gerado por `npx @google/design.md export --format dtcg`.
    """
    result = {
        "yaml_frontmatter": {
            "version": "1.0",
            "name": f"{engine_output.get('project_name', 'Project')} Design System",
            "description": map_description(engine_output),
            "colors": map_colors(engine_output),
            "typography": map_typography(engine_output),
            "spacing": dict(SPACING_SCALE),
            "rounded": map_rounded(engine_output),
            "components": [],
        }
    }

    if include_body:
        result["body"] = build_body_sections(engine_output, product_type, keywords)

    return result


def build_design_md(engine_output: dict, product_type: str = "", keywords: str = "") -> str:
    """Monta o DESIGN.md completo como string (YAML front matter + corpo markdown)."""
    data = csv_to_design_md_yaml(engine_output, include_body=True, product_type=product_type, keywords=keywords)
    fm = data["yaml_frontmatter"]
    body = data.get("body", "")

    yaml_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    return f"---\n{yaml_str}---\n\n{body}"


# ---------------------------------------------------------------------------
# Validação de entrada
# ---------------------------------------------------------------------------

def validate_engine_output(engine_output: dict) -> str | None:
    """Retorna mensagem de erro ou None se válido."""
    colors = engine_output.get("colors", {})
    typo = engine_output.get("typography", {})
    if not colors.get("primary"):
        return "Campo obrigatório ausente: colors.primary"
    if not typo.get("body"):
        return "Campo obrigatório ausente: typography.body"
    return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="adapter.py — ui-ux-pro-max → DESIGN.md YAML")
    parser.add_argument("--engine-output", required=True, help="Path para JSON com output do engine")
    parser.add_argument("--product-type", default="", help="Tipo de produto (opcional)")
    parser.add_argument("--keywords", default="", help="Keywords separadas por vírgula (opcional)")
    parser.add_argument("--out", required=True, help="Path de saída para o YAML front matter")
    args = parser.parse_args()

    try:
        with open(args.engine_output, "r", encoding="utf-8") as f:
            engine_output = json.load(f)
    except (FileNotFoundError, PermissionError) as e:
        sys.stderr.write(f"[adapter] Erro de I/O ao ler --engine-output: {e}\n")
        sys.exit(2)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"[adapter] JSON inválido em --engine-output: {e}\n")
        sys.exit(1)

    error = validate_engine_output(engine_output)
    if error:
        sys.stderr.write(f"[adapter] Validação falhou: {error}\n")
        sys.exit(1)

    data = csv_to_design_md_yaml(engine_output, include_body=False)
    fm = data["yaml_frontmatter"]

    try:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        yaml_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(yaml_str)
    except (OSError, PermissionError) as e:
        sys.stderr.write(f"[adapter] Erro de I/O ao escrever --out: {e}\n")
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
