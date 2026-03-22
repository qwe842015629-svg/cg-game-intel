const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, 'public/characters/d11df872153c3b6ce8eb7ae02f726313.json');
const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));

console.log('Keys:', Object.keys(data));
if (data.originalData) {
    console.log('originalData keys:', Object.keys(data.originalData));
    // Check for common image fields
    if (data.originalData.avatar) console.log('Found originalData.avatar (length):', data.originalData.avatar.length);
    if (data.originalData.image) console.log('Found originalData.image (length):', data.originalData.image.length);
}
