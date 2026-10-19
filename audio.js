// Web Audio API Synthesizer for Retro Arcade Sounds
class SoundEngine {
  constructor() {
    this.ctx = null;
    this.soundEnabled = true;
    this.musicEnabled = false;
    this.musicInterval = null;
    this.musicStep = 0;
  }

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioCtx();
    }
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  toggleSound() {
    this.soundEnabled = !this.soundEnabled;
    return this.soundEnabled;
  }

  toggleMusic() {
    this.musicEnabled = !this.musicEnabled;
    if (this.musicEnabled) {
      this.init();
      this.startMusic();
    } else {
      this.stopMusic();
    }
    return this.musicEnabled;
  }

  // Soft click/move
  playMove() {
    if (!this.soundEnabled) return;
    this.init();
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(320, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(180, this.ctx.currentTime + 0.05);

      gain.gain.setValueAtTime(0.08, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.05);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start();
      osc.stop(this.ctx.currentTime + 0.05);
    } catch (e) {}
  }

  // Rotate sound (rising pitch chirp)
  playRotate() {
    if (!this.soundEnabled) return;
    this.init();
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(420, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(680, this.ctx.currentTime + 0.08);

      gain.gain.setValueAtTime(0.12, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.08);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start();
      osc.stop(this.ctx.currentTime + 0.08);
    } catch (e) {}
  }

  // Soft lock / drop
  playDrop() {
    if (!this.soundEnabled) return;
    this.init();
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(220, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(80, this.ctx.currentTime + 0.09);

      gain.gain.setValueAtTime(0.15, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.09);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start();
      osc.stop(this.ctx.currentTime + 0.09);
    } catch (e) {}
  }

  // Hard drop punch
  playHardDrop() {
    if (!this.soundEnabled) return;
    this.init();
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(180, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(40, this.ctx.currentTime + 0.16);

      gain.gain.setValueAtTime(0.25, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.16);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start();
      osc.stop(this.ctx.currentTime + 0.16);
    } catch (e) {}
  }

  // Hold piece ping
  playHold() {
    if (!this.soundEnabled) return;
    this.init();
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(500, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(750, this.ctx.currentTime + 0.1);

      gain.gain.setValueAtTime(0.12, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.1);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start();
      osc.stop(this.ctx.currentTime + 0.1);
    } catch (e) {}
  }

  // Line Clear sound - pitch rises with more lines
  playLineClear(linesCount) {
    if (!this.soundEnabled) return;
    this.init();
    try {
      const isTetris = linesCount >= 4;
      const notes = isTetris ? [440, 554.37, 659.25, 880, 1108.73] : [523.25, 659.25, 783.99];
      const duration = isTetris ? 0.08 : 0.06;

      notes.forEach((freq, idx) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = isTetris ? 'sawtooth' : 'square';
        osc.frequency.setValueAtTime(freq, this.ctx.currentTime + idx * duration);

        const startTime = this.ctx.currentTime + idx * duration;
        gain.gain.setValueAtTime(0.15, startTime);
        gain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.2);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(startTime);
        osc.stop(startTime + 0.2);
      });
    } catch (e) {}
  }

  // Level Up Fanfare
  playLevelUp() {
    if (!this.soundEnabled) return;
    this.init();
    try {
      const notes = [392, 523.25, 659.25, 783.99, 1046.5];
      notes.forEach((freq, idx) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'triangle';
        const startTime = this.ctx.currentTime + idx * 0.09;
        osc.frequency.setValueAtTime(freq, startTime);

        gain.gain.setValueAtTime(0.18, startTime);
        gain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.25);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(startTime);
        osc.stop(startTime + 0.25);
      });
    } catch (e) {}
  }

  // Game Over Sound
  playGameOver() {
    if (!this.soundEnabled) return;
    this.init();
    try {
      const notes = [440, 415.3, 392, 369.99, 349.23, 220];
      notes.forEach((freq, idx) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sawtooth';
        const startTime = this.ctx.currentTime + idx * 0.12;
        osc.frequency.setValueAtTime(freq, startTime);

        gain.gain.setValueAtTime(0.2, startTime);
        gain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.25);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(startTime);
        osc.stop(startTime + 0.25);
      });
    } catch (e) {}
  }

  // Ambient 8-bit / Synthwave background arpeggiator loop
  startMusic() {
    this.stopMusic();
    // Classic Korobeiniki (Tetris theme A) simplified melodic motifs
    const melody = [
      659.25, 493.88, 523.25, 587.33, 523.25, 493.88, 440,
      440, 523.25, 659.25, 587.33, 523.25, 493.88,
      523.25, 587.33, 659.25, 523.25, 440, 440, 0
    ];
    const bass = [
      164.81, 130.81, 146.83, 123.47, 110.00, 130.81, 123.47, 164.81
    ];

    let noteIdx = 0;
    let bassIdx = 0;
    this.musicInterval = setInterval(() => {
      if (!this.musicEnabled || !this.ctx) return;

      try {
        const freq = melody[noteIdx % melody.length];
        if (freq > 0) {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
          gain.gain.setValueAtTime(0.035, this.ctx.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + 0.22);
          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start();
          osc.stop(this.ctx.currentTime + 0.22);
        }

        // Bass beat
        if (noteIdx % 2 === 0) {
          const bFreq = bass[bassIdx % bass.length];
          const bOsc = this.ctx.createOscillator();
          const bGain = this.ctx.createGain();
          bOsc.type = 'triangle';
          bOsc.frequency.setValueAtTime(bFreq, this.ctx.currentTime);
          bGain.gain.setValueAtTime(0.04, this.ctx.currentTime);
          bGain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + 0.35);
          bOsc.connect(bGain);
          bGain.connect(this.ctx.destination);
          bOsc.start();
          bOsc.stop(this.ctx.currentTime + 0.35);
          bassIdx++;
        }

        noteIdx++;
      } catch (e) {}
    }, 240);
  }

  stopMusic() {
    if (this.musicInterval) {
      clearInterval(this.musicInterval);
      this.musicInterval = null;
    }
  }
}

window.soundEngine = new SoundEngine();
