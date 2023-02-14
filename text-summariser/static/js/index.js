"use strict"

// ************************************************************************************
// Constants
// ************************************************************************************
// DOM element IDs
const EXAMPLE_BTN_ID = HTML.TEXT_ENTRY.EXAMPLE_BTN_ID;
const TEXT_ENTRY_DIV_ID = HTML.TEXT_ENTRY.PANEL_ID;
const TEXT_ENTRY_ID = HTML.TEXT_ENTRY.ID;
const SUMMARISE_DIV_ID = HTML.SUMMARISE.ID;
const SUMMARISE_FORM_ID = HTML.TEXT_ENTRY.FORM_ID;
const MAX_WORDS = 250
const EXAMPLE_TEXT = `One month after the United States began what has become a troubled 
rollout of a national COVID vaccination campaign, the effort is finally gathering real 
steam. Close to a million doses -- over 951,000, to be more exact -- made their way 
into the arms of Americans in the past 24 hours, the U.S. Centers for Disease Control 
and Prevention reported Wednesday. That's the largest number of shots given in one day 
since the rollout began and a big jump from the previous day, when just under 340,000 
doses were given, CBS News reported. That number is likely to jump quickly after the 
federal government on Tuesday gave states the OK to vaccinate anyone over 65 and said 
it would release all the doses of vaccine it has available for distribution. Meanwhile,
a number of states have now opened mass vaccination sites in an effort to get larger 
numbers of people inoculated, CBS News reported.`


// ************************************************************************************
// Helper functions
// ************************************************************************************
/**
 * Resize the three cards on the bottom row so that they're all the same height, using
 * the middle card (Original text) as the baseline.
 */
function resizeCards() {
    // resize the 'results' and 'summarise' boxes, based on the height of 'Original text'
    const height = document.getElementById(TEXT_ENTRY_DIV_ID).offsetHeight;
    document.getElementById(SUMMARISE_DIV_ID).style.height = `${height}px`;
}


/**
 * Interrupt the Summarise POST request, to perform some checks:
 * - Check that there is some text to process (essential to prevent a crash)
 * - Check the length of the text sent; warn the user if likely to be too long
 */
function interruptSummarise() {
    document.getElementById(SUMMARISE_FORM_ID).addEventListener("submit", function(e) {
        // get the text from Original text
        const text = document.getElementById(TEXT_ENTRY_ID).value;

        // if there isn't any text, show an alert and stop the submission
        if (text.trim() === "") {
            alert("ERROR: no text to process");
            e.preventDefault();
        }

        // check the number of words (approximately). If > 250, fire a confirm request
        if(text.split(" ").length > MAX_WORDS) {   
            // if the user is ok to continue, submit the POST. Otherwise, stop it and
            // wait for another Summarise request.
            const response = confirm(`WARNING: the summariser can struggle with long 
            passages of text. Do you want to continue?`);
            console.log(response);
            if(response) {
                return response;
            }
            else {
                e.preventDefault();
            }
        } 
    })
}


/**
 * Overall driver function to populate the dynamic page elements; the two inputs, the
 * table, and the three cards.
 */
function renderPage() {
    // Add an event listener to the 'Example' button, to display some sample text
    document.getElementById(EXAMPLE_BTN_ID).addEventListener("click", e => {
        // Convert to plain text and remove any line breaks, quotes etc. 
        document.getElementById(TEXT_ENTRY_ID).value = JSON.stringify(EXAMPLE_TEXT)
                                                           .replaceAll('"', '')
                                                           .replaceAll('\\n','');
    })

    // Add an event listener to resize the cards when the textarea is resized, and do
    //  an inital resize
    const resizeObserver = new ResizeObserver(() => {
        resizeCards();
        console.log('Size changed');
    });
    resizeObserver.observe(document.getElementById(TEXT_ENTRY_DIV_ID));
    resizeCards();

    // Add the interruption event listener to the Summarise button
    interruptSummarise();
}


// ************************************************************************************
// Set up page and element events
// ************************************************************************************
document.addEventListener('DOMContentLoaded', renderPage());

