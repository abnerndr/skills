#!/usr/bin/env node
/**
 * extract-tokens.cjs
 *
 * Extracts design tokens from a project's config files.
 * Reads tailwind.config.js, CSS custom properties, and design-tokens.json.
 *
 * Usage:
 *   node extract-tokens.cjs <project_path>
 *   node extract-tokens.cjs <project_path> --json  # JSON output (default)
 *
 * Output (stdout, JSON):
 *   { colors: {...}, typography: {...}, spacing: {...} }
 *
 * Exit codes: 0=success, 1=no tokens found, 2=I/O error
 */

"use strict";

const fs = require("fs");
const path = require("path");

const HEX_PATTERN = /#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})\b/g;
const CSS_VAR_COLOR = /(--(?:color|brand|primary|secondary|accent|bg|background|text|surface|border|muted)[-\w]*)\s*:\s*(#[0-9A-Fa-f]{3,6})/g;
const CSS_VAR_FONT = /(--(?:font|typeface|heading|body|sans|serif|mono)[-\w]*)\s*:\s*["']?([^;'"]+)["']?/g;
const CSS_VAR_SPACING = /(--(?:space|spacing|gap|padding|margin|size)[-\w]*)\s*:\s*([\d.]+(?:px|rem|em))/g;

function readFileSafe(filepath) {
  try {
    return fs.readFileSync(filepath, "utf-8");
  } catch {
    return null;
  }
}

function normalizeFontName(raw) {
  return raw.trim().replace(/^['"]|['"]$/g, "").split(",")[0].trim();
}

function extractBraceBlock(content, keyword) {
  const startRe = new RegExp(`\\b${keyword}\\s*:\\s*\\{`);
  const match = startRe.exec(content);
  if (!match) return null;
  const openPos = content.indexOf("{", match.index + match[0].length - 1);
  let depth = 0, i = openPos;
  while (i < content.length) {
    if (content[i] === "{") depth++;
    else if (content[i] === "}") { depth--; if (depth === 0) break; }
    i++;
  }
  return content.slice(openPos + 1, i);
}

function extractFromTailwindConfig(projectPath) {
  const result = { colors: {}, typography: {}, spacing: {} };

  const candidates = ["tailwind.config.js", "tailwind.config.ts", "tailwind.config.mjs"];
  let content = null;
  for (const c of candidates) {
    content = readFileSafe(path.join(projectPath, c));
    if (content) break;
  }
  if (!content) return result;

  // Extract colors from theme.extend.colors or theme.colors blocks (brace-depth tracking)
  const colorBlock = extractBraceBlock(content, "colors");
  if (colorBlock) {
    for (const [, key, hex] of colorBlock.matchAll(/(\w[\w-]*)\s*:\s*['"]?(#[0-9A-Fa-f]{3,6})['"]?/g)) {
      result.colors[key] = hex;
    }
  }

  // Extract font families (brace-depth tracking)
  const fontBlock = extractBraceBlock(content, "fontFamily");
  if (fontBlock) {
    for (const [, key, font] of fontBlock.matchAll(/(\w+)\s*:\s*\[?\s*['"]([^'"]+)['"]/g)) {
      result.typography[key] = normalizeFontName(font);
    }
  }

  return result;
}

function extractFromCSSFiles(projectPath) {
  const result = { colors: {}, typography: {}, spacing: {} };

  const searchDirs = ["src", "styles", "css", "assets/css", "app", "."];
  const cssExts = [".css", ".scss", ".sass"];

  const files = [];
  for (const dir of searchDirs) {
    const dirPath = path.join(projectPath, dir);
    if (!fs.existsSync(dirPath)) continue;
    try {
      const entries = fs.readdirSync(dirPath, { withFileTypes: true });
      for (const entry of entries) {
        if (entry.isFile() && cssExts.includes(path.extname(entry.name))) {
          files.push(path.join(dirPath, entry.name));
        }
      }
    } catch { /* skip */ }
  }

  for (const file of files) {
    const content = readFileSafe(file);
    if (!content) continue;

    for (const [, varName, hex] of content.matchAll(CSS_VAR_COLOR)) {
      result.colors[varName.replace(/^--/, "")] = hex;
    }

    for (const [, varName, font] of content.matchAll(CSS_VAR_FONT)) {
      result.typography[varName.replace(/^--/, "")] = normalizeFontName(font);
    }

    for (const [, varName, val] of content.matchAll(CSS_VAR_SPACING)) {
      result.spacing[varName.replace(/^--/, "")] = val;
    }
  }

  return result;
}

function extractFromDesignTokensJson(projectPath) {
  const result = { colors: {}, typography: {}, spacing: {} };

  const candidates = ["design-tokens.json", "design_tokens.json", "tokens.json"];
  let content = null;
  for (const c of candidates) {
    content = readFileSafe(path.join(projectPath, c));
    if (content) break;
  }
  if (!content) return result;

  let tokens;
  try {
    tokens = JSON.parse(content);
  } catch {
    return result;
  }

  // Support flat {name: value} and DTCG {name: {$value: ...}} formats
  function walk(obj, category, prefix) {
    if (!obj || typeof obj !== "object") return;
    for (const [key, val] of Object.entries(obj)) {
      if (typeof val === "string") {
        if (val.match(/^#[0-9A-Fa-f]{3,6}$/)) result.colors[prefix + key] = val;
        else if (category === "typography") result.typography[prefix + key] = val;
        else if (val.match(/^\d+(?:px|rem|em)$/)) result.spacing[prefix + key] = val;
      } else if (typeof val === "object" && "$value" in val) {
        const v = val.$value;
        if (typeof v === "string" && v.match(/^#[0-9A-Fa-f]{3,6}$/)) result.colors[prefix + key] = v;
        else if (typeof v === "string" && v.match(/^\d+(?:px|rem|em)$/)) result.spacing[prefix + key] = v;
        else if (typeof v === "string") result.typography[prefix + key] = v;
      } else if (typeof val === "object") {
        const cat = key.toLowerCase().includes("color") ? "color"
          : key.toLowerCase().includes("font") || key.toLowerCase().includes("typography") ? "typography"
          : key.toLowerCase().includes("spacing") || key.toLowerCase().includes("space") ? "spacing"
          : category;
        walk(val, cat, "");
      }
    }
  }

  walk(tokens, "", "");
  return result;
}

function mergeResults(...sources) {
  const merged = { colors: {}, typography: {}, spacing: {} };
  for (const src of sources) {
    Object.assign(merged.colors, src.colors);
    Object.assign(merged.typography, src.typography);
    Object.assign(merged.spacing, src.spacing);
  }
  return merged;
}

function main() {
  const args = process.argv.slice(2);
  const projectPath = args.find((a) => !a.startsWith("--"));

  if (!projectPath) {
    process.stderr.write("Usage: node extract-tokens.cjs <project_path>\n");
    process.exit(2);
  }

  const resolvedPath = path.isAbsolute(projectPath)
    ? projectPath
    : path.join(process.cwd(), projectPath);

  if (!fs.existsSync(resolvedPath)) {
    process.stderr.write(`Project path not found: ${resolvedPath}\n`);
    process.exit(2);
  }

  const fromTailwind = extractFromTailwindConfig(resolvedPath);
  const fromCSS = extractFromCSSFiles(resolvedPath);
  const fromJson = extractFromDesignTokensJson(resolvedPath);

  // Priority: JSON > Tailwind > CSS (JSON is most explicit)
  const result = mergeResults(fromCSS, fromTailwind, fromJson);

  const isEmpty =
    Object.keys(result.colors).length === 0 &&
    Object.keys(result.typography).length === 0 &&
    Object.keys(result.spacing).length === 0;

  if (isEmpty) {
    process.stderr.write("No design tokens found in project.\n");
    process.exit(1);
  }

  process.stdout.write(JSON.stringify(result, null, 2) + "\n");
  process.exit(0);
}

if (require.main === module) {
  main();
} else {
  module.exports = {
    extractFromTailwindConfig,
    extractFromCSSFiles,
    extractFromDesignTokensJson,
    mergeResults,
  };
}
