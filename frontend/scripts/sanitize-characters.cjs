#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const projectRoot = path.resolve(__dirname, "..");
const charactersDir = path.join(projectRoot, "public", "characters");
const indexPath = path.join(charactersDir, "index.json");
const reportPath = path.join(charactersDir, "sanitize-report.json");

function buildRegex(terms) {
  return new RegExp(terms.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|"), "i");
}

const FORCE_KEEP_IDS = new Set([
  "00528540f936a1be53d7328db3ba6ccd"
]);

const FORCE_KEEP_NAMES = new Set([
  "崩坏星穹铁道"
]);

const BL_STANDALONE = /(?:^|[^a-z])bl(?:[^a-z]|$)/i;

const PATTERNS = {
  erotic: buildRegex([
    "色情", "情色", "性描写", "性行为", "性爱", "性交", "做爱", "口交", "肛交", "手淫", "自慰",
    "调教", "催情", "媚药", "约炮", "网黄", "性癖", "xp向", "个人xp", "不合xp", "xp大乱炖",
    "r18", "nsfw", "smut", "porn", "sex", "bdsm", "dom/sub", "kink", "fetish", "ntr"
  ]),
  bl: buildRegex(["耽美", "男同", "男男", "腐向", "yaoi", "danmei", "boys love", "boyslove"]),
  unethical: buildRegex([
    "不道德", "违背伦理", "伦理禁忌", "乱伦", "骨科", "近亲", "有血缘", "亲兄妹", "亲姐弟", "父女", "母子",
    "叔侄", "姑侄", "舅甥", "姨甥", "继母", "后妈", "继子", "继女", "stepmom", "stepmother",
    "step mother", "incest", "出轨", "婚外情", "小三", "诱奸", "迷奸", "强迫关系", "非自愿"
  ]),
  crime: buildRegex([
    "犯罪", "违法", "黑帮", "帮派", "毒品", "吸毒", "贩毒", "制毒", "洗钱", "诈骗", "勒索", "绑架", "拐卖",
    "人口贩卖", "走私", "枪击", "抢劫", "谋杀", "连环杀手", "杀手", "越狱", "犯罪集团", "犯罪组织",
    "homicide", "mafia", "cartel", "kidnap", "fraud"
  ]),
  violence: buildRegex([
    "暴力", "血腥", "虐杀", "分尸", "肢解", "酷刑", "折磨", "凌虐", "殴打", "施暴", "屠杀", "杀戮", "灭门",
    "追杀", "刺杀", "自残", "gore", "dismember", "behead", "torture", "slaughter", "bloodplay"
  ]),
  minorSexual: buildRegex([
    "未成年性", "儿童色情", "恋童", "幼交", "幼女", "正太", "萝莉", "child porn", "csam", "underage sex"
  ]),
  harmfulTone: buildRegex([
    "正则", "regex", "霸凌", "校园霸凌", "侮辱", "羞辱", "辱骂", "脏话", "黑暗", "阴暗", "阴郁", "病娇",
    "奴仆", "奴隶", "仆从", "仆人", "主仆", "臣服", "奴性", "跪下", "狗链", "slave", "servant",
    "humiliation", "bully", "bullying", "toxic relationship"
  ]),
  edgeRisk: buildRegex([
    "黑化", "复仇", "报复", "仇恨", "病态", "操控", "精神控制", "洗脑", "驯化", "控制欲", "占有欲",
    "极端关系", "扭曲关系", "反社会", "权谋", "阴谋", "dark romance", "obsessive", "manipulation"
  ]),
  copyrightNotice: buildRegex([
    "版权", "著作权", "作者声明", "仅供学习", "禁止转载", "谢绝转载", "二传", "二改", "商用禁止",
    "侵删", "请勿搬运", "未经许可", "all rights reserved", "copyright", "do not repost",
    "for personal use only", "author note"
  ]),
  whitelistSafe: buildRegex([
    "百科", "wiki", "攻略", "教程", "学习", "教育", "科普", "编程", "算法", "开发", "文档", "工具",
    "客服", "充值", "商城", "资讯", "新闻", "知识库", "guide", "manual", "reference"
  ])
};

const HARD_REASONS = [
  "erotic",
  "bl",
  "unethical",
  "crime",
  "violence",
  "minor_sexual",
  "harmful_tone",
  "copyright_notice"
];

function safeString(value) {
  return typeof value === "string" ? value : "";
}

function collectEntryText(entry) {
  return [
    safeString(entry.name),
    safeString(entry.description),
    safeString(entry.systemPrompt),
    safeString(entry.firstMessage)
  ].join("\n");
}

function collectStringsDeep(value, bucket, depth = 0) {
  if (depth > 12) return;
  if (typeof value === "string") {
    bucket.push(value);
    return;
  }
  if (Array.isArray(value)) {
    for (const item of value) collectStringsDeep(item, bucket, depth + 1);
    return;
  }
  if (value && typeof value === "object") {
    for (const key of Object.keys(value)) collectStringsDeep(value[key], bucket, depth + 1);
  }
}

function detectReasons(text) {
  const reasons = [];
  if (PATTERNS.erotic.test(text)) reasons.push("erotic");
  if (PATTERNS.bl.test(text) || BL_STANDALONE.test(text)) reasons.push("bl");
  if (PATTERNS.unethical.test(text)) reasons.push("unethical");
  if (PATTERNS.crime.test(text)) reasons.push("crime");
  if (PATTERNS.violence.test(text)) reasons.push("violence");
  if (PATTERNS.minorSexual.test(text)) reasons.push("minor_sexual");
  if (PATTERNS.harmfulTone.test(text)) reasons.push("harmful_tone");
  if (PATTERNS.edgeRisk.test(text)) reasons.push("edge_risk");
  if (PATTERNS.copyrightNotice.test(text)) reasons.push("copyright_notice");
  return reasons;
}

function isWhitelisted(text) {
  return PATTERNS.whitelistSafe.test(text);
}

function isForceKept(entry) {
  const id = safeString(entry?.id);
  const name = safeString(entry?.name);
  return FORCE_KEEP_IDS.has(id) || FORCE_KEEP_NAMES.has(name);
}

function shouldRemove(reasons, whitelisted) {
  if (reasons.some((r) => HARD_REASONS.includes(r))) return true;
  if (reasons.includes("edge_risk") && !whitelisted) return true;
  return false;
}

function createReasonCounter() {
  return {
    erotic: 0,
    bl: 0,
    unethical: 0,
    crime: 0,
    violence: 0,
    minor_sexual: 0,
    harmful_tone: 0,
    edge_risk: 0,
    copyright_notice: 0
  };
}

function sanitizeIndex() {
  const indexData = JSON.parse(fs.readFileSync(indexPath, "utf8"));
  const kept = [];
  const removed = [];
  const retainedByWhitelist = [];
  const reasonCount = createReasonCounter();

  for (const entry of indexData) {
    if (isForceKept(entry)) {
      kept.push(entry);
      continue;
    }

    const text = collectEntryText(entry);
    const reasons = detectReasons(text);
    const whitelisted = isWhitelisted(text);
    const remove = shouldRemove(reasons, whitelisted);

    if (remove) {
      for (const reason of reasons) {
        if (Object.prototype.hasOwnProperty.call(reasonCount, reason)) reasonCount[reason] += 1;
      }
      removed.push({
        id: entry.id,
        name: entry.name,
        group: entry.group || "",
        reasons,
        whitelisted
      });
      continue;
    }

    if (reasons.includes("edge_risk") && whitelisted) {
      retainedByWhitelist.push({
        id: entry.id,
        name: entry.name,
        group: entry.group || "",
        reasons
      });
    }
    kept.push(entry);
  }

  fs.writeFileSync(indexPath, JSON.stringify(kept, null, 2) + "\n", "utf8");

  return {
    indexOriginalCount: indexData.length,
    indexRemovedCount: removed.length,
    indexRemainingCount: kept.length,
    retainedByWhitelistCount: retainedByWhitelist.length,
    reasonCount,
    removed,
    retainedByWhitelist
  };
}

function cleanupCharacterJsonFiles() {
  const files = fs
    .readdirSync(charactersDir)
    .filter((file) => file.endsWith(".json") && file !== "index.json" && file !== "sanitize-report.json");

  let deletedFileCount = 0;
  const deletedFiles = [];
  const parseErrors = [];

  for (const fileName of files) {
    const fullPath = path.join(charactersDir, fileName);
    let parsed;
    try {
      parsed = JSON.parse(fs.readFileSync(fullPath, "utf8"));
    } catch (error) {
      parseErrors.push({ file: fileName, error: error.message });
      continue;
    }

    const textBucket = [];
    collectStringsDeep(parsed, textBucket);
    const text = textBucket.join("\n");
    if (isForceKept(parsed)) continue;
    const reasons = detectReasons(text);
    const remove = shouldRemove(reasons, isWhitelisted(text));
    if (!remove) continue;

    fs.unlinkSync(fullPath);
    deletedFileCount += 1;
    deletedFiles.push({
      file: fileName,
      id: safeString(parsed.id) || path.basename(fileName, ".json"),
      name: safeString(parsed.name) || "removed",
      reasons
    });
  }

  return {
    scannedFileCount: files.length,
    deletedFileCount,
    deletedFiles,
    parseErrors
  };
}

function main() {
  if (!fs.existsSync(indexPath)) {
    throw new Error(`index.json not found: ${indexPath}`);
  }

  const indexResult = sanitizeIndex();
  const fileResult = cleanupCharacterJsonFiles();

  const report = {
    generatedAt: new Date().toISOString(),
    policyVersion: "whitelist_blacklist_v3",
    ...indexResult,
    ...fileResult
  };

  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + "\n", "utf8");

  console.log(
    `[sanitize-characters] index: ${report.indexOriginalCount} -> ${report.indexRemainingCount} (removed ${report.indexRemovedCount})`
  );
  console.log(`[sanitize-characters] whitelist-retained edge cases: ${report.retainedByWhitelistCount}`);
  console.log(`[sanitize-characters] character files deleted: ${report.deletedFileCount}/${report.scannedFileCount}`);
  console.log(`[sanitize-characters] report: ${path.relative(projectRoot, reportPath)}`);
}

main();
