"use strict";

let redButton = document.getElementById("id-btn-red");
let yellowButton = document.getElementById("id-btn-yellow");
let greenButton = document.getElementById("id-btn-green");

redButton.addEventListener("click", function(){
    // simple debug message
    console.log("red button clicked");

    // send the Google analytics event message (maybe...)
    gtag("event", "red_button_clicked", {
        "event_category": "engagement",
        "event_label": "content_type"
    });
});

yellowButton.addEventListener("click", function(){
    // simple debug message
    console.log("yellow button clicked");

    // send the Google analytics event message (maybe...)
    gtag("event", "yellow_button_clicked", {
        "event_category": "engagement",
        "event_label": "content_type"
    });
});

greenButton.addEventListener("click", function(){
    // simple debug message
    console.log("green button clicked");

    // send the Google analytics event message (maybe...)
    gtag("event", "green_button_clicked", {
        "event_category": "engagement",
        "event_label": "content_type"
    });
});