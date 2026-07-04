// app.js – UI logic with WebSocket backend integration

let socket = null;

// ─── WebSocket ────────────────────────────────────────────────────────────────
function initWebSocket() {
  socket = new WebSocket('ws://localhost:8767');

  socket.addEventListener('open', () => {
    addMessage('assistant', '✅ Connected to OmniCore. Say or type a command…');
  });

  socket.addEventListener('message', (event) => {
    try {
      const data = JSON.parse(event.data);
      
      // Handle Operator loop HUD updates
      if (data.type === "status_update") {
        const hud = document.getElementById('operator-hud');
        if (hud) {
          hud.style.display = 'block';
          
          document.getElementById('op-status').textContent = data.status;
          document.getElementById('op-task').textContent = data.task || 'None';
          document.getElementById('op-step').textContent = data.step || 'None';
          document.getElementById('op-progress').style.width = data.percentage + '%';
          document.getElementById('op-percentage').textContent = data.percentage + '%';
          
          const opStatusEl = document.getElementById('op-status');
          opStatusEl.className = 'hud-value'; // reset classes
          
          if (data.status === 'Thinking...') opStatusEl.classList.add('status-thinking');
          else if (data.status === 'Planning...') opStatusEl.classList.add('status-planning');
          else if (data.status === 'Executing...') opStatusEl.classList.add('status-executing');
          else if (data.status === 'Observing...') opStatusEl.classList.add('status-observing');
          else if (data.status === 'Completed') {
            opStatusEl.classList.add('status-completed');
            // Hide HUD after 4 seconds of showing completion
            setTimeout(() => {
              if (document.getElementById('op-status').textContent === 'Completed') {
                hud.style.display = 'none';
              }
            }, 4000);
          }
        }
        return;
      }

      // Handle standard message replies
      if (data.role && data.content) {
        addMessage('assistant', data.content);
      }
    } catch (e) {
      addMessage('assistant', 'Error parsing response');
    }
  });

  socket.addEventListener('close', () => {
    addMessage('assistant', '🔌 Backend disconnected.');
    document.getElementById('status-dot').style.color = '#ef4444';
  });

  socket.addEventListener('error', () => {
    addMessage('assistant', '⚠️ Cannot reach backend. Run backend_server.py first.');
  });
}

// ─── Process Command ──────────────────────────────────────────────────────────
function processCommand(text) {
  if (!text.trim()) return;

  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ role: 'user', content: text }));
  } else {
    addMessage('assistant', '⚠️ Backend not connected. Start backend_server.py first.');
  }
}

// ─── Add message to conversation ──────────────────────────────────────────────
function addMessage(sender, text) {
  const convo = document.getElementById('conversation');
  const msg = document.createElement('div');
  msg.className = `msg ${sender}`;
  msg.textContent = text;
  convo.appendChild(msg);
  convo.scrollTop = convo.scrollHeight;
}

// ─── Voice Recognition ────────────────────────────────────────────────────────
function setupVoice(micBtn, onResult) {
  if (!window.SpeechRecognition && !window.webkitSpeechRecognition) {
    if (micBtn) micBtn.style.display = 'none';
    return null;
  }
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  const rec = new SR();
  rec.lang = 'en-IN';
  rec.interimResults = true;
  rec.continuous = true;
  rec.maxAlternatives = 1;

  let micActive = false;
  let silenceTimer = null;
  let lastTranscript = '';

  rec.onstart = () => {
    lastTranscript = '';
    micBtn && micBtn.classList.add('mic-active');
  };
  rec.onerror = (e) => {
    if (e.error !== 'aborted' && e.error !== 'no-speech') {
      addMessage('assistant', '⚠️ Voice error: ' + e.error);
    }
    clearTimeout(silenceTimer);
    micActive = false;
    micBtn && micBtn.classList.remove('mic-active');
  };
  rec.onresult = (e) => {
    let interim = '', final = '';
    for (let i = 0; i < e.results.length; i++) {
      e.results[i].isFinal
        ? (final += e.results[i][0].transcript)
        : (interim += e.results[i][0].transcript);
    }
    const current = (final + interim).trim();
    if (current) lastTranscript = current;

    clearTimeout(silenceTimer);
    silenceTimer = setTimeout(() => {
      if (lastTranscript) {
        addMessage('user', lastTranscript);
        onResult(lastTranscript);
        lastTranscript = '';
      }
      try { rec.stop(); } catch (_) {}
      micActive = false;
      micBtn && micBtn.classList.remove('mic-active');
    }, 1200);
  };
  rec.onend = () => {
    clearTimeout(silenceTimer);
    if (lastTranscript) {
      addMessage('user', lastTranscript);
      onResult(lastTranscript);
      lastTranscript = '';
    }
    micActive = false;
    micBtn && micBtn.classList.remove('mic-active');
  };

  micBtn && micBtn.addEventListener('click', () => {
    if (!micActive) {
      micActive = true;
      lastTranscript = '';
      clearTimeout(silenceTimer);
      try { rec.start(); } catch (_) {}
    } else {
      try { rec.stop(); } catch (_) {}
    }
  });

  return rec;
}

// ─── Init ─────────────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  initWebSocket();

  const sendBtn   = document.getElementById('send-btn');
  const userInput = document.getElementById('user-input');
  const micBtn    = document.getElementById('mic-btn');

  sendBtn.addEventListener('click', () => {
    const text = userInput.value.trim();
    if (!text) return;
    addMessage('user', text);
    userInput.value = '';
    processCommand(text);
  });
  userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendBtn.click();
  });
  setupVoice(micBtn, processCommand);
});
