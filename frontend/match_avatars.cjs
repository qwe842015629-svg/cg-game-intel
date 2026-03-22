const fs = require('fs');
const path = require('path');

const CHARACTERS_DIR = path.join(__dirname, 'public/characters');
const INDEX_FILE = path.join(CHARACTERS_DIR, 'index.json');
const AVATARS_DIR = path.join(CHARACTERS_DIR, 'avatars');
const SOURCE_DIR = 'e:\\小程序开发\\游戏充值网站\\酒馆500+角色卡';

if (!fs.existsSync(AVATARS_DIR)) {
    fs.mkdirSync(AVATARS_DIR, { recursive: true });
}

// 1. Load Character Index
const characters = JSON.parse(fs.readFileSync(INDEX_FILE, 'utf-8'));
console.log(`Loaded ${characters.length} characters from index.`);

// 2. Build Map of Potential Images from Source
// We will store paths keyed by "normalized name"
const imageMap = new Map();

function walkDir(dir) {
    if (!fs.existsSync(dir)) return;
    const files = fs.readdirSync(dir);
    for (const file of files) {
        const fullPath = path.join(dir, file);
        const stat = fs.statSync(fullPath);
        if (stat.isDirectory()) {
            walkDir(fullPath);
        } else {
            const ext = path.extname(file).toLowerCase();
            if (['.png', '.jpg', '.jpeg', '.webp'].includes(ext)) {
                // Key strategies:
                // 1. File name without extension (e.g., "Alice.png" -> "Alice")
                const nameFromBase = path.basename(file, ext);
                
                // 2. Parent folder name (e.g., "Alice/001.png" -> "Alice")
                const parentDir = path.basename(path.dirname(fullPath));
                
                // Store paths
                // We prefer exact matches on filename first, then folder name
                
                if (!imageMap.has(nameFromBase)) imageMap.set(nameFromBase, []);
                imageMap.get(nameFromBase).push(fullPath);

                if (!imageMap.has(parentDir)) imageMap.set(parentDir, []);
                imageMap.get(parentDir).push(fullPath);
            }
        }
    }
}

console.log('Scanning source directory for images...');
walkDir(SOURCE_DIR);
console.log(`Found potential matches for ${imageMap.size} unique names/folders.`);
console.log('Available keys:', [...imageMap.keys()].join(', '));

// 3. Match and Copy
let updatedCount = 0;

for (const char of characters) {
    const charName = char.name;
    // Try to find a match
    let bestMatchPath = null;
    
    // Strategy 1: Exact Name Match
    if (imageMap.has(charName)) {
        const candidates = imageMap.get(charName);
        // Sort by file size (assuming larger is better quality/original) or just take first
        candidates.sort((a, b) => fs.statSync(b).size - fs.statSync(a).size);
        bestMatchPath = candidates[0];
    } 
    // Strategy 2: Partial Match (if needed, but risky)
    else {
        // iterate all keys
        for (const key of imageMap.keys()) {
            if (key.includes(charName) || charName.includes(key)) {
                // check similarity?
                if (key.length > 1 && charName.length > 1) {
                     // simplified fuzzy match
                }
            }
        }
    }

    if (bestMatchPath) {
        const ext = path.extname(bestMatchPath);
        const newFileName = `${char.id}${ext}`;
        const destPath = path.join(AVATARS_DIR, newFileName);
        
        fs.copyFileSync(bestMatchPath, destPath);
        
        // Update character record
        char.avatar = `/characters/avatars/${newFileName}`;
        updatedCount++;
        console.log(`Matched [${charName}] -> ${bestMatchPath}`);
    } else {
        console.log(`No match found for [${charName}]`);
        // Keep DiceBear or set to default? 
        // User hates DiceBear. Maybe set to a placeholder if really not found?
        // For now, keep as is to avoid broken images if DiceBear works at least.
    }
}

// 4. Save Index
fs.writeFileSync(INDEX_FILE, JSON.stringify(characters, null, 2), 'utf-8');
console.log(`Updated ${updatedCount} characters. Saved to index.json.`);
