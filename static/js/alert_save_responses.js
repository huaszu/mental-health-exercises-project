'use strict';

const button = document.querySelector('#completed-exercise');

button.addEventListener('click', (evt) => {
    evt.preventDefault();
    alert('To save your responses for future viewing, create account or log in by clicking link at bottom.  New tab will open.  After login in new tab, click Submit again in current tab to get to view of all your responses.');
});