'use strict';

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
                    credentials: 'include'})
                    .then((response) => window.location.replace(response.url))
            }
        });
    });