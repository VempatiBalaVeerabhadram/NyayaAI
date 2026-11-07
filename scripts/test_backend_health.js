const express = require('express');
const request = require('supertest');
const healthRoutes = require('../backend/src/routes/health');

async function testHealth() {
  const app = express();
  app.use('/api/health', healthRoutes);

  console.log('Testing GET /api/health...');
  const res = await request(app).get('/api/health');
  console.log('Response Status:', res.status);
  console.log('Response Body:', JSON.stringify(res.body, null, 2));

  if (res.status === 200 && res.body.success === true) {
    console.log('✅ Backend Health Check PASSED!');
    process.exit(0);
  } else {
    console.error('❌ Backend Health Check FAILED!');
    process.exit(1);
  }
}

testHealth().catch((err) => {
  console.error('Test error:', err);
  process.exit(1);
});
