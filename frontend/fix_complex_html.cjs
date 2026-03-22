const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, 'public/characters/index.json');

// Backup the file first
// fs.copyFileSync(filePath, filePath + '.bak_complex_fix');

try {
  const data = fs.readFileSync(filePath, 'utf8');
  let characters = JSON.parse(data);
  let modifiedCount = 0;

  characters = characters.map(char => {
    let modified = false;
    let content = char.firstMessage || "";

    if (!content) return char;

    // Helper to unescape HTML entities if they look like code but shouldn't be
    // e.g. &lt;div style=... -> <div style=...
    // Only do this if we see a pattern that looks like escaped HTML tags
    if (content.includes('&lt;') && content.includes('&gt;')) {
      // Simple unescape for common chars
      const unescaped = content
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>')
        .replace(/&quot;/g, '"')
        .replace(/&amp;/g, '&');
      
      // If unescaping reveals HTML tags, use it
      if (/<[a-z][\s\S]*>/i.test(unescaped)) {
        console.log(`Unescaped HTML entities for character: ${char.name}`);
        content = unescaped;
        modified = true;
      }
    }

    // Function to un-indent content
    const unindent = (str) => {
      if (!str) return str;
      const lines = str.split('\n');
      // Find minimum indentation
      let minIndent = Infinity;
      let hasIndentedLines = false;
      
      for (const line of lines) {
        if (line.trim().length === 0) continue;
        const match = line.match(/^(\s+)/);
        const indent = match ? match[1].length : 0;
        if (indent < minIndent) minIndent = indent;
        hasIndentedLines = true;
      }
      
      if (!hasIndentedLines || minIndent === 0 || minIndent === Infinity) return str;
      
      return lines.map(line => {
         if (line.trim().length === 0) return line;
         return line.substring(minIndent);
      }).join('\n');
    };

    // Remove Markdown code blocks
    // Matches ```html ... ```, ```xml ... ```, or just ``` ... ```
    // We want to keep the CONTENT inside the block
    const codeBlockRegex = /```(?:html|xml|css)?\s*([\s\S]*?)\s*```/gi;
    if (codeBlockRegex.test(content)) {
      console.log(`Removing markdown code blocks for character: ${char.name}`);
      content = content.replace(codeBlockRegex, '$1');
      modified = true;
    }

    // Now handle full HTML document structures
    // Goal: Extract <style>, <link rel="stylesheet">, and <body> content.
    // Remove DOCTYPE, html, head, meta, title.

    // Check if it has <html> or <!DOCTYPE or <head> or <body>
    if (
      /<!DOCTYPE/i.test(content) || 
      /<html/i.test(content) || 
      /<head/i.test(content) || 
      /<body/i.test(content)
    ) {
      // ... (existing logic) ...
      console.log(`Processing full HTML structure for character: ${char.name}`);
      
      // Extract styles
      const styleRegex = /<style[\s\S]*?>([\s\S]*?)<\/style>/gi;
      let styles = [];
      let match;
      while ((match = styleRegex.exec(content)) !== null) {
        styles.push(match[0]); // Keep the full <style> tag
      }

      // Extract stylesheets links
      const linkRegex = /<link[^>]*rel=["']stylesheet["'][^>]*>/gi;
      let links = [];
      while ((match = linkRegex.exec(content)) !== null) {
        links.push(match[0]);
      }

      // Extract body content
      const bodyRegex = /<body[\s\S]*?>([\s\S]*?)<\/body>/i;
      const bodyMatch = bodyRegex.exec(content);
      
      let bodyContent = "";
      if (bodyMatch) {
        bodyContent = bodyMatch[1];
      }

      if (bodyContent) {
        // Find where the HTML part starts to preserve intro text
        const htmlStartIndex = content.search(/<!DOCTYPE|<html|<head/i);
        
        let introText = "";
        if (htmlStartIndex > 0) {
          introText = content.substring(0, htmlStartIndex);
        }

        // Clean up intro text (trim end)
        introText = introText.trim();

        // Unindent extracted body content to prevent Markdown code blocks
        bodyContent = unindent(bodyContent);

        content = `${introText}\n\n${links.join('\n')}\n${styles.join('\n')}\n<div class="extracted-card-content">\n${bodyContent}\n</div>`;
        modified = true;
      } else {
         // If no body tag, but we have html/head...
         const oldContent = content;
         
         // Remove DOCTYPE
         content = content.replace(/<!DOCTYPE[^>]*>/gi, '');
         // Remove <html> opening and closing
         content = content.replace(/<html[^>]*>/gi, '').replace(/<\/html>/gi, '');
         // Remove <meta> and <title>
         content = content.replace(/<meta[^>]*>/gi, '').replace(/<title>.*?<\/title>/gi, '');
         
         // Remove <head> tags but keep content. 
         content = content.replace(/<head[^>]*>([\s\S]*?)<\/head>/gi, (match, inner) => {
             return unindent(inner);
         });
         
         // Remove <body> tags but keep content
         content = content.replace(/<body[^>]*>([\s\S]*?)<\/body>/gi, (match, inner) => {
             return unindent(inner);
         });
         
         if (content !== oldContent) {
             modified = true;
         }
      }
    } else {
      // Logic for partial HTML cards (like CTE Team) that don't have full document structure
      // but have indented HTML that causes Markdown code blocks.
      
      // Regex to find lines starting with 4 or more spaces followed by an HTML tag
      // We replace 4+ spaces with 0 spaces to prevent code blocks.
      const indentedHtmlRegex = /^(\s{4,})(<[a-z/][^>]*>)/gim;
      
      if (indentedHtmlRegex.test(content)) {
        console.log(`Fixing indented HTML for character: ${char.name}`);
        content = content.replace(indentedHtmlRegex, '$2'); // Keep only the tag, remove whitespace
        modified = true;
      }
    }

    if (modified) {
      modifiedCount++;
      char.firstMessage = content;
    }
    return char;
  });

  if (modifiedCount > 0) {
    fs.writeFileSync(filePath, JSON.stringify(characters, null, 2), 'utf8');
    console.log(`Successfully fixed HTML content for ${modifiedCount} characters.`);
  } else {
    console.log('No characters needed fixing.');
  }

} catch (err) {
  console.error('Error processing file:', err);
}
