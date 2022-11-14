'use strict';

const button = document.querySelector('#notify'); 

// button.addEventListener('click', (evt) => {
//     console.log('hello');
//     if ('Notification' in window) {
//         if (Notification.permission === 'granted') {
//             // console.log('granted');

//             // setTimeout(() => {
//             //     //send notification
//             // }, interval_in_milliseconds);

//             const notification = new Notification('Test!');
//         } else if (Notification.permission !== 'denied') {
//             // console.log('ask for permission');
//             Notification.requestPermission().then((permission) => {
//                 if (permission === 'granted') {
//                     // console.log('now granted');
//                     const notification = new Notification('Test me');
//                 }
//             });
//         }
//     }
// }
// );

function notify() {
    console.log('hello');
    if ('Notification' in window) {
        if (Notification.permission === 'granted') {
            // console.log('granted');

            // setTimeout(() => {
            //     //send notification
            // }, interval_in_milliseconds);

            const notification = new Notification('Test!');
        } else if (Notification.permission !== 'denied') {
            // console.log('ask for permission');
            Notification.requestPermission().then((permission) => {
                if (permission === 'granted') {
                    // console.log('now granted');
                    const notification = new Notification('Test me');
                }
            });
        }
    }
};

button.addEventListener('click', (evt) => {setInterval(notify, 2000);});