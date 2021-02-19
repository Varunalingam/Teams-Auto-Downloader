// ==UserScript==
// @name         Teams Auto Download
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  Video Downloader for MSTeams
// @author       You
// @match        https://teams.microsoft.com/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';
    console.log("Auto Download Script is Initiated")
    var script = document.createElement('script'); 
    script.src = 'https://www.github.com/';
    script.type = 'text/javascript'; 
    document.getElementsByTagName('body')[0].appendChild(script); 
    function wait() { 
        if(typeof unsafeWindow.jQuery == 'undefined') 
    { window.setTimeout(GM_wait,100); } 
            else { $ = unsafeWindow.jQuery; console.log("Auto Download is Loaded") } 
    } 
    wait(); 
})();