const fs = require('fs');
const path = require('path');

const CHARACTERS_DIR = path.join(__dirname, 'public/characters');
const INDEX_FILE = path.join(CHARACTERS_DIR, 'index.json');

const characters = JSON.parse(fs.readFileSync(INDEX_FILE, 'utf-8'));
let updatedCount = 0;

for (const char of characters) {
    if (char.name.length > 20) {
        console.log(`Fixing long name: [${char.name.substring(0, 30)}...]`);
        // Try to cut at first space or punctuation
        let newName = char.name.split(/[ ：:，,]/)[0];
        if (newName.length > 20) {
            newName = newName.substring(0, 10);
        }
        
        // Specific fix for the "陈池..." case which seemed to be space separated
        if (char.name.includes('陈池')) {
            newName = '陈池 (恋综)';
        }
        
        char.name = newName;
        updatedCount++;
        console.log(`-> Renamed to: [${newName}]`);
    }
}

if (updatedCount > 0) {
    fs.writeFileSync(INDEX_FILE, JSON.stringify(characters, null, 2), 'utf-8');
    console.log(`Fixed ${updatedCount} long names.`);
} else {
    console.log('No long names found.');
}
