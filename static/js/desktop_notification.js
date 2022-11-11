'use strict';

const button = document.querySelector('#notify'); 

button.addEventListener('click', (evt) => {
    if ('Notification' in window) {
        if (Notification.permission === 'granted') {
            const notification = new Notification('Test!');
        } else if (Notification.permission !== 'denied') {
            Notification.requestPermission().then((permission) => {
                if (permission === 'granted') {
                    const notification = new Notification('Test me');
                }
            });
        }
    }
});

// Uncaught TypeError: Cannot read properties of null (reading 'addEventListener')
// This file is loading in the <head> and the id #notify is not yet found