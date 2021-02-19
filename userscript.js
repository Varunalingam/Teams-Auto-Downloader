// ==UserScript==
// @name         Teams Auto Download
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  Video Downloader for MSTeams
// @author       You
// @match        https://teams.microsoft.com/*
// @run-at       document-idle
// @grant        none
// ==/UserScript==

(function() {
    'use strict';
    console.log("Auto Download Script is Initiated");
    var index = 0;
    var nextPage = null
    function waitUntilLoadPage(){
        if(document.getElementsByClassName('match-parent team left-rail-item-kb-l2').length < 1){
            console.log("Auto Download Script is Reruning");
            setTimeout(waitUntilLoadPage, 3000);
        }
        else{
            var pages = document.getElementsByClassName("match-parent team left-rail-item-kb-l2")
            console.log(pages);
            if (index < pages.length){
                nextPage = pages[index];
            }else{
                nextPage = null;
            }
            //while(nextPage == null || index != pages.length){
              //  if (pages[index].getAttribute("aria-expanded") == 'true'){
                //    if (index != pages.length - 1){
                  //      nextPage = pages[index + 1];
                    //    break;
                    //}else {
                      //  break;
                    //}
                //}
                //index += 1
            //};
            if (nextPage != null){
                nextPage.click();
                nextPage.getElementsByTagName('h3')[0].click()
                index += 1
                WaitTillDownload();
            }
            console.log(nextPage);
            //var downloads = document.getElementsByClassName("download-label")
            //downloads[downloads.length - 1].onclick = function() {
                //alert(document.getElementsByClassName("download-label").length);
            //};
            //downloads[downloads.length - 1].target = '_Blank'
            //downloads[downloads.length - 1].download = "ABC.mp4"
            //downloads[downloads.length - 1].click();
        }
    };
    function WaitTillDownload(){
        if(document.getElementsByClassName('item-wrap ts-message-list-item').length < 1){
            console.log("Auto Download Script is Reruning");
            setTimeout(WaitTillDownload, 3000);
        }else{
            var downloads = document.getElementsByClassName('app-small-font download-recording');
            var pos = 0;
            while(pos < downloads.length){
                if (downloads[pos].getElementsByClassName('download-expiration')[0].getAttribute("title") == "(expires in 20 day(s))"){
                    downloads[pos].getElementsByClassName("download-label")[0].click();
                }
                pos+= 1;
            }
            var pages = document.getElementsByClassName("match-parent team left-rail-item-kb-l2")
            if (index!= pages.length){
               console.log("Auto Download Script is Loading Next Page");
               setTimeout(waitUntilLoadPage, 3000);
            }else{
               console.log("end-point");
            }
        }
    }
    waitUntilLoadPage();
})();