'use strict';

// Listen for click on "notify" button to check whether client has granted
// permission to send notifications and, if so, to send a test notification


const button = document.querySelector('#notify'); 


function notify() {
    console.log('hello');
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
};


button.addEventListener('click', (evt) => {setInterval(notify, 2000);});