// Sonidos discretos sintetizados con WebAudio (sin archivos): acierto, error y fin de lección.
const SFX = (() => {
  let ctx = null, muted = false;
  try { muted = localStorage.getItem('qiskit:mute') === '1'; } catch (e) {}
  const ac = () => ctx || (ctx = new (window.AudioContext || window.webkitAudioContext)());

  function tone(freq, dur, { type = 'sine', vol = .08, at = 0 } = {}) {
    const c = ac(), t0 = c.currentTime + at, o = c.createOscillator(), g = c.createGain();
    o.type = type; o.frequency.setValueAtTime(freq, t0);
    g.gain.setValueAtTime(0.0001, t0);
    g.gain.exponentialRampToValueAtTime(vol, t0 + .015);
    g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
    o.connect(g).connect(c.destination);
    o.start(t0); o.stop(t0 + dur + .02);
  }
  const sounds = {
    tick: () => tone(880, .06, { vol: .03 }),
    ok:   () => { tone(660, .18); tone(990, .28, { at: .09 }); },
    no:   () => tone(220, .22, { type: 'triangle', vol: .06 }),
    done: () => [523, 659, 784].forEach((f, i) => tone(f, .35, { at: i * .12, vol: .07 }))
  };
  return {
    unlock() { try { ac().resume(); } catch (e) {} },
    play(n) { if (!muted && sounds[n]) try { sounds[n](); } catch (e) {} },
    get muted() { return muted; },
    toggle() { muted = !muted; try { localStorage.setItem('qiskit:mute', muted ? '1' : '0'); } catch (e) {} return muted; }
  };
})();
