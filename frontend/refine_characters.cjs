const fs = require('fs');
const path = require('path');

const CHARACTERS_DIR = path.join(__dirname, 'public/characters');
const INDEX_FILE = path.join(CHARACTERS_DIR, 'index.json');

const characters = JSON.parse(fs.readFileSync(INDEX_FILE, 'utf-8'));
let updatedCount = 0;
const namesSeen = new Set();
const finalCharacters = [];

for (const char of characters) {
    let newName = char.name;
    
    // 1. Fix Date Names or Long Tagged Names
    if (/^\d{4}-\d{2}-\d{2}/.test(char.name) || char.name.length > 10 || /[【\[]/.test(char.name)) {
        // Try to find name in description
        const nameMatch = char.description.match(/(?:Name|姓名)(?:\s*[(（]Name[)）])?[:：]\s*([^\r\n]+)/i);
        if (nameMatch) {
            newName = nameMatch[1].trim();
            // Clean up if extraction captured too much (e.g. "Name: Alice Gender: F")
            newName = newName.split(/[ ：:，,]/)[0];
            if (newName.length > 15) newName = newName.substring(0, 15);
            
            console.log(`Extracted Name [${char.name}] -> [${newName}]`);
        } else {
            // If no name in description, try to clean the filename
            // Remove content in brackets 【】 [] ()
            let cleanName = char.name
                .replace(/【.*?】/g, '')
                .replace(/\[.*?\]/g, '')
                .replace(/（.*?）/g, '')
                .replace(/\(.*?\)/g, '')
                .replace(/^\d{4}-\d{2}-\d{2}.*?/, '') // Remove dates
                .replace(/[+＋|｜]/g, '') // Remove separators
                .trim();
            
            // If result is empty or too short, keep original or part of it
            if (cleanName.length > 0 && cleanName.length < 20) {
                 newName = cleanName;
                 console.log(`Cleaned Filename [${char.name}] -> [${newName}]`);
            } else if (cleanName.length > 20) {
                 // Still too long? Take first few chars
                 newName = cleanName.substring(0, 10);
                 console.log(`Truncated Filename [${char.name}] -> [${newName}]`);
            }
        }
    }
    
    // 2. Fix System Prompt
    if (char.systemPrompt.startsWith('You are 202') || char.systemPrompt === `You are ${char.name}.`) {
        // Use description as system prompt if available
        if (char.description && char.description.length > 50) {
            char.systemPrompt = char.description;
        }
    }
    
    // 3. Deduplicate
    if (namesSeen.has(newName)) {
        console.log(`Skipping duplicate: ${newName}`);
        continue;
    }
    
    char.name = newName;
    namesSeen.add(newName);
    finalCharacters.push(char);
    updatedCount++;
}

fs.writeFileSync(INDEX_FILE, JSON.stringify(finalCharacters, null, 2), 'utf-8');
console.log(`Refined ${updatedCount} characters.`);
