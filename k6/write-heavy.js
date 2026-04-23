import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE = 'http://localhost:8000';
const CATEGORIES = ['checkpoint_delay', 'road_closure', 'accident', 'weather', 'military', 'other'];
const MAX_VUS = 30;

export const options = {
  stages: [
    { duration: '10s', target: 10 },
    { duration: '40s', target: MAX_VUS },
    { duration: '10s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<1200'],
    http_req_failed:   ['rate<0.01'],
  },
};

export function setup() {
  const tokens = [];
  for (let i = 1; i <= MAX_VUS; i++) {
    const email = `k6_write_${i}_${Date.now()}@test.com`;
    const password = 'K6Test@Pass123!';

    http.post(
      `${BASE}/api/v1/auth/register`,
      JSON.stringify({ email, username: `k6w${i}x${Date.now()}`, password }),
      { headers: { 'Content-Type': 'application/json' } }
    );

    const login = http.post(
      `${BASE}/api/v1/auth/login`,
      JSON.stringify({ email, password }),
      { headers: { 'Content-Type': 'application/json' } }
    );

    tokens.push(JSON.parse(login.body).data.access_token);
  }
  return { tokens };
}

export default function (data) {
  const token = data.tokens[(__VU - 1) % data.tokens.length];
  const params = {
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
  };

  const payload = JSON.stringify({
    category: CATEGORIES[Math.floor(Math.random() * CATEGORIES.length)],
    description: `k6 write test ${__VU} ${Date.now()}`,
    latitude: 31.9 + Math.random() * 0.5,
    longitude: 35.2 + Math.random() * 0.3,
  });

  const res = http.post(`${BASE}/api/v1/reports/`, payload, params);
  check(res, { 'report submitted 201': (r) => r.status === 200 || r.status === 201 });
  sleep(7);
}
