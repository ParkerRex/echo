import { initializeApp, getApps } from "firebase/app";
import type { FirebaseApp } from "firebase/app";
import { getFirestore, Firestore } from "firebase/firestore";

// Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyAHQ-vpHkanz4zMdMBteX73vq63vWTP9iQ",
    authDomain: "automations-457120.firebaseapp.com",
    projectId: "automations-457120",
    storageBucket: "automations-457120.appspot.com",
    messagingSenderId: "598863037291",
    appId: "1:598863037291:web:bfb205598a28ef5312c22e"
};

let app: FirebaseApp;
if (!getApps().length) {
    app = initializeApp(firebaseConfig);
} else {
    app = getApps()[0];
}

const db: Firestore = getFirestore(app);

export { db }; 