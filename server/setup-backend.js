const fs = require('fs');
const path = require('path');

// Klasörleri oluştur
const dirs = ['config', 'models', 'routes', 'middleware'];
dirs.forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir);
    console.log(`✅ ${dir} klasörü oluşturuldu`);
  }
});

console.log('✅ Tüm klasörler hazır!');
console.log('Şimdi VS Code\'da dosyaları manuel oluştur.');