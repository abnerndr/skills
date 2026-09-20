"use strict";
/**
 * Tests for extract-tokens.cjs
 * Run: node --test tests/test_extract_tokens.test.js
 * (Node 18+ built-in test runner)
 */

const { describe, it, before, after, beforeEach, afterEach } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const path = require("path");
const os = require("os");

const {
  extractFromTailwindConfig,
  extractFromCSSFiles,
  extractFromDesignTokensJson,
  mergeResults,
} = require("../extract-tokens.cjs");

function makeTmpDir() {
  return fs.mkdtempSync(path.join(os.tmpdir(), "extract-tokens-test-"));
}

function removeTmpDir(dir) {
  fs.rmSync(dir, { recursive: true, force: true });
}

// ---------------------------------------------------------------------------
// extractFromTailwindConfig
// ---------------------------------------------------------------------------

describe("extractFromTailwindConfig", () => {
  let tmpDir;

  beforeEach(() => { tmpDir = makeTmpDir(); });
  afterEach(() => { removeTmpDir(tmpDir); });

  it("retorna objeto vazio quando nenhum tailwind.config existe", () => {
    const result = extractFromTailwindConfig(tmpDir);
    assert.deepEqual(result, { colors: {}, typography: {}, spacing: {} });
  });

  it("extrai cores do bloco theme.extend.colors (flat)", () => {
    fs.writeFileSync(
      path.join(tmpDir, "tailwind.config.js"),
      `module.exports = { theme: { extend: { colors: { primary: '#1466C3', secondary: '#FF6B35' } } } };`
    );
    const result = extractFromTailwindConfig(tmpDir);
    assert.equal(result.colors.primary, "#1466C3");
    assert.equal(result.colors.secondary, "#FF6B35");
  });

  it("extrai cores de objetos aninhados (shade scales)", () => {
    fs.writeFileSync(
      path.join(tmpDir, "tailwind.config.js"),
      `module.exports = { theme: { colors: { brand: { primary: '#1466C3', secondary: '#FF6B35' }, gray: { 500: '#9CA3AF' } } } };`
    );
    const result = extractFromTailwindConfig(tmpDir);
    assert.equal(result.colors.primary, "#1466C3", "brand.primary deve ser extraído");
    assert.equal(result.colors.secondary, "#FF6B35", "brand.secondary deve ser extraído");
    assert.equal(result.colors["500"], "#9CA3AF", "gray.500 deve ser extraído (segundo objeto aninhado)");
  });

  it("extrai fontFamily do config", () => {
    fs.writeFileSync(
      path.join(tmpDir, "tailwind.config.js"),
      `module.exports = { theme: { fontFamily: { heading: ['Rubik', 'sans-serif'], body: ['Inter', 'sans-serif'] } } };`
    );
    const result = extractFromTailwindConfig(tmpDir);
    assert.equal(result.typography.heading, "Rubik");
    assert.equal(result.typography.body, "Inter");
  });

  it("lê tailwind.config.ts como alternativa", () => {
    fs.writeFileSync(
      path.join(tmpDir, "tailwind.config.ts"),
      `export default { theme: { extend: { colors: { brand: '#AABBCC' } } } };`
    );
    const result = extractFromTailwindConfig(tmpDir);
    assert.equal(result.colors.brand, "#AABBCC");
  });

  it("ignora cores sem valor hex válido", () => {
    fs.writeFileSync(
      path.join(tmpDir, "tailwind.config.js"),
      `module.exports = { theme: { extend: { colors: { primary: 'blue', danger: '#FF0000' } } } };`
    );
    const result = extractFromTailwindConfig(tmpDir);
    assert.ok(!("primary" in result.colors), "cor nomeada 'blue' não deve ser extraída");
    assert.equal(result.colors.danger, "#FF0000");
  });
});

// ---------------------------------------------------------------------------
// extractFromCSSFiles
// ---------------------------------------------------------------------------

describe("extractFromCSSFiles", () => {
  let tmpDir;

  beforeEach(() => { tmpDir = makeTmpDir(); });
  afterEach(() => { removeTmpDir(tmpDir); });

  it("retorna objeto vazio quando nenhum CSS existe", () => {
    const result = extractFromCSSFiles(tmpDir);
    assert.deepEqual(result, { colors: {}, typography: {}, spacing: {} });
  });

  it("extrai cor de CSS custom property com prefixo --color-*", () => {
    const stylesDir = path.join(tmpDir, "styles");
    fs.mkdirSync(stylesDir);
    fs.writeFileSync(
      path.join(stylesDir, "globals.css"),
      `:root {\n  --color-primary: #1466C3;\n  --color-background: #F6F5FA;\n}\n`
    );
    const result = extractFromCSSFiles(tmpDir);
    assert.equal(result.colors["color-primary"], "#1466C3");
    assert.equal(result.colors["color-background"], "#F6F5FA");
  });

  it("extrai spacing de CSS custom property com prefixo --space-*", () => {
    const stylesDir = path.join(tmpDir, "src");
    fs.mkdirSync(stylesDir);
    fs.writeFileSync(
      path.join(stylesDir, "tokens.css"),
      `:root {\n  --space-4: 16px;\n  --spacing-base: 8px;\n}\n`
    );
    const result = extractFromCSSFiles(tmpDir);
    assert.ok(
      result.spacing["space-4"] === "16px" || result.spacing["spacing-base"] === "8px",
      "deve extrair ao menos um token de spacing"
    );
  });

  it("ignora propriedades CSS sem prefixo semântico reconhecido", () => {
    const stylesDir = path.join(tmpDir, "styles");
    fs.mkdirSync(stylesDir);
    fs.writeFileSync(
      path.join(stylesDir, "misc.css"),
      `:root {\n  --arbitrary-internal: #DEADBE;\n}\n`
    );
    const result = extractFromCSSFiles(tmpDir);
    assert.deepEqual(result.colors, {}, "hex sem prefixo semântico não deve ser extraído via CSS_VAR_COLOR");
  });

  it("dois CSS vars com mesmo hex são armazenados separadamente", () => {
    const stylesDir = path.join(tmpDir, "styles");
    fs.mkdirSync(stylesDir);
    fs.writeFileSync(
      path.join(stylesDir, "tokens.css"),
      `:root {\n  --color-primary: #2563EB;\n  --color-link: #2563EB;\n}\n`
    );
    const result = extractFromCSSFiles(tmpDir);
    assert.equal(result.colors["color-primary"], "#2563EB", "color-primary deve ser registrado");
    assert.equal(result.colors["color-link"], "#2563EB", "color-link também deve ser registrado (mesmo hex)");
  });

  it("spacing com valor decimal (1.5rem) armazena var name correto", () => {
    const stylesDir = path.join(tmpDir, "styles");
    fs.mkdirSync(stylesDir);
    fs.writeFileSync(
      path.join(stylesDir, "spacing.css"),
      `:root {\n  --space-md: 1.5rem;\n  --space-lg: 2rem;\n}\n`
    );
    const result = extractFromCSSFiles(tmpDir);
    assert.ok(result.spacing["space-md"] === "1.5rem" || result.spacing["space-lg"] === "2rem",
      "tokens de spacing com valor decimal devem ser extraídos com var name correto");
  });
});

// ---------------------------------------------------------------------------
// extractFromDesignTokensJson
// ---------------------------------------------------------------------------

describe("extractFromDesignTokensJson", () => {
  let tmpDir;

  beforeEach(() => { tmpDir = makeTmpDir(); });
  afterEach(() => { removeTmpDir(tmpDir); });

  it("retorna objeto vazio quando nenhum JSON existe", () => {
    const result = extractFromDesignTokensJson(tmpDir);
    assert.deepEqual(result, { colors: {}, typography: {}, spacing: {} });
  });

  it("extrai cores de formato flat {name: '#hex'}", () => {
    fs.writeFileSync(
      path.join(tmpDir, "design-tokens.json"),
      JSON.stringify({ primary: "#1466C3", secondary: "#FF6B35" })
    );
    const result = extractFromDesignTokensJson(tmpDir);
    assert.equal(result.colors.primary, "#1466C3");
    assert.equal(result.colors.secondary, "#FF6B35");
  });

  it("extrai cores de formato W3C DTCG {$value: '#hex'}", () => {
    fs.writeFileSync(
      path.join(tmpDir, "design-tokens.json"),
      JSON.stringify({
        colors: {
          primary: { $value: "#1466C3", $type: "color" },
          background: { $value: "#F6F5FA", $type: "color" },
        },
      })
    );
    const result = extractFromDesignTokensJson(tmpDir);
    assert.equal(result.colors.primary, "#1466C3");
    assert.equal(result.colors.background, "#F6F5FA");
  });

  it("extrai spacing de formato W3C DTCG", () => {
    fs.writeFileSync(
      path.join(tmpDir, "tokens.json"),
      JSON.stringify({
        spacing: {
          base: { $value: "8px" },
          lg: { $value: "24px" },
        },
      })
    );
    const result = extractFromDesignTokensJson(tmpDir);
    assert.equal(result.spacing.base, "8px");
    assert.equal(result.spacing.lg, "24px");
  });

  it("retorna objeto vazio para JSON malformado", () => {
    fs.writeFileSync(path.join(tmpDir, "design-tokens.json"), "{ invalid json }");
    const result = extractFromDesignTokensJson(tmpDir);
    assert.deepEqual(result, { colors: {}, typography: {}, spacing: {} });
  });

  it("lê design_tokens.json como alternativa a design-tokens.json", () => {
    fs.writeFileSync(
      path.join(tmpDir, "design_tokens.json"),
      JSON.stringify({ brand: "#AABBCC" })
    );
    const result = extractFromDesignTokensJson(tmpDir);
    assert.equal(result.colors.brand, "#AABBCC");
  });
});

// ---------------------------------------------------------------------------
// mergeResults — prioridade: JSON > Tailwind > CSS
// ---------------------------------------------------------------------------

describe("mergeResults", () => {
  it("mescla múltiplas fontes de tokens", () => {
    const css = { colors: { primary: "#CSS" }, typography: {}, spacing: {} };
    const tailwind = { colors: { primary: "#TAILWIND", secondary: "#FF0000" }, typography: {}, spacing: {} };
    const json = { colors: { primary: "#JSON" }, typography: {}, spacing: {} };

    // Ordem: CSS, Tailwind, JSON — cada um sobrescreve o anterior
    const result = mergeResults(css, tailwind, json);
    assert.equal(result.colors.primary, "#JSON", "JSON deve ter prioridade sobre Tailwind e CSS");
    assert.equal(result.colors.secondary, "#FF0000", "campos do Tailwind preservados quando JSON não conflita");
  });

  it("combina typography e spacing de fontes distintas", () => {
    const a = { colors: {}, typography: { heading: "Rubik" }, spacing: {} };
    const b = { colors: {}, typography: {}, spacing: { base: "8px" } };
    const result = mergeResults(a, b);
    assert.equal(result.typography.heading, "Rubik");
    assert.equal(result.spacing.base, "8px");
  });

  it("retorna estrutura completa mesmo sem tokens", () => {
    const result = mergeResults(
      { colors: {}, typography: {}, spacing: {} },
      { colors: {}, typography: {}, spacing: {} }
    );
    assert.deepEqual(result, { colors: {}, typography: {}, spacing: {} });
  });
});
