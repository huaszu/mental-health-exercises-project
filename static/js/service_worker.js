'use strict';

// Let's use the Service Worker API!

self.addEventListener('install', (evt) => {
  console.log('Service Worker installing {=');
});

self.addEventListener('activate', (evt) => {
  console.log('Service Worker activating (^O^)');
});

self.addEventListener('push', (evt) => {
  console.log('[Service Worker] Push received ᕕ( ᐛ )ᕗ');
  // Read data sent with event
  const pushData = evt.data.text(); 
  console.log(`[Service Worker] Push received this data - "${pushData}"`);

  // Have the notification show a title, and content in the body
  let data, title, body;
  try {
    // If data sent with event is JSON string that can be parsed, parse the JSON string
    data = JSON.parse(pushData);
    // Extract title from the JSON
    title = data.title;
    // Extract body from the JSON
    body = data.body;
  } catch(e) {
    // If the `try` block throws an exception, possibly because the data sent with
    // event is not a JSON string that can be parsed as above, assign `body`
    // the string as the value
    title = "Untitled";
    body = pushData;
  }
  const options = {
    body: body
  };
  console.log(title, options);

  // The `ExtendableEvent.waitUntil()` method tells the event dispatcher that 
  // work is ongoing. It can also be used to detect whether that work was 
  // successful. 
  // In service workers, waitUntil() tells the browser that work is ongoing 
  // until the promise settles, and it should not terminate the service worker 
  // if it wants that work to complete.
  // waitUntil() takes in a promise.  Returns None (undefined).
  // https://developer.mozilla.org/en-US/docs/Web/API/ExtendableEvent/waitUntil
  evt.waitUntil(

    // The showNotification() method of the ServiceWorkerRegistration 
    // interface creates a notification on an active service worker.
    // https://developer.mozilla.org/en-US/docs/Web/API/ServiceWorkerRegistration/
    
    // `options` is an object that allows configuring the notification. 
    // `options` has a property `body`, which is a string that represents 
    // extra content to display within the notification.
    self.registration.showNotification(title, options)
  );
});