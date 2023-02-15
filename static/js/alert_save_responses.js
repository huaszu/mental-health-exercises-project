'use strict';

// Offer a useful path for the user if the user wants to save an exercise
// submission but had not signed in to prevent the user from 
// experiencing loss of the information they provided, if they indeed want to
// sign in and keep the information. 


const form = document.querySelector('#exercise');

form.addEventListener('submit', (evt) => {
    evt.preventDefault();

    fetch('/login-status.json', {method: 'GET', credentials: 'include'})
        .then((response) => response.json())
        .then((responseJson) => {
            console.log(responseJson);
            if (responseJson === false) {
                alert('To save your responses for future viewing, create account or log in by clicking link at bottom.  New tab will open.  After login in new tab, click Submit again in current tab to view your responses.');
            } 
            if (responseJson === true) {
                let responses = {};
                
                for (const element of document.querySelectorAll('.responses')) {
                    responses[element.id] = element.value;
                }
                
                const splitPath = window.location.pathname.split('/');

                const exercise_id = splitPath[2]

                fetch(`/exercises/${exercise_id}/submitted`, {
                    method: 'POST', 
                    body: JSON.stringify(responses),
                    headers: {'Content-Type': 'application/json'},
                    credentials: 'include',
                    redirect: 'follow'})
                    // `response` object has a property `url`.  `url` is what was the destination.
                    // https://developer.mozilla.org/en-US/docs/Web/API/Response
                    .then((response) => response.json()) // Extract response body.
                    // Body is entirely JSON or entirely HTML or the data that I want to send.
                    // In this case, the body is a JSON object with one key in it.
                    // Read that JSON object from our JavaScript.
                    .then((responseJson) => {
                        console.log(responseJson.url);

                        console.log(window.location.hostname); // Example: 'fellowship.hackbrightacademy.com'
                        console.log(window.location.origin); // Example: 'https://fellowship.hackbrightacademy.com'

                        // Go to that URL.
                        window.location.replace(window.location.origin + responseJson.url);                      
                    })
            }
        });
    });