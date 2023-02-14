"use strict";

let carousel = document.getElementById("id-carousel");

carousel.addEventListener("click", function(){
    // simple debug message
    console.log("carousel clicked");

    // send the Google analytics event message (maybe...)
    gtag("event", "carousel_clicked", {
        "event_category": "engagement",
        "event_label": "content_type"
    });
});