const request = require('supertest');
const express = require('express');
const healthRoutes = require('../src/routes/health');

describe('NyayaAI Backend Health Check API', () => {
  let app;

  beforeAll(() => {
    app = express();
    app.use('/api/health', healthRoutes);
  });

  it('GET /api/health returns 200 with status report', async () => {
    const res = await request(app).get('/api/health');
    expect(res.statusCode).toBe(200);
    expect(res.body.success).toBe(true);
    expect(res.body.data).toHaveProperty('status');
    expect(res.body.data).toHaveProperty('services');
  });
});
