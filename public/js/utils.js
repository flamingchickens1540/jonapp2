// utils.js misc utility functions and helpers
// Author: Nate Sales
//
// This file provides miscellaneous independent utilities and helper functions.
// It can be loaded at any time during page load and requires no dependencies.

/**
 * Copy text from an element to the clipboard
 * @param element Element to get text from
 */
function copyToClipboard(element) {
    const copyElement = document.getElementById(element);
    copyElement.select();
    copyElement.setSelectionRange(0, 99999);
    document.execCommand("copy");
}
