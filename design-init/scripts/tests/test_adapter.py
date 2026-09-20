"""
test_adapter.py — Testes unitários para adapter.py.

Cobertura mínima: ≥85% (configurado em pytest.ini).
Execução: cd .claude/skills/design-init/scripts && python3 -m pytest tests/ -v --cov=adapter
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Adiciona o diretório pai (scripts/) ao sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

import adapter


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def minimal_engine_output():
    """Output mínimo válido do engine."""
    return {
        "project_name": "TestProject",
        "category": "SaaS",
        "style": {"name": "Minimalism"},
        "colors": {
            "primary": "#2563EB",
            "secondary": "#3B82F6",
            "cta": "#F97316",
            "background": "#F8FAFC",
            "text": "#1E293B",
        },
        "typography": {
            "heading": "Inter",
            "body": "Inter",
            "mood": "Clean",
        },
        "pattern": {
            "name": "Hero + Features + CTA",
            "sections": "Hero > Features > CTA",
            "cta_placement": "Above fold",
        },
        "key_effects": "Subtle hover transitions",
        "anti_patterns": "Heavy drop shadows + Comic Sans",
        "decision_rules": {},
        "severity": "MEDIUM",
    }


@pytest.fixture
def glassmorphism_output(minimal_engine_output):
    out = minimal_engine_output.copy()
    out["style"] = {"name": "Glassmorphism"}
    return out


@pytest.fixture
def brutalism_output(minimal_engine_output):
    out = minimal_engine_output.copy()
    out["style"] = {"name": "Brutalism"}
    return out


@pytest.fixture
def custom_fonts_output(minimal_engine_output):
    out = minimal_engine_output.copy()
    out["typography"] = {"heading": "Playfair Display", "body": "Lato", "mood": "Elegant"}
    return out


# ---------------------------------------------------------------------------
# TestStylesCSV — styles.csv → rounded.*
# ---------------------------------------------------------------------------

class TestStylesCSV:
    def test_minimalism_rounded_small(self, minimal_engine_output):
        result = adapter.csv_to_design_md_yaml(minimal_engine_output)
        rounded = result["yaml_frontmatter"]["rounded"]
        assert rounded["sm"] == "2px"
        assert rounded["md"] == "4px"
        assert rounded["lg"] == "8px"

    def test_glassmorphism_rounded_large(self, glassmorphism_output):
        result = adapter.csv_to_design_md_yaml(glassmorphism_output)
        rounded = result["yaml_frontmatter"]["rounded"]
        assert rounded["sm"] == "8px"
        assert rounded["md"] == "16px"
        assert rounded["lg"] == "24px"

    def test_brutalism_rounded_zero(self, brutalism_output):
        result = adapter.csv_to_design_md_yaml(brutalism_output)
        rounded = result["yaml_frontmatter"]["rounded"]
        assert rounded["sm"] == "0px"
        assert rounded["md"] == "0px"

    def test_unknown_style_uses_default(self, minimal_engine_output):
        minimal_engine_output["style"] = {"name": "SomeUnknownStyle"}
        result = adapter.csv_to_design_md_yaml(minimal_engine_output)
        rounded = result["yaml_frontmatter"]["rounded"]
        assert rounded["sm"] == "4px"
        assert rounded["md"] == "8px"
        assert rounded["lg"] == "16px"

    def test_flat_design_rounded_small(self, minimal_engine_output):
        minimal_engine_output["style"] = {"name": "Flat Design"}
        result = adapter.csv_to_design_md_yaml(minimal_engine_output)
        rounded = result["yaml_frontmatter"]["rounded"]
        assert rounded["sm"] == "2px"


# ---------------------------------------------------------------------------
# TestColorsCSV — colors.csv → colors.*
# ---------------------------------------------------------------------------

class TestColorsCSV:
    def test_primary_hex_valid(self, minimal_engine_output):
        result = adapter.csv_to_design_md_yaml(minimal_engine_output)
        colors = result["yaml_frontmatter"]["colors"]
        assert adapter.is_valid_hex(colors["primary"])

    def test_background_hex_valid(self, minimal_engine_output):
        result = adapter.csv_to_design_md_yaml(minimal_engine_output)
        colors = result["yaml_frontmatter"]["colors"]
        assert adapter.is_valid_hex(colors["background"])

    def test_text_hex_valid(self, minimal_engine_output):
        result = adapter.csv_to_design_md_yaml(minimal_engine_output)
        colors = result["yaml_frontmatter"]["colors"]
        assert adapter.is_valid_hex(colors["text"])

    def test_cta_mapped_to_surface(self, minimal_engine_output):
        result = adapter.csv_to_design_md_yaml(minimal_engine_output)
        colors = result["yaml_frontmatter"]["colors"]
        # cta do engine deve aparecer como surface no design.md
        assert "surface" in colors
        assert colors["surface"] == "#F97316"

    def test_invalid_hex_replaced_with_black(self, minimal_engine_output):
        minimal_engine_output["colors"]["primary"] = "$--color-primary"
        result = adapter.csv_to_design_md_yaml(minimal_engine_output)
        colors = result["yaml_frontmatter"]["colors"]
        assert colors["primary"] == "#000000"

    def test_all_required_color_fields_present(self, minimal_engine_output):
        result = adapter.csv_to_design_md_yaml(minimal_engine_output)
        colors = result["yaml_frontmatter"]["colors"]
        for field in ["primary", "secondary", "background", "text"]:
            assert field in colors


# ---------------------------------------------------------------------------
# TestTypographyCSV — typography.csv → typography.*
# ---------------------------------------------------------------------------

class TestTypographyCSV:
    def test_heading_font_name_present(self, minimal_engine_output):
        result = adapter.csv_to_design_md_yaml(minimal_engine_output)
        typo = result["yaml_frontmatter"]["typography"]
        assert typo["heading"]["fontFamily"] == "Inter"

    def test_body_font_name_present(self, minimal_engine_output):
        result = adapter.csv_to_design_md_yaml(minimal_engine_output)
        typo = result["yaml_frontmatter"]["typography"]
        assert typo["body"]["fontFamily"] == "Inter"

    def test_heading_weight_default(self, minimal_engine_output):
        result = adapter.csv_to_design_md_yaml(minimal_engine_output)
        typo = result["yaml_frontmatter"]["typography"]
        assert typo["heading"]["fontWeight"] == 700

    def test_body_font_size_default(self, minimal_engine_output):
        result = adapter.csv_to_design_md_yaml(minimal_engine_output)
        typo = result["yaml_frontmatter"]["typography"]
        assert typo["body"]["fontSize"] == "16px"

    def test_custom_fonts(self, custom_fonts_output):
        result = adapter.csv_to_design_md_yaml(custom_fonts_output)
        typo = result["yaml_frontmatter"]["typography"]
        assert typo["heading"]["fontFamily"] == "Playfair Display"
        assert typo["body"]["fontFamily"] == "Lato"


# ---------------------------------------------------------------------------
# TestUXGuidelinesCSV — ux-guidelines.csv → anti-patterns no output
# ---------------------------------------------------------------------------

class TestUXGuidelinesCSV:
    def test_anti_patterns_in_body(self, minimal_engine_output):
        result = adapter.csv_to_design_md_yaml(minimal_engine_output, include_body=True)
        body = result.get("body", "")
        assert "Anti-patterns" in body or "anti" in body.lower()

    def test_anti_patterns_not_in_yaml_frontmatter(self, minimal_engine_output):
        result = adapter.csv_to_design_md_yaml(minimal_engine_output)
        fm = result["yaml_frontmatter"]
        assert "anti_patterns" not in fm
        assert "dos_and_donts" not in fm

    def test_effects_in_body(self, minimal_engine_output):
        result = adapter.csv_to_design_md_yaml(minimal_engine_output, include_body=True)
        body = result.get("body", "")
        assert "hover" in body.lower() or "Subtle" in body


# ---------------------------------------------------------------------------
# TestLandingCSV — landing.csv → layout pattern no output
# ---------------------------------------------------------------------------

class TestLandingCSV:
    def test_layout_section_in_body(self, minimal_engine_output):
        result = adapter.csv_to_design_md_yaml(minimal_engine_output, include_body=True)
        body = result.get("body", "")
        assert "## Layout" in body

    def test_pattern_name_in_body(self, minimal_engine_output):
        result = adapter.csv_to_design_md_yaml(minimal_engine_output, include_body=True)
        body = result.get("body", "")
        assert "Hero" in body

    def test_cta_placement_in_body(self, minimal_engine_output):
        result = adapter.csv_to_design_md_yaml(minimal_engine_output, include_body=True)
        body = result.get("body", "")
        assert "CTA" in body


# ---------------------------------------------------------------------------
# TestUIReasoningCSV — ui-reasoning.csv → description gerado
# ---------------------------------------------------------------------------

class TestUIReasoningCSV:
    def test_description_present(self, minimal_engine_output):
        result = adapter.csv_to_design_md_yaml(minimal_engine_output)
        fm = result["yaml_frontmatter"]
        assert "description" in fm
        assert len(fm["description"]) > 0

    def test_description_contains_project_name(self, minimal_engine_output):
        result = adapter.csv_to_design_md_yaml(minimal_engine_output)
        fm = result["yaml_frontmatter"]
        assert "TestProject" in fm["name"]

    def test_name_ends_with_design_system(self, minimal_engine_output):
        result = adapter.csv_to_design_md_yaml(minimal_engine_output)
        fm = result["yaml_frontmatter"]
        assert "Design System" in fm["name"]


# ---------------------------------------------------------------------------
# TestStacksDir — stacks/ → Stack Notes presente quando stack identificado
# ---------------------------------------------------------------------------

class TestStacksDir:
    def test_no_stack_notes_without_stack_key(self, minimal_engine_output):
        # sem stack explícita, body pode não ter Stack Notes
        result = adapter.csv_to_design_md_yaml(minimal_engine_output, include_body=True)
        body = result.get("body", "")
        # não deve crashar; Stack Notes é opcional
        assert isinstance(body, str)

    def test_body_includes_components_section(self, minimal_engine_output):
        result = adapter.csv_to_design_md_yaml(minimal_engine_output, include_body=True)
        body = result.get("body", "")
        assert "## Components" in body


# ---------------------------------------------------------------------------
# TestEdgeCases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_colors_uses_defaults(self):
        engine = {
            "project_name": "X",
            "style": {"name": ""},
            "colors": {},
            "typography": {"heading": "Inter", "body": "Inter"},
            "pattern": {},
            "key_effects": "",
            "anti_patterns": "",
        }
        result = adapter.csv_to_design_md_yaml(engine)
        colors = result["yaml_frontmatter"]["colors"]
        assert adapter.is_valid_hex(colors["primary"])

    def test_missing_typography_uses_defaults(self):
        engine = {
            "project_name": "Y",
            "style": {"name": "Minimalism"},
            "colors": {"primary": "#111", "secondary": "#222", "background": "#fff", "text": "#000"},
            "typography": {},
            "pattern": {},
            "key_effects": "",
            "anti_patterns": "",
        }
        result = adapter.csv_to_design_md_yaml(engine)
        typo = result["yaml_frontmatter"]["typography"]
        assert typo["heading"]["fontFamily"] == "Inter"
        assert typo["body"]["fontFamily"] == "Inter"

    def test_spacing_named_scale_tokens(self, minimal_engine_output):
        result = adapter.csv_to_design_md_yaml(minimal_engine_output)
        spacing = result["yaml_frontmatter"]["spacing"]
        assert spacing.get("sm") == "8px"
        assert spacing.get("md") == "16px"
        assert len(spacing) >= 5

    def test_components_is_empty_list(self, minimal_engine_output):
        result = adapter.csv_to_design_md_yaml(minimal_engine_output)
        fm = result["yaml_frontmatter"]
        assert fm["components"] == []

    def test_version_is_string(self, minimal_engine_output):
        result = adapter.csv_to_design_md_yaml(minimal_engine_output)
        fm = result["yaml_frontmatter"]
        assert fm["version"] == "1.0"

    def test_validate_missing_primary_returns_error(self):
        engine = {"colors": {}, "typography": {"body": "Inter"}}
        err = adapter.validate_engine_output(engine)
        assert err is not None
        assert "primary" in err

    def test_validate_missing_body_font_returns_error(self):
        engine = {"colors": {"primary": "#000"}, "typography": {}}
        err = adapter.validate_engine_output(engine)
        assert err is not None
        assert "body" in err

    def test_validate_valid_output_returns_none(self, minimal_engine_output):
        err = adapter.validate_engine_output(minimal_engine_output)
        assert err is None

    def test_build_design_md_has_yaml_fence(self, minimal_engine_output):
        content = adapter.build_design_md(minimal_engine_output)
        assert content.startswith("---\n")
        assert "---\n\n" in content

    def test_cli_writes_yaml_file(self, minimal_engine_output):
        with tempfile.TemporaryDirectory() as tmpdir:
            engine_path = Path(tmpdir) / "engine.json"
            out_path = Path(tmpdir) / "out.yaml"
            engine_path.write_text(json.dumps(minimal_engine_output))

            import subprocess
            result = subprocess.run(
                [sys.executable, str(Path(__file__).parent.parent / "adapter.py"),
                 "--engine-output", str(engine_path),
                 "--out", str(out_path)],
                capture_output=True, text=True
            )
            assert result.returncode == 0
            assert out_path.exists()
            content = out_path.read_text()
            assert "primary" in content

    def test_cli_exits_1_on_missing_primary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            engine_path = Path(tmpdir) / "engine.json"
            out_path = Path(tmpdir) / "out.yaml"
            engine_path.write_text(json.dumps({"colors": {}, "typography": {"body": "Inter"}}))

            import subprocess
            result = subprocess.run(
                [sys.executable, str(Path(__file__).parent.parent / "adapter.py"),
                 "--engine-output", str(engine_path),
                 "--out", str(out_path)],
                capture_output=True, text=True
            )
            assert result.returncode == 1

    def test_cli_exits_2_on_missing_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "out.yaml"
            import subprocess
            result = subprocess.run(
                [sys.executable, str(Path(__file__).parent.parent / "adapter.py"),
                 "--engine-output", "/nonexistent/path.json",
                 "--out", str(out_path)],
                capture_output=True, text=True
            )
            assert result.returncode == 2


# ---------------------------------------------------------------------------
# TestMainDirect — testa main() diretamente (para coverage de branches)
# ---------------------------------------------------------------------------

class TestMainDirect:
    """Testa main() diretamente com sys.argv patchado para cobrir branches."""

    def test_main_success(self, minimal_engine_output, monkeypatch):
        with tempfile.TemporaryDirectory() as tmpdir:
            engine_path = Path(tmpdir) / "engine.json"
            out_path = Path(tmpdir) / "out.yaml"
            engine_path.write_text(json.dumps(minimal_engine_output))

            monkeypatch.setattr(sys, "argv", [
                "adapter.py",
                "--engine-output", str(engine_path),
                "--out", str(out_path),
                "--product-type", "SaaS",
                "--keywords", "dashboard",
            ])
            with pytest.raises(SystemExit) as exc_info:
                adapter.main()
            assert exc_info.value.code == 0
            assert out_path.exists()

    def test_main_exit_1_on_invalid_json(self, monkeypatch):
        with tempfile.TemporaryDirectory() as tmpdir:
            engine_path = Path(tmpdir) / "bad.json"
            out_path = Path(tmpdir) / "out.yaml"
            engine_path.write_text("{ not valid json }")

            monkeypatch.setattr(sys, "argv", [
                "adapter.py",
                "--engine-output", str(engine_path),
                "--out", str(out_path),
            ])
            with pytest.raises(SystemExit) as exc_info:
                adapter.main()
            assert exc_info.value.code == 1

    def test_main_exit_2_on_file_not_found(self, monkeypatch):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "out.yaml"
            monkeypatch.setattr(sys, "argv", [
                "adapter.py",
                "--engine-output", "/nonexistent/engine.json",
                "--out", str(out_path),
            ])
            with pytest.raises(SystemExit) as exc_info:
                adapter.main()
            assert exc_info.value.code == 2

    def test_main_exit_1_on_validation_error(self, monkeypatch):
        with tempfile.TemporaryDirectory() as tmpdir:
            engine_path = Path(tmpdir) / "engine.json"
            out_path = Path(tmpdir) / "out.yaml"
            engine_path.write_text(json.dumps({"colors": {}, "typography": {}}))

            monkeypatch.setattr(sys, "argv", [
                "adapter.py",
                "--engine-output", str(engine_path),
                "--out", str(out_path),
            ])
            with pytest.raises(SystemExit) as exc_info:
                adapter.main()
            assert exc_info.value.code == 1

    def test_main_exit_2_on_write_error(self, minimal_engine_output, monkeypatch):
        with tempfile.TemporaryDirectory() as tmpdir:
            engine_path = Path(tmpdir) / "engine.json"
            engine_path.write_text(json.dumps(minimal_engine_output))

            monkeypatch.setattr(sys, "argv", [
                "adapter.py",
                "--engine-output", str(engine_path),
                "--out", "/root/no-permission/out.yaml",
            ])
            with pytest.raises(SystemExit) as exc_info:
                adapter.main()
            assert exc_info.value.code == 2


# ---------------------------------------------------------------------------
# TestProductTypeForwarding — product_type deve aparecer no Overview do corpo
# ---------------------------------------------------------------------------

class TestProductTypeForwarding:
    def test_product_type_appears_in_body_overview(self, minimal_engine_output):
        # Quando category está vazia, product_type deve aparecer no Overview
        minimal_engine_output["category"] = ""
        result = adapter.csv_to_design_md_yaml(
            minimal_engine_output, include_body=True, product_type="SaaS", keywords="dashboard"
        )
        body = result.get("body", "")
        assert "SaaS" in body, "product_type deve aparecer na seção Overview quando category está vazia"

    def test_build_design_md_forwards_product_type(self, minimal_engine_output):
        minimal_engine_output["category"] = ""
        content = adapter.build_design_md(minimal_engine_output, product_type="e-commerce", keywords="luxury")
        assert "e-commerce" in content, "build_design_md deve repassar product_type ao corpo do DESIGN.md"

    def test_empty_cta_falls_back_to_surface_in_body(self, minimal_engine_output):
        # cta como string vazia deve fazer fallback para surface na tabela de cores do corpo
        minimal_engine_output["colors"]["cta"] = ""
        minimal_engine_output["colors"]["surface"] = "#FF6B35"
        result = adapter.csv_to_design_md_yaml(minimal_engine_output, include_body=True)
        body = result.get("body", "")
        assert "#FF6B35" in body, "Fallback para surface quando cta é string vazia"
        # Garante que não tem célula de hex em branco
        assert "| CTA/Accent | `` |" not in body
