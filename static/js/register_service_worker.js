'use strict';

// Base64 is a group of similar binary-to-text encoding schemes that represent 
// binary data in an ASCII string format by translating it into a radix-64 
// representation.  https://developer.mozilla.org/en-US/docs/Glossary/Base64

// One common application of Base64 encoding on the web is to encode binary 
// data so it can be included in a data: URL.

// Each Base64 digit represents exactly 6 bits of data. So, three 8-bits bytes 
// of the input string/binary file (3×8 bits = 24 bits) can be represented by 
// four 6-bit Base64 digits (4×6 = 24 bits).

// This means that the Base64 version of a string or file will be at least 
// 133% the size of its source (a ~33% increase). The increase may be larger 
// if the encoded data is small. For example, the string "a" with length === 1 
// gets encoded to "YQ==" with length === 4 — a 300% increase.

// Convert to UTF-8 array of characters

// Why do we have this code?  We will want to fetch the server's public key 
// and convert the response to text; then it needs to be converted to a 
// Uint8Array (to support Chrome).  Browser interoperability.
// https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Re-engageable_Notifications_Push

function urlB64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');

    // The atob() function decodes a string of data that has been encoded using Base64 encoding.  https://developer.mozilla.org/en-US/docs/Web/API/atob
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
        // The charCodeAt() method returns an integer between 0 and 65535 
        // representing the UTF-16 code unit at the given index.  
        // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/charCodeAt
        outputArray[i] = rawData.charCodeAt(i);
    }
    console.log('function urlB64ToUint8Array(base64String) ok');
    return outputArray;
}

// Send subscription to application server
// POSTs subscription_json to API endpoint
function updateSubscriptionOnServer(subscription, apiEndpoint) {
    console.log('function updateSubscriptionOnServer() about to run');
    return fetch(apiEndpoint, {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            subscription_json: JSON.stringify(subscription)
        })
    });
}

// Subscribe user to subscription
function subscribeUser(swRegistration, 
                       applicationServerPublicKey, 
                       apiEndpoint) {

    console.log('function subscribeUser() about to run');

    // FILL IN COMMENT ON WHY APPSERVERKEY COMES IN AS B64
    const applicationServerKey = urlB64ToUint8Array(applicationServerPublicKey);
    // console.log(applicationServerKey);

    // The PushManager interface of the Push API provides a way to receive 
    // notifications from third-party servers as well as request URLs for 
    // push notifications.
    // This interface is accessed via the ServiceWorkerRegistration.pushManager 
    // property.
    // https://developer.mozilla.org/en-US/docs/Web/API/PushManager

    // The subscribe() method of the PushManager interface subscribes to a 
    // push service.
    // It returns a Promise that resolves to a PushSubscription object containing 
    // details 

                        // WHAT DETAILS, incl API endpoint?

    // of a push subscription. A new push subscription is created if the 
    // current service worker does not have an existing subscription.  
    // https://developer.mozilla.org/en-US/docs/Web/API/PushManager/subscribe

    // Side effect of subscribe(): request permission from user to show
    // push notifications, if user has not already given permission.

    // When accepted, the permission works for both notifications and push.
    // https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Re-engageable_Notifications_Push

    // Hurrah, tested that this side effect is true!
    // TEST WHAT HAPPENS IF USER CLICKS BLOCK.  ARE THERE PROBLEMS W USING APP?
    swRegistration.pushManager.subscribe({

        // userVisibleOnly is a boolean indicating that the returned 
        // push subscription will only be used for messages whose effect 
        // is made visible to the user.
        userVisibleOnly: true,

        // applicationServerKey is a Base64-encoded string or ArrayBuffer 
        // containing an ECDSA P-256 public key that the push server will use 
        // to authenticate the application server. If specified, all messages 
        // from the application server must use the VAPID authentication scheme, 
        // and include a JSON Web Token signed with the corresponding private key. This 
        // key IS NOT the same ECDH key used to encrypt the data.
        // This parameter is required in some browsers, including Chrome and Edge.
        applicationServerKey: applicationServerKey
    })

    // The subscribe() method returns a Promise that resolves to a 
    // PushSubscription object, containing details of a push subscription. 
    // A new push subscription is created if the current service worker 
    // does not have an existing subscription.
    .then((subscription) => {
        console.log('ヽ(^o^)丿 User is subscribed.');

        // CLARIFICATION TO COME ON WHAT THIS RETURNS, SHOULD BE IN JSON since later we do response.json()
        return updateSubscriptionOnServer(subscription, apiEndpoint);

    })

    .then((response) => {

        // The ok read-only property of the Response interface contains 
        // a Boolean stating whether the response was successful (status in 
        // the range 200-299) or not.
        // https://developer.mozilla.org/en-US/docs/Web/API/Response/ok
        if (!response.ok) {

            // The throw statement throws a user-defined exception. Execution 
            // of the current function will stop (the statements after throw 
            // won't be executed), and control will be passed to the first catch 
            // block in the call stack. If no catch block exists among caller 
            // functions, the program will terminate.
            // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/throw
            throw new Error(':@ Bad status code from server.');
        }
        return response.json(); // Return a promise that resolves with the 
        // result of parsing the body text as JSON, i.e., of taking JSON as 
        // input and parsing it to produce a JavaScript object.
    })

    .then((responseData) => {
        console.log(responseData);
            // if the route /api/push-subscriptions returns a "status" that is not "success":
            if (responseData.status!=="success") {
                throw new Error('v.v Bad response from server.');
            }
    })
  
    .catch((err) => {
        console.log(';_; Failed to subscribe the user: ', err);

        // The stack property of Error objects offer a trace of which functions 
        // were called, in what order, from which line and file, and with what 
        // arguments. The stack string proceeds from the most recent calls to 
        // earlier ones, leading back to the original global scope call.
        console.log(err.stack);
    });
}

// Register service worker

// serviceWorkerUrl is the url the browser uses to load the service worker.  
// In our case, the url would be `/static/service_worker.js`.

// applicationServerPublicKey is the vapid public key, the public key
// component of a public key/private key pair that securely authorizes
// communication between the push server and the push service running on the
// client.

// apiEndpoint is the API endpoint used to save the push subscriptions 
// generated by clients. 

function registerServiceWorker(serviceWorkerUrl, 
                               applicationServerPublicKey, 
                               apiEndpoint) {
    
    // console.log(serviceWorkerUrl);
    // console.log(applicationServerPublicKey);
    // console.log(apiEndpoint);

    let swRegistration = null;
    if ('serviceWorker' in navigator && 'PushManager' in window) {
        console.log('ヽ(´▽`)/ Browser supports Service Worker and Push');

        // The register() method of the ServiceWorkerContainer interface 
        // creates or updates a ServiceWorkerRegistration for the given scriptURL.

        // If successful, a service worker registration ties the provided 
        // script URL to a scope, which is subsequently used for navigation 
        // matching. Can call this method unconditionally from the controlled 
        // page. I.e., don't need to first check whether there's an active 
        // registration.
        // https://developer.mozilla.org/en-US/docs/Web/API/ServiceWorkerContainer/register
        navigator.serviceWorker.register(serviceWorkerUrl)
        // navigator.serviceWorker.register(serviceWorkerUrl, { scope: "/" })

        // scope: A string representing a URL that defines a service worker's 
        // registration scope; that is, what range of URLs a service worker 
        // can control. This is usually a relative URL. It is relative to the 
        // base URL of the application. By default, the scope value for a 
        // service worker registration is set to the directory where the 
        // service worker script is located. 

        // register() returns a Promise that resolves with a 
        // ServiceWorkerRegistration object.

        .then((swReg) => {
            console.log('(＾▽＾) Service Worker is registered', swReg);
            subscribeUser(swReg, applicationServerPublicKey, apiEndpoint);

            // Reassign swRegistration from null to value of swReg
            swRegistration = swReg;
        })

        .catch((err) => {
            console.error('>:( Service Worker Error', err);
        });
    } else {
        console.warn('( ༎ຶ ۝ ༎ຶ ) Push messaging is not supported');
    } 
    
    console.log(swRegistration);
    return swRegistration;
}
