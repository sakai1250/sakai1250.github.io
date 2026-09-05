/**
 * Taigo Sakai Portfolio - Temporary compatibility shim
 */

// Kept only for older cached main.js versions until this file is removed.
function initBackgroundParticles() {}

function initTypingEffect() {
    const cursor = document.querySelector('.typing-container .cursor');
    if (cursor) cursor.style.display = 'none';
}

window.initBackgroundParticles = initBackgroundParticles;
window.initTypingEffect = initTypingEffect;
