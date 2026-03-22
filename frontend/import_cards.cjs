const fs = require('fs');
const path = require('path');

const SOURCE_DIR = 'e:\\小程序开发\\游戏充值网站\\酒馆500+角色卡';
const PUBLIC_DIR = path.join(__dirname, 'public');
const CHARACTERS_DIR = path.join(PUBLIC_DIR, 'characters');
const AVATARS_DIR = path.join(CHARACTERS_DIR, 'avatars');
const INDEX_FILE = path.join(CHARACTERS_DIR, 'index.json');

if (!fs.existsSync(AVATARS_DIR)) {
    fs.mkdirSync(AVATARS_DIR, { recursive: true });
}

// Simple PNG Text Chunk Reader
function extractPngMetadata(filePath) {
    try {
        const buffer = fs.readFileSync(filePath);
        let offset = 8; // Skip PNG signature
        
        while (offset < buffer.length) {
            const length = buffer.readUInt32BE(offset);
            const type = buffer.toString('ascii', offset + 4, offset + 8);
            
            if (type === 'tEXt') {
                const data = buffer.slice(offset + 8, offset + 8 + length);
                // format: keyword + null + text
                let nullIndex = -1;
                for (let i = 0; i < data.length; i++) {
                    if (data[i] === 0) {
                        nullIndex = i;
                        break;
                    }
                }
                if (nullIndex !== -1) {
                    const keyword = data.toString('ascii', 0, nullIndex);
                    const text = data.toString('utf8', nullIndex + 1); // Latin1 usually but try utf8
                    
                    if (keyword === 'chara') {
                        return Buffer.from(text, 'base64').toString('utf-8');
                    }
                }
            }
            
            offset += 12 + length; // Length + Type + Data + CRC
        }
    } catch (e) {
        // console.error(`Error reading PNG ${filePath}:`, e.message);
    }
    return null;
}

const newCharacters = [];
const processedNames = new Set();

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
            if (ext === '.png') {
                const filename = path.basename(file, ext);
                // Skip if already processed
                if (processedNames.has(filename)) continue;
                
                // Try to extract metadata
                let charData = null;
                const rawMeta = extractPngMetadata(fullPath);
                if (rawMeta) {
                    try {
                        charData = JSON.parse(rawMeta);
                    } catch (e) {
                        // console.error('Failed to parse JSON from PNG', e);
                    }
                }
                
                // Construct Character Object
                const id = require('crypto').createHash('md5').update(filename + Date.now()).digest('hex');
                const safeName = filename; // Use filename as it's likely Chinese
                
                const charObj = {
                    id: id,
                    name: safeName, // Prefer filename as it matches user intent
                    description: charData?.description || charData?.data?.description || `Character: ${safeName}`,
                    avatar: `/characters/avatars/${filename}.png`,
                    systemPrompt: charData?.data?.system_prompt || charData?.system_prompt || 
                                  charData?.data?.post_history_instructions || 
                                  `You are ${safeName}.`,
                    firstMessage: charData?.first_mes || charData?.data?.first_mes || '',
                    // Keep original file mapping just in case
                    originalFile: fullPath
                };
                
                // Copy Image
                const destPath = path.join(AVATARS_DIR, `${filename}.png`);
                try {
                    fs.copyFileSync(fullPath, destPath);
                    newCharacters.push(charObj);
                    processedNames.add(filename);
                    console.log(`Imported: ${safeName}`);
                } catch (e) {
                    console.error(`Failed to copy ${fullPath}`, e);
                }
            }
        }
    }
}

console.log('Starting import from:', SOURCE_DIR);
walkDir(SOURCE_DIR);

if (newCharacters.length > 0) {
    fs.writeFileSync(INDEX_FILE, JSON.stringify(newCharacters, null, 2), 'utf-8');
    console.log(`Successfully imported ${newCharacters.length} characters to index.json`);
} else {
    console.log('No characters found.');
}
