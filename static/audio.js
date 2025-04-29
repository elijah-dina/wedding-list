document.addEventListener('DOMContentLoaded', function() {
    const backgroundMusic = document.getElementById('backgroundMusic');
    let isPlaying = false;
    let currentTime = 0;

    function playAudio() {
        backgroundMusic.play().catch(error => {
            // Autoplay was prevented. You might want to show a play button.
            console.error("Autoplay prevented:", error);
        });
        isPlaying = true;
    }

    function pauseAudio() {
        backgroundMusic.pause();
        isPlaying = false;
        currentTime = backgroundMusic.currentTime;
    }

    function restoreAudio() {
        if (localStorage.getItem('isPlaying') === 'true') {
            backgroundMusic.currentTime = parseFloat(localStorage.getItem('currentTime')) || 0;
            playAudio();
        }
    }

    // Play audio on initial load if not already playing
    if (localStorage.getItem('isPlaying') !== 'true') {
        playAudio();
    } else {
        restoreAudio();
    }

    // Store audio state before navigating away
    window.addEventListener('beforeunload', function() {
        localStorage.setItem('isPlaying', isPlaying);
        localStorage.setItem('currentTime', backgroundMusic.currentTime);
    });
});