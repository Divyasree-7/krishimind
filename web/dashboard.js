// ===================== DASHBOARD DATA LOADING =====================

const WEATHER_ICONS = {
  0: 'ti-sun', 1: 'ti-cloud-sun', 2: 'ti-cloud', 3: 'ti-cloud',
  45: 'ti-haze', 48: 'ti-haze', 51: 'ti-cloud-rain', 53: 'ti-cloud-rain',
  55: 'ti-cloud-rain', 61: 'ti-cloud-rain', 63: 'ti-cloud-rain', 65: 'ti-cloud-rain',
  71: 'ti-snowflake', 80: 'ti-cloud-storm', 81: 'ti-cloud-storm', 82: 'ti-cloud-storm',
  95: 'ti-bolt', 96: 'ti-bolt', 99: 'ti-bolt'
};

function weatherIcon(code) {
  return WEATHER_ICONS[code] || 'ti-cloud';
}

function dayName(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-US', { weekday: 'short' });
}

function getCurrentContext() {
  return {
    state: document.getElementById('dash-state')?.value || 'Maharashtra',
    soil: document.getElementById('dash-soil')?.value || 'loamy',
    season: document.getElementById('dash-season')?.value || 'kharif',
  };
}

// ===================== WEATHER WIDGET =====================

async function loadWeatherWidget() {
  const container = document.getElementById('weather-widget');
  if (!container) return;
  container.innerHTML = '<div class="widget-loading"><div class="spinner"></div></div>';

  try {
    const res = await fetch('/api/weather');
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Failed to load weather');

    const riskColors = { LOW: 'good', MEDIUM: 'warn', HIGH: 'bad' };
    const riskClass = riskColors[data.risk_level] || 'warn';

    let daysHtml = data.days.map(d => `
      <div class="forecast-day">
        <div class="fday-name">${dayName(d.date)}</div>
        <i class="ti ${weatherIcon(d.weather_code)} fday-icon"></i>
        <div class="fday-temp">${Math.round(d.max_temp)}°<span class="fday-temp-min">/${Math.round(d.min_temp)}°</span></div>
        <div class="fday-rain"><i class="ti ti-droplet"></i> ${Math.round(d.rain_prob || 0)}%</div>
      </div>
    `).join('');

    container.innerHTML = `
      <div class="weather-header">
        <div>
          <div class="weather-location"><i class="ti ti-map-pin"></i> ${data.location}</div>
          <div class="weather-current">${Math.round(data.current_temp)}°C</div>
        </div>
        <div class="risk-badge risk-${riskClass}">
          <i class="ti ti-alert-triangle"></i> ${data.risk_level} rain risk
        </div>
      </div>
      <p class="weather-advisory">${data.risk_message}</p>
      <div class="forecast-row">${daysHtml}</div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="widget-error"><i class="ti ti-alert-circle"></i> ${err.message}</div>`;
  }
}

// ===================== MARKET OVERVIEW WIDGET =====================

async function loadMarketWidget() {
  const container = document.getElementById('market-widget');
  if (!container) return;
  container.innerHTML = '<div class="widget-loading"><div class="spinner"></div></div>';

  const { state } = getCurrentContext();
  try {
    const res = await fetch(`/api/market/overview?state=${encodeURIComponent(state)}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Failed to load prices');

    const rows = data.crops.slice(0, 6).map(c => {
      const isLive = c.is_live;
      const vsMsp = c.pct_above_msp !== null ? `${c.pct_above_msp > 0 ? '+' : ''}${c.pct_above_msp}%` : '—';
      const vsMspClass = c.pct_above_msp > 0 ? 'price-up' : c.pct_above_msp < 0 ? 'price-down' : '';
      return `
        <div class="price-row" onclick="openPriceDetail('${c.crop}')">
          <div class="price-crop">${c.crop}</div>
          <div class="price-val">₹${c.current_price_per_quintal.toLocaleString('en-IN')}</div>
          <div class="price-vs-msp ${vsMspClass}">${vsMsp} MSP</div>
          ${isLive ? '<span class="live-tag">LIVE</span>' : ''}
        </div>
      `;
    }).join('');

    container.innerHTML = `
      <div class="price-list">${rows}</div>
      <p class="data-note"><i class="ti ti-info-circle"></i> ${data.crops[0]?.is_live ? 'Live Agmarknet data' : 'Sample data shown — live feed unavailable, connect a data.gov.in API key for real prices'}</p>
    `;
  } catch (err) {
    container.innerHTML = `<div class="widget-error"><i class="ti ti-alert-circle"></i> ${err.message}</div>`;
  }
}

function openPriceDetail(crop) {
  document.getElementById('crop').value = crop;
  showPage('chat');
  document.getElementById('msg-input').value = `Should I sell my ${crop} now or wait?`;
}

// ===================== PEST ALERTS WIDGET =====================

async function loadPestWidget() {
  const container = document.getElementById('pest-widget');
  if (!container) return;
  container.innerHTML = '<div class="widget-loading"><div class="spinner"></div></div>';

  try {
    const res = await fetch('/api/pest-alerts');
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Failed to load pest alerts');

    if (!data.active_alerts.length) {
      container.innerHTML = `
        <p class="pest-general"><i class="ti ti-shield-check"></i> ${data.general_alert}</p>
        <div class="empty-mini">No high-priority alerts for ${data.month}.</div>
      `;
      return;
    }

    const alerts = data.active_alerts.slice(0, 4).map(a => `
      <div class="pest-alert-item risk-${a.risk.toLowerCase()}">
        <div class="pest-alert-top">
          <span class="pest-name">${a.pest}</span>
          <span class="pest-risk-tag">${a.risk}</span>
        </div>
        <div class="pest-crop-tag">${a.crop}</div>
        <p class="pest-symptoms">${a.symptoms}</p>
      </div>
    `).join('');

    container.innerHTML = `
      <p class="pest-general"><i class="ti ti-calendar-event"></i> ${data.general_alert}</p>
      <div class="pest-alert-list">${alerts}</div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="widget-error"><i class="ti ti-alert-circle"></i> ${err.message}</div>`;
  }
}

// ===================== CROP CALENDAR WIDGET =====================

async function loadCropCalendarWidget() {
  const container = document.getElementById('calendar-widget');
  if (!container) return;
  container.innerHTML = '<div class="widget-loading"><div class="spinner"></div></div>';

  const { soil, season, state } = getCurrentContext();
  try {
    const res = await fetch(`/api/crop-calendar?soil_type=${soil}&season=${season}&state=${encodeURIComponent(state)}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Failed to load calendar');

    if (!data.suggested_crops || !data.suggested_crops.length) {
      container.innerHTML = `<div class="empty-mini">No crop matches for this combination. Try a different soil or season.</div>`;
      return;
    }

    const cards = data.suggested_crops.slice(0, 4).map(c => `
      <div class="calendar-card" onclick="openCropDetail('${c.crop}')">
        <div class="calendar-crop-name">${c.crop}</div>
        <div class="calendar-row"><i class="ti ti-seeding"></i> Sow: ${c.sowing_months.join(', ')}</div>
        <div class="calendar-row"><i class="ti ti-cut"></i> Harvest: ${c.harvest_months.join(', ')}</div>
        <div class="calendar-row"><i class="ti ti-droplet"></i> Water: ${c.water_requirement}</div>
      </div>
    `).join('');

    container.innerHTML = `<div class="calendar-grid">${cards}</div>`;
  } catch (err) {
    container.innerHTML = `<div class="widget-error"><i class="ti ti-alert-circle"></i> ${err.message}</div>`;
  }
}

function openCropDetail(crop) {
  document.getElementById('crop').value = crop;
  showPage('chat');
  document.getElementById('msg-input').value = `Tell me more about growing ${crop}`;
}

// ===================== HISTORY (localStorage) =====================

const HISTORY_KEY = 'krishimind_history';

function saveToHistory(question, answer, agentsUsed) {
  const history = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
  history.unshift({
    question, answer, agentsUsed,
    timestamp: new Date().toISOString()
  });
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(0, 50)));
}

function loadHistory() {
  return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
}

function renderHistoryWidget() {
  const container = document.getElementById('history-widget');
  if (!container) return;
  const history = loadHistory();

  if (!history.length) {
    container.innerHTML = `<div class="empty-mini">No questions asked yet. Your conversation history will appear here.</div>`;
    return;
  }

  const items = history.slice(0, 8).map((h, i) => {
    const date = new Date(h.timestamp);
    const timeStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) + ' · ' + date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    return `
      <div class="history-item" onclick="replayHistory(${i})">
        <div class="history-q">${h.question}</div>
        <div class="history-meta">${timeStr}</div>
      </div>
    `;
  }).join('');

  container.innerHTML = `<div class="history-list">${items}</div>`;
}

function replayHistory(index) {
  const history = loadHistory();
  const item = history[index];
  if (!item) return;
  showPage('chat');
  addMessage(item.question, 'user');
  addMessage(item.answer, 'bot', item.agentsUsed);
}

function clearHistory() {
  localStorage.removeItem(HISTORY_KEY);
  renderHistoryWidget();
}

// ===================== INIT DASHBOARD =====================

function initDashboard() {
  loadWeatherWidget();
  loadMarketWidget();
  loadPestWidget();
  loadCropCalendarWidget();
  renderHistoryWidget();
}

['dash-state', 'dash-soil', 'dash-season'].forEach(id => {
  document.addEventListener('DOMContentLoaded', () => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('change', () => {
      loadMarketWidget();
      loadCropCalendarWidget();
    });
  });
});
