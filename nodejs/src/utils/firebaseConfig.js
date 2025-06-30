const Setting = require('../models/setting');
const { FIREBASE_PRIVATE_KEY } = require('../config/constants/common');
const admin = require('firebase-admin');
const { FIREBASE } = require('../config/config');

new Promise((resolve, reject) => {
    try {
        const firebaseConfig = Setting.findOne({ code: FIREBASE_PRIVATE_KEY });
        resolve(firebaseConfig);
    } catch (error) {
        logger.error('error in firebase config', error);
        reject(error);
    }
}).then((firebaseData) => {
    if (!firebaseData?.details || !Object.keys(firebaseData.details).length) {
        Setting.create({
            name: FIREBASE_PRIVATE_KEY,
            code: FIREBASE_PRIVATE_KEY,
            details: {
                type: FIREBASE.PROJECT_TYPE,
                project_id: FIREBASE.PROJECT_ID,
                private_key_id: FIREBASE.PRIVATE_KEY_ID,
                private_key: FIREBASE.PRIVATE_KEY,
                client_email: FIREBASE.CLIENT_EMAIL,
                client_id: FIREBASE.CLIENT_ID,
                auth_uri: FIREBASE.AUTH_URI,
                token_uri: FIREBASE.TOKEN_URI,
                auth_provider_x509_cert_url: FIREBASE.AUTH_PROVIDER,
                client_x509_cert_url: FIREBASE.CERT_URL,
                universe_domain: FIREBASE.UNIVERSE_DOMAIN,
            },
        }).then((response) => {
            admin.initializeApp({
                credential: admin.credential.cert(response.details),
            });
        });
    }
    // every time server restart
    if (Object.keys(firebaseData.details).length) {
        admin.initializeApp({
            credential: admin.credential.cert(firebaseData.details),
        });
        logger.info('Firebase Notification Initialized!🔥');
    }
});
