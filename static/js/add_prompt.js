'use strict';

const button = document.querySelector('#add-prompt');

const morePrompts = document.querySelector('#more-prompts');

let promptCounter = 2

button.addEventListener('click', (evt) => {
    morePrompts.insertAdjacentHTML('beforeend', 
                                   `<br><label for="${promptCounter}">
                                   A prompt for the user to respond to: 
                                   </label><textarea class="prompt" name=
                                   "${promptCounter}" id="${promptCounter}"></textarea>`);
    promptCounter += 1;                               
    });