#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const zlib = require("zlib");

const SOURCE_DIR_NAME = "\u6e38\u620f\u89d2\u8272\u5361";
const TARGET_GROUP = "\u6e38\u620f\u5c0f\u8bf4\u597d\u53cb";
const IMPORT_SOURCE = "game_novel_cards";

const frontendRoot = path.resolve(__dirname, "..");
const workspaceRoot = path.resolve(frontendRoot, "..");
const sourceDir = path.join(workspaceRoot, SOURCE_DIR_NAME);
const charactersDir = path.join(frontendRoot, "public", "characters");
const avatarsDir = path.join(charactersDir, "avatars");
const indexPath = path.join(charactersDir, "index.json");

const PNG_SIGNATURE = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);

function ensureDir(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

function readPngTextChunks(filePath) {
  const buffer = fs.readFileSync(filePath);
  if (buffer.length < 8 || !buffer.subarray(0, 8).equals(PNG_SIGNATURE)) {
    return [];
  }

  const chunks = [];
  let offset = 8;
  while (offset + 8 <= buffer.length) {
    const length = buffer.readUInt32BE(offset);
    const type = buffer.toString("ascii", offset + 4, offset + 8);
    const dataStart = offset + 8;
    const dataEnd = dataStart + length;
    if (dataEnd + 4 > buffer.length) break;
    const data = buffer.subarray(dataStart, dataEnd);
    chunks.push({ type, data });
    offset = dataEnd + 4;
  }
  return chunks;
}

function parseTEXt(data) {
  const sep = data.indexOf(0);
  if (sep <= 0) return null;
  return {
    keyword: data.subarray(0, sep).toString("latin1"),
    text: data.subarray(sep + 1).toString("latin1")
  };
}

function parseZTXt(data) {
  const sep = data.indexOf(0);
  if (sep <= 0 || sep + 2 > data.length) return null;
  const keyword = data.subarray(0, sep).toString("latin1");
  const compressed = data.subarray(sep + 2);
  try {
    const text = zlib.inflateSync(compressed).toString("utf8");
    return { keyword, text };
  } catch {
    return null;
  }
}

function parseITXt(data) {
  const keywordEnd = data.indexOf(0);
  if (keywordEnd <= 0 || keywordEnd + 3 > data.length) return null;

  const keyword = data.subarray(0, keywordEnd).toString("utf8");
  const compressedFlag = data[keywordEnd + 1];
  let cursor = keywordEnd + 3;

  const languageEnd = data.indexOf(0, cursor);
  if (languageEnd < 0) return null;
  cursor = languageEnd + 1;

  const translatedEnd = data.indexOf(0, cursor);
  if (translatedEnd < 0) return null;
  cursor = translatedEnd + 1;

  const textBytes = data.subarray(cursor);
  try {
    const text =
      compressedFlag === 1
        ? zlib.inflateSync(textBytes).toString("utf8")
        : textBytes.toString("utf8");
    return { keyword, text };
  } catch {
    return null;
  }
}

function tryParseCharacterPayload(rawText) {
  if (!rawText || typeof rawText !== "string") return null;
  const trimmed = rawText.trim();
  if (!trimmed) return null;

  const attempts = [];
  attempts.push(trimmed);

  if (/^[A-Za-z0-9+/=\r\n]+$/.test(trimmed) && trimmed.length >= 32) {
    try {
      attempts.unshift(Buffer.from(trimmed.replace(/\s+/g, ""), "base64").toString("utf8"));
    } catch {
      // ignore
    }
  }

  for (const candidate of attempts) {
    try {
      return JSON.parse(candidate);
    } catch {
      // continue
    }
  }

  return null;
}

function extractCharacterCardFromPng(filePath) {
  const chunks = readPngTextChunks(filePath);
  for (const chunk of chunks) {
    let parsed = null;
    if (chunk.type === "tEXt") parsed = parseTEXt(chunk.data);
    if (chunk.type === "zTXt") parsed = parseZTXt(chunk.data);
    if (chunk.type === "iTXt") parsed = parseITXt(chunk.data);
    if (!parsed) continue;
    if (parsed.keyword !== "chara") continue;

    const payload = tryParseCharacterPayload(parsed.text);
    if (payload) return payload;
  }
  return null;
}

function listPngFiles(dirPath) {
  if (!fs.existsSync(dirPath)) return [];
  const result = [];

  function walk(current) {
    const entries = fs.readdirSync(current, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(current, entry.name);
      if (entry.isDirectory()) {
        walk(fullPath);
        continue;
      }
      if (entry.isFile() && path.extname(entry.name).toLowerCase() === ".png") {
        result.push(fullPath);
      }
    }
  }

  walk(dirPath);
  return result;
}

function pick(...values) {
  for (const value of values) {
    if (typeof value === "string" && value.trim()) return value.trim();
  }
  return "";
}

function loadIndex() {
  if (!fs.existsSync(indexPath)) return [];
  try {
    const parsed = JSON.parse(fs.readFileSync(indexPath, "utf8"));
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function main() {
  if (!fs.existsSync(sourceDir)) {
    throw new Error(`source directory not found: ${sourceDir}`);
  }

  ensureDir(charactersDir);
  ensureDir(avatarsDir);

  const existingIndex = loadIndex();
  const pngFiles = listPngFiles(sourceDir);
  const imported = [];

  for (const filePath of pngFiles) {
    const card = extractCharacterCardFromPng(filePath);
    const baseName = path.basename(filePath, path.extname(filePath));
    const id = crypto
      .createHash("md5")
      .update(`game_novel:${path.relative(workspaceRoot, filePath).toLowerCase()}`)
      .digest("hex");

    const avatarFile = `${id}.png`;
    const avatarDest = path.join(avatarsDir, avatarFile);
    fs.copyFileSync(filePath, avatarDest);

    const name = pick(card?.name, card?.data?.name, baseName);
    const description = pick(
      card?.description,
      card?.data?.description,
      card?.personality,
      card?.data?.personality,
      `Character: ${name}`
    );
    const systemPrompt = pick(
      card?.data?.system_prompt,
      card?.system_prompt,
      card?.systemPrompt,
      card?.data?.post_history_instructions,
      card?.data?.personality,
      card?.personality,
      `You are ${name}.`
    );
    const firstMessage = pick(
      card?.first_mes,
      card?.data?.first_mes,
      card?.mes_example,
      card?.data?.mes_example
    );

    imported.push({
      id,
      name,
      description,
      avatar: `/characters/avatars/${avatarFile}`,
      systemPrompt,
      firstMessage,
      originalFile: filePath,
      group: TARGET_GROUP,
      importSource: IMPORT_SOURCE
    });
  }

  const filteredExisting = existingIndex.filter((item) => {
    if (!item || typeof item !== "object") return false;
    if (item.importSource === IMPORT_SOURCE) return false;
    if (typeof item.group === "string" && item.group === TARGET_GROUP) return false;
    if (typeof item.originalFile === "string" && item.originalFile.includes(SOURCE_DIR_NAME)) return false;
    return true;
  });

  const merged = [...imported, ...filteredExisting];
  fs.writeFileSync(indexPath, JSON.stringify(merged, null, 2) + "\n", "utf8");

  console.log(`[import-game-novel-cards] source: ${sourceDir}`);
  console.log(`[import-game-novel-cards] imported png cards: ${imported.length}`);
  console.log(`[import-game-novel-cards] index: ${existingIndex.length} -> ${merged.length}`);
  console.log(`[import-game-novel-cards] group: ${TARGET_GROUP}`);
}

main();
