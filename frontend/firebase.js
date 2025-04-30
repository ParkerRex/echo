// frontend/src/firebase.js

// TODO: Replace the below config object with your Firebase project configuration.
// You can find this in your Firebase Console > Project Settings > General > Your apps > Firebase SDK snippet.

import { initializeApp, getApps } from "firebase/app";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "AIzaSyAHQ-vpHkanz4zMdMBteX73vq63vWTP9iQ",
  authDomain: "automations-457120.firebaseapp.com",
  projectId: "automations-457120",
  storageBucket: "automations-457120.appspot.com",
  messagingSenderId: "598863037291",
  appId: "1:598863037291:web:bfb205598a28ef5312c22e"
};

let app;
if (!getApps().length) {
  app = initializeApp(firebaseConfig);
} else {
  app = getApps()[0];
}

const db = getFirestore(app);

export { db };
