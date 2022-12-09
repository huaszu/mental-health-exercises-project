'use strict';

const button = document.querySelector('#add-prompt');

const morePrompts = document.querySelector('#more-prompts');

let promptCounter = 2

button.addEventListener('click', (evt) => {
    morePrompts.insertAdjacentHTML('beforeend', 
                                   `<div class="row mb-3">
                                        <label for="${promptCounter}" class="col-sm-2 col-form-label">A prompt for the user to respond to: 
                                        </label>
                                        <textarea name="prompt" class="form-control prompt" id="${promptCounter}" required>
                                        </textarea>
                                    </div>`);
    promptCounter += 1;                               
    });