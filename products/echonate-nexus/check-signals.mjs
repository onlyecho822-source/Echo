import mysql from 'mysql2/promise';

const conn = await mysql.createConnection(process.env.DATABASE_URL);
const [rows] = await conn.execute('SELECT id, signalType, title, direction, confidence, detectedAt FROM signals ORDER BY detectedAt DESC');
console.log('Signals in database:');
rows.forEach(r => {
  console.log(`ID: ${r.id}, Type: ${r.signalType}, Date: ${r.detectedAt}, Title: ${r.title?.substring(0,50)}`);
});
await conn.end();
