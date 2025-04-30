// get_firebase_config.js
// Usage: node get_firebase_config.js

const { google } = require('googleapis');
const fs = require('fs');
const path = require('path');

async function main() {
  const keyPath = path.join(__dirname, '..', 'credentials', 'service_account.json');
  const keyFile = fs.readFileSync(keyPath, 'utf8');
  const key = JSON.parse(keyFile);

  const jwtClient = new google.auth.JWT(
    key.client_email,
    null,
    key.private_key,
    [
      'https://www.googleapis.com/auth/cloud-platform',
      'https://www.googleapis.com/auth/firebase'
    ]
  );

  await jwtClient.authorize();

  const firebase = google.firebase({
    version: 'v1beta1',
    auth: jwtClient,
  });

  // List all web apps for the project
  const projectId = key.project_id;
  const parent = `projects/${projectId}`;

  const res = await firebase.projects.webApps.list({ parent });
  if (!res.data.apps || res.data.apps.length === 0) {
    console.error('No Firebase web apps found for this project.');
    process.exit(1);
  }

  // Get the config for the first web app
  const appId = res.data.apps[0].appId;
  const configRes = await firebase.projects.webApps.getConfig({
    name: `projects/${projectId}/webApps/${appId}/config`
  });

  console.log('Firebase Web App Config:');
  console.log(JSON.stringify(configRes.data, null, 2));
}

main().catch(err => {
  console.error('Error fetching Firebase config:', err);
  process.exit(1);
});
