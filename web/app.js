// ===== Page Routing =====
function showPage(pageId) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('visible'));
  document.getElementById(`page-${pageId}`).classList.add('visible');
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  const navLink = document.querySelector(`.nav-link[data-page="${pageId}"]`);
  if (navLink) navLink.classList.add('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });
  history.replaceState(null, '', `#${pageId}`);

  if (pageId === 'home' && typeof initDashboard === 'function') {
    initDashboard();
  }
}

function quickAsk(question) {
  showPage('chat');
  setTimeout(() => {
    document.getElementById('msg-input').value = question;
    sendMessage();
  }, 350);
}

document.querySelectorAll('[data-page]').forEach(el => {
  el.addEventListener('click', () => showPage(el.dataset.page));
});

// Init page from URL hash
const initialPage = window.location.hash.replace('#', '') || 'home';
showPage(['home', 'chat', 'about'].includes(initialPage) ? initialPage : 'home');

// ===== Chat Logic =====
const messagesEl = document.getElementById('messages');
const input = document.getElementById('msg-input');
const sendBtn = document.getElementById('send-btn');
const errorBanner = document.getElementById('error-banner');
const clearBtn = document.getElementById('clear-btn');
let selectedLang = 'auto';

document.querySelectorAll('.lang-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    selectedLang = btn.dataset.lang;
  });
});

document.querySelectorAll('.example-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    input.value = btn.dataset.q;
    sendMessage();
  });
});

clearBtn.addEventListener('click', () => {
  messagesEl.innerHTML = `
    <div class="empty-state" id="empty-state">
      <div class="emoji">🌾</div>
      <h4>Namaste! Ask me anything about your farm.</h4>
      <p>I'll coordinate weather, crop, market, and pest agents to give you the best advice — in your language.</p>
    </div>`;
  resetAgentStatus();
});

function resetAgentStatus() {
  document.querySelectorAll('.agent-status').forEach(el => el.classList.remove('active'));
}

function setAgentsActive(agents) {
  resetAgentStatus();
  agents.forEach(agent => {
    const el = document.querySelector(`.agent-status[data-agent="${agent}"]`);
    if (el) el.classList.add('active');
  });
}

function addMessage(text, sender, agentsUsed) {
  const empty = document.getElementById('empty-state');
  if (empty) empty.remove();

  const row = document.createElement('div');
  row.className = `msg-row ${sender}`;

  const avatar = document.createElement('div');
  avatar.className = `avatar ${sender}`;
  avatar.innerHTML = sender === 'user' ? '<i class="ti ti-user"></i>' : '<i class="ti ti-plant-2"></i>';

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';
  bubble.textContent = text;

  if (agentsUsed && agentsUsed.length) {
    const tag = document.createElement('div');
    tag.className = 'agents-tag';
    tag.innerHTML = '<i class="ti ti-robot" style="font-size:11px"></i> Agents consulted:';
    agentsUsed.forEach(a => {
      const chip = document.createElement('span');
      chip.className = 'agent-chip';
      chip.textContent = a;
      tag.appendChild(chip);
    });
    bubble.appendChild(tag);
  }

  row.appendChild(avatar);
  row.appendChild(bubble);
  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return row;
}

function addLoading() {
  const row = document.createElement('div');
  row.className = 'msg-row bot loading';
  row.id = 'loading-row';
  row.innerHTML = `
    <div class="avatar bot"><i class="ti ti-plant-2"></i></div>
    <div class="msg-bubble"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>
  `;
  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function removeLoading() {
  const el = document.getElementById('loading-row');
  if (el) el.remove();
}

async function sendMessage() {
  const message = input.value.trim();
  if (!message) return;

  errorBanner.classList.add('hidden');
  addMessage(message, 'user');
  input.value = '';
  sendBtn.disabled = true;
  addLoading();

  const payload = {
    message: message,
    state: document.getElementById('state').value,
    soil_type: document.getElementById('soil').value,
    season: document.getElementById('season').value,
    crop: document.getElementById('crop').value,
    language: selectedLang
  };

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    let data;
    try {
      data = await res.json();
    } catch {
      throw new Error('Server returned an invalid response.');
    }

    removeLoading();

    if (!res.ok) {
      errorBanner.textContent = data.detail || `Server error (${res.status}). Check the terminal running server.py.`;
      errorBanner.classList.remove('hidden');
      resetAgentStatus();
    } else {
      setAgentsActive(data.agents_used || []);
      addMessage(data.response, 'bot', data.agents_used);
      if (typeof saveToHistory === 'function') {
        saveToHistory(message, data.response, data.agents_used || []);
      }
    }
  } catch (err) {
    removeLoading();
    errorBanner.textContent = 'Could not reach the server. Make sure "python server.py" is running in your terminal, then refresh this page.';
    errorBanner.classList.remove('hidden');
    resetAgentStatus();
  } finally {
    sendBtn.disabled = false;
  }
}

sendBtn.addEventListener('click', sendMessage);
input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') sendMessage();
});

// Health check on load
fetch('/api/health').then(r => r.json()).then(data => {
  if (data.status !== 'ok') {
    errorBanner.textContent = `Server started with an error: ${data.detail}. Check your GROQ_API_KEY in config/settings.py`;
    errorBanner.classList.remove('hidden');
  }
}).catch(() => {
  errorBanner.textContent = 'Could not reach the server. Make sure "python server.py" is running.';
  errorBanner.classList.remove('hidden');
});
