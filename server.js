const http = require('http');
const fs = require('fs');
const path = require('path');

const port = 8080;
const publicDir = path.join(__dirname, 'frontend', 'dist');

const mimeTypes = {
  '.html': 'text/html',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.wav': 'audio/wav',
  '.mp4': 'video/mp4',
  '.woff': 'application/font-woff',
  '.ttf': 'application/font-ttf',
  '.eot': 'application/vnd.ms-fontobject',
  '.otf': 'application/font-otf',
  '.wasm': 'application/wasm'
};

const server = http.createServer((req, res) => {
  console.log(`${req.method} ${req.url}`);
  
  // Handle CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }
  
  let filePath = path.join(publicDir, req.url === '/' ? 'index.html' : req.url);
  
  // Security check
  if (!filePath.startsWith(publicDir)) {
    res.writeHead(403);
    res.end('Forbidden');
    return;
  }
  
  // Check if file exists
  fs.access(filePath, fs.constants.F_OK, (err) => {
    if (err) {
      // If file doesn't exist and it's not an API call, serve index.html (SPA routing)
      if (!req.url.startsWith('/api')) {
        filePath = path.join(publicDir, 'index.html');
      } else {
        res.writeHead(404);
        res.end('Not Found');
        return;
      }
    }
    
    // Get file extension
    const extname = String(path.extname(filePath)).toLowerCase();
    const mimeType = mimeTypes[extname] || 'application/octet-stream';
    
    // Read and serve file
    fs.readFile(filePath, (error, content) => {
      if (error) {
        if (error.code === 'ENOENT') {
          res.writeHead(404);
          res.end('File not found');
        } else {
          res.writeHead(500);
          res.end('Server error: ' + error.code);
        }
      } else {
        res.writeHead(200, { 'Content-Type': mimeType });
        res.end(content, 'utf-8');
      }
    });
  });
});

server.listen(port, '0.0.0.0', () => {
  console.log(`🚀 XTTS V2 Frontend Server running at http://0.0.0.0:${port}`);
  console.log(`📁 Serving files from: ${publicDir}`);
});