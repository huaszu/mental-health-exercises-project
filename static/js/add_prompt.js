'use strict';

// Allow user to add an additional prompt within an exercise.


const button = document.querySelector('#add-prompt');

const morePrompts = document.querySelector('#more-prompts');

// The user interface initially gives the user room to fill out 1 prompt.
// The first additional prompt would be the second prompt, the next 
// additional would be the third, and so on. 
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