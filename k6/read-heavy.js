import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE = 'http://localhost:8000';

export const options = {
  stages: [
    { duration: '10s', target: 20 },
    { duration: '40s', target: 50 },
    { duration: '10s', target: 0  },
  ],
  thresholds: {
    http_req_duration: ['p(95)<800'],
    http_req_failed:   ['rate<0.01'],
  },
};

export function setup() {
  const res = http.post(
    `${BASE}/api/v1/auth/login`,
    JSON.stringify({ email: __ENV.K6_EMAIL, password: __ENV.K6_PASSWORD }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  return { token: JSON.parse(res.body).data.access_token };
}

export default function (data) {
  const params = {
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${data.token}`,
    },
  };

  const res = http.get(`${BASE}/api/v1/incidents/?page=1&page_size=20`, params);
  check(res, { 'incidents list 200': (r) => r.status === 200 });
  sleep(1);
}
