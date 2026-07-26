import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, "..");
const docsDir = path.join(rootDir, "docs_generali");
const workbookPath = path.join(docsDir, "Matrice_portali.xlsx");

const sources = [
  {
    markdownPath: path.join(docsDir, "matrice_portali_esistenti_ATK-Pro.md"),
    sheetName: "Matrice portali esistenti",
    headers: [
      "Chiave",
      "Portale",
      "Area",
      "Metodo tecnico osservato",
      "Rischio manutenzione",
      "Stato legale operativo",
      "Prossimo passo",
    ],
  },
  {
    markdownPath: path.join(docsDir, "matrice_portali_candidati_ATK-Pro.md"),
    sheetName: "Matrice portali candidati",
    headers: [
      "Chiave candidata",
      "Portale",
      "Area strategica",
      "Fonte ufficiale consultata",
      "Rilevanza genealogica",
      "Prima lettura tecnica/legale",
      "Decisione provvisoria",
    ],
  },
];

function normalizeCell(value) {
  const text = value === null || value === undefined ? "" : String(value);
  return text.replaceAll("`", "").replace(/\s+/g, " ").trim();
}

function parseMarkdownRow(line) {
  return line
    .trim()
    .replace(/^\|/, "")
    .replace(/\|$/, "")
    .split("|")
    .map((cell) => normalizeCell(cell));
}

function isSeparatorRow(row) {
  return row.every((cell) => /^:?-{3,}:?$/.test(cell));
}

async function readMarkdownTable(markdownPath, expectedHeaders) {
  const content = await fs.readFile(markdownPath, "utf8");
  const lines = content.split(/\r?\n/);
  const expected = expectedHeaders.map((header) => normalizeCell(header));

  let current = [];
  for (const line of [...lines, ""]) {
    if (line.startsWith("|")) {
      current.push(parseMarkdownRow(line));
      continue;
    }

    if (current.length > 0) {
      const header = current[0];
      if (JSON.stringify(header) === JSON.stringify(expected)) {
        return current.filter((row, index) => index === 0 || !isSeparatorRow(row));
      }
      current = [];
    }
  }

  throw new Error(`Markdown table not found in ${markdownPath}`);
}

function computeColumnWidths(rows) {
  const minWidths = [18, 28, 24, 34, 22, 26, 36];
  const maxWidths = [26, 40, 34, 48, 28, 34, 54];

  return rows[0].map((_, index) => {
    const longest = rows.reduce((max, row) => {
      const length = (row[index] || "").length;
      return Math.max(max, length);
    }, 0);
    const padded = Math.min(longest + 2, maxWidths[index] || 40);
    return Math.max(padded, minWidths[index] || 18);
  });
}

function styleHeader(range) {
  range.format = {
    fill: "#5B9BD5",
    font: { bold: true, color: "#FFFFFF" },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "all", style: "thin", color: "#D9E2F3" },
  };
}

function styleBody(range) {
  range.format = {
    horizontalAlignment: "left",
    verticalAlignment: "top",
    wrapText: true,
    borders: { preset: "all", style: "thin", color: "#D9D9D9" },
  };
}

async function buildWorkbook() {
  const workbook = Workbook.create();

  for (const source of sources) {
    const rows = await readMarkdownTable(source.markdownPath, source.headers);
    const widths = computeColumnWidths(rows);
    const sheet = workbook.worksheets.add(source.sheetName);
    sheet.showGridLines = false;
    sheet.freezePanes.freezeRows(1);
    sheet.getRange("A1:G1").values = [rows[0]];
    styleHeader(sheet.getRange("A1:G1"));

    if (rows.length > 1) {
      const dataRange = sheet.getRange(`A2:G${rows.length}`);
      dataRange.values = rows.slice(1);
      styleBody(dataRange);
    }

    const usedRange = sheet.getRange(`A1:G${rows.length}`);
    usedRange.format.autofitRows();

    widths.forEach((width, index) => {
      sheet.getRangeByIndexes(0, index, rows.length, 1).format.columnWidth = width;
    });

    sheet.getRange("A1:G1").format.rowHeight = 34;
  }

  return workbook;
}

async function main() {
  const workbook = await buildWorkbook();
  const output = await SpreadsheetFile.exportXlsx(workbook);
  await fs.rm(workbookPath, { force: true });
  await fs.rm(`${workbookPath}.inspect.ndjson`, { force: true });
  await output.save(workbookPath);
  console.log(`Workbook rebuilt: ${workbookPath}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
