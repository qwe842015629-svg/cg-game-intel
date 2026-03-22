
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const sourceDir = 'E:\\小程序开发\\游戏充值网站\\酒馆预设合集';
const destDir = path.join(__dirname, 'public/characters');
const indexFile = path.join(destDir, 'index.json');

if (!fs.existsSync(destDir)) {
  fs.mkdirSync(destDir, { recursive: true });
}

const characters = [];

function scanDir(dir) {
  const files = fs.readdirSync(dir);
  
  for (const file of files) {
    const fullPath = path.join(dir, file);
    const stat = fs.statSync(fullPath);
    
    if (stat.isDirectory()) {
      scanDir(fullPath);
    } else if (file.endsWith('.json')) {
      try {
        const content = fs.readFileSync(fullPath, 'utf8');
        const data = JSON.parse(content);
        
        // Check if it's a valid character card
        // SillyTavern cards usually have 'name', 'description', 'first_mes', 'personality'
        // Some might be V2 spec (data wrapper)
        
        let charData = data;
        if (data.spec === 'chara_card_v2' && data.data) {
           charData = data.data;
        } else if (data.name && (data.description || data.personality || data.first_mes)) {
           // Likely V1 or simple format
           charData = data;
        } else {
           // Not a character card (maybe regex, world info, etc.)
           continue;
        }
        
        // Skip if name is missing
        if (!charData.name) continue;
        
        console.log(`Found character: ${charData.name} in ${file}`);
        
        // Generate a unique ID
        const id = crypto.createHash('md5').update(charData.name + fullPath).digest('hex');
        const destFile = `${id}.json`;
        
        // Copy the file
        fs.copyFileSync(fullPath, path.join(destDir, destFile));
        
        // Look for avatar
        // 1. Check if there's an image with the same name in the same folder
        const baseName = path.basename(file, '.json');
        let avatarUrl = '';
        
        const possibleExts = ['.png', '.jpg', '.jpeg', '.webp'];
        for (const ext of possibleExts) {
           const imgPath = path.join(dir, baseName + ext);
           if (fs.existsSync(imgPath)) {
             const destImg = `${id}${ext}`;
             fs.copyFileSync(imgPath, path.join(destDir, destImg));
             avatarUrl = `/characters/${destImg}`;
             break;
           }
        }
        
        // 2. If no local image, check if 'avatar' field in JSON is a URL or Base64 (we don't extract base64 to file here to keep it simple, just use it if it's a URL, or let the frontend handle base64 if it's inside the JSON)
        // Actually, for the index, we want a thumbnail. 
        // If the JSON contains "avatar": "base64...", we can use that for the index? 
        // Or just leave it blank and let frontend load the JSON to get the avatar.
        // For now, let's just record if we found a local image.
        
        characters.push({
          id: id,
          name: charData.name,
          description: charData.description || '',
          avatar: avatarUrl, // might be empty
          file: destFile,
          originalPath: fullPath
        });
        
      } catch (e) {
        console.error(`Error parsing ${file}:`, e.message);
      }
    }
  }
}

scanDir(sourceDir);

fs.writeFileSync(indexFile, JSON.stringify(characters, null, 2));
console.log(`Imported ${characters.length} characters.`);
