const player = document.getElementById("podcast-audio");
const controlContainer = document.getElementById("audio-controls");
const playButton = document.getElementById("play-button");
const playIcon = document.getElementById("play-icon");
const muteButton = document.getElementById("mute-button");
const currentTime = document.getElementById("current-time");
const duration = document.getElementById("duration");
const progress = document.getElementById("audio-seek");
const volSlider = document.getElementById("volume-slider");
const currentVol = document.getElementById("current-volume");

let raf = null;     // requestAnimationFrame request id

/* Time Display Functions */
function formatTime(time){
    const secs = Math.floor(time % 60);
    const mins = Math.floor((time / 60) % 60);
    const hours = Math.floor(time / 3600);
    const formattedSecs = secs < 10 ? `0${secs}` : `${secs}`;
    return `${ hours < 1 ? "" : hours+":" }${mins}:${formattedSecs}`;
}

/* 
    Updates while the player is running
    1. Match the progress slider to current time 
    2. Update the current time display
    3. Update the pseudo element that displays progress on the slider
    4. Make sure the thumb progresses across the slider
*/
function whilePlaying(){
    progress.value = Math.floor(player.currentTime);        
    currentTime.textContent = formatTime(progress.value);   
    controlContainer.style.setProperty("--seek-before-width", `${(progress.value / progress.max) * 100}%`);
    raf = requestAnimationFrame(whilePlaying);             
}

/* Play/Pause Button */
let playState = "play";
function playButtonClick(el, state){
    if(state === "play"){
        player.play();
        el.src = "/static/icons/pause.svg";
        requestAnimationFrame(whilePlaying);
        state = "pause";
    }
    else if(state === "pause"){
        player.pause();
        el.src = "/static/icons/play.svg";
        cancelAnimationFrame(raf);
        state = "play";
    }
    return state;
}

/* Mute Button */
let volState = "unmute";
function muteButtonClick(state){
    if(state === "unmute"){
        player.muted = true;
        currentVol.textContent = "0";
        volSlider.value = "0";
        muteButton.classList.add("muted");
        state = "mute"
    } else if(state === "mute"){
        player.muted = false;
        currentVol.textContent = player.volume * 100;
        volSlider.value = player.volume * 100;
        muteButton.classList.remove("muted");
        state = "unmute";
    }
    return state;
}

function displayAudioDuration(){
    duration.textContent = formatTime(player.duration);
}

/* Progress Bar Functions */
function progressMax(){
    progress.max = Math.floor(player.duration);
}

function displayBufferedAmt(){
    const bufferedAmt = Math.floor(player.buffered.end(player.buffered.length - 1));
    const bufferWidth = `${(bufferedAmt / progress.max) * 100}%`;
    controlContainer.style.setProperty("--buffered-width", bufferWidth);
}

function showSliderBefore(range){
    if(range === progress){
        controlContainer.style.setProperty("--seek-before-width", (range.value / range.max) * 100 + "%");
    } else if(range === volSlider){
        controlContainer.style.setProperty("--volume-before-width", (range.value / range.max) * 100 + "%");
    }
}

/* Volume Functions */
function volControl(ev){
    const val = ev.target.value;
    currentVol.textContent = val;
    player.volume = val / 100;
    if(val === "0"){
        volState = "mute";
        player.muted = true;
        muteButton.classList.add("muted");
    } else{
        volState = "unmute";
        player.muted = false;
        muteButton.classList.remove("muted");
    }
}

/* Implement Initial Functions */
if(player.readyState === true && player.readyState > 0){
    displayAudioDuration();
    progressMax();
    displayBufferedAmt();
    player.addEventListener("progress", 
        function(){
            displayBufferedAmt();
        }
    );
} else{
    player.addEventListener(
        "loadedmetadata",
        function(){
            displayAudioDuration();
            progressMax();
            displayBufferedAmt();
            player.addEventListener("progress", 
                function(){
                    displayBufferedAmt();
                }
            );
        }
    )
}

/* Event Listeners */
playButton.addEventListener(                                    
    "click", 
    function(){
        playState = playButtonClick(playIcon, playState);
    }
);

muteButton.addEventListener(
    "click",
    function(){
        volState = muteButtonClick(volState);
    }
);

progress.addEventListener(                                      // Progress Bar Function
    "change",
    function(){
        player.currentTime = progress.value;
        if(!player.paused){
            requestAnimationFrame(whilePlaying);
        }
    }
);

progress.addEventListener(                                      // Progress Bar Display
    "input",
    function(ev){
        currentTime.textContent = formatTime(progress.value);
        showSliderBefore(ev.target);
        if(!player.paused){
            cancelAnimationFrame(raf);
        }
    }
);

volSlider.addEventListener(
    "input",
    function(ev){
        volControl(ev);
        showSliderBefore(ev.target);
    }
);