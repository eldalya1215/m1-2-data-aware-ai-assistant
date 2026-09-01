const API = (window.APP_CONFIG?.API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

const state = { data: [], messages: [], conversationId: null, conversations: [] };
const $ = (selector) => document.querySelector(selector);

async function request(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `요청 실패 (${response.status})`);
  }
  if (response.status === 204) return null;
  return response.json();
}

function toast(message) {
  const element = $("#toast");
  element.textContent = message;
  element.classList.add("show");
  window.setTimeout(() => element.classList.remove("show"), 2200);
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[char]);
}

async function checkHealth() {
  try {
    const health = await request("/api/health");
    const element = $("#api-status");
    element.textContent = `API 연결 · ${health.storage_backend}/${health.ai_backend}`;
    element.classList.add("online");
  } catch {
    $("#api-status").textContent = "API 연결 대기 중";
  }
}

async function loadSummary() {
  const summary = await request("/api/data/summary");
  const change = summary.recent_change_pct == null ? "계산 불가" : `${summary.recent_change_pct > 0 ? "+" : ""}${summary.recent_change_pct}%`;
  $("#summary-grid").innerHTML = `
    <div class="metric"><span>데이터 기간</span><strong>${escapeHtml(summary.period)}</strong></div>
    <div class="metric"><span>레코드</span><strong>${summary.count.toLocaleString()}개</strong></div>
    <div class="metric"><span>최근 값</span><strong>${summary.metrics.latest.toLocaleString()} ${summary.unit}</strong></div>
    <div class="metric"><span>최근 추세</span><strong>${summary.trend} · ${change}</strong></div>`;
}

async function loadData() {
  state.data = await request("/api/data");
  $("#data-count").textContent = `${state.data.length} records`;
  const recent = [...state.data].reverse().slice(0, 30);
  $("#data-table").innerHTML = recent.map((record) => `
    <tr>
      <td>${escapeHtml(record.date)}</td>
      <td>${Number(record.value).toLocaleString()}</td>
      <td>${escapeHtml(record.memo || "-")}</td>
      <td><div class="row-actions">
        <button type="button" data-edit="${record.id}">수정</button>
        <button type="button" class="delete" data-delete="${record.id}">삭제</button>
      </div></td>
    </tr>`).join("");
  drawChart(state.data.slice(-48));
}

function drawChart(records) {
  const canvas = $("#trend-chart");
  const ratio = window.devicePixelRatio || 1;
  const width = canvas.clientWidth || 600;
  const height = 350;
  canvas.width = width * ratio;
  canvas.height = height * ratio;
  const ctx = canvas.getContext("2d");
  ctx.scale(ratio, ratio);
  ctx.clearRect(0, 0, width, height);
  if (!records.length) return;

  const styles = getComputedStyle(document.documentElement);
  const line = styles.getPropertyValue("--line").trim();
  const primary = styles.getPropertyValue("--primary").trim();
  const muted = styles.getPropertyValue("--muted").trim();
  const values = records.map((item) => Number(item.value));
  const min = Math.min(...values);
  const max = Math.max(...values);
  const pad = { top: 20, right: 16, bottom: 38, left: 52 };
  const chartW = width - pad.left - pad.right;
  const chartH = height - pad.top - pad.bottom;
  const x = (index) => pad.left + (index / Math.max(1, records.length - 1)) * chartW;
  const y = (value) => pad.top + chartH - ((value - min) / Math.max(1, max - min)) * chartH;

  ctx.strokeStyle = line;
  ctx.fillStyle = muted;
  ctx.font = "12px system-ui";
  for (let i = 0; i <= 4; i += 1) {
    const yy = pad.top + (i / 4) * chartH;
    ctx.beginPath(); ctx.moveTo(pad.left, yy); ctx.lineTo(width - pad.right, yy); ctx.stroke();
    const label = Math.round(max - (i / 4) * (max - min));
    ctx.fillText(label.toLocaleString(), 6, yy + 4);
  }
  ctx.strokeStyle = primary;
  ctx.lineWidth = 3;
  ctx.beginPath();
  records.forEach((item, index) => index ? ctx.lineTo(x(index), y(item.value)) : ctx.moveTo(x(index), y(item.value)));
  ctx.stroke();
  ctx.fillStyle = muted;
  [0, Math.floor((records.length - 1) / 2), records.length - 1].forEach((index) => {
    const label = records[index].date.slice(0, 7);
    ctx.fillText(label, Math.min(width - 70, x(index) - 22), height - 12);
  });
}

function resetDataForm() {
  $("#data-form").reset();
  $("#data-id").value = "";
  $("#data-submit").textContent = "추가";
  $("#data-cancel").classList.add("hidden");
}

async function saveData(event) {
  event.preventDefault();
  const id = $("#data-id").value;
  const payload = { date: $("#data-date").value, value: Number($("#data-value").value), memo: $("#data-memo").value.trim() };
  await request(id ? `/api/data/${id}` : "/api/data", { method: id ? "PUT" : "POST", body: JSON.stringify(payload) });
  toast(id ? "데이터를 수정했습니다." : "데이터를 추가했습니다.");
  resetDataForm();
  await Promise.all([loadData(), loadSummary()]);
}

async function onDataTableClick(event) {
  const editId = event.target.dataset.edit;
  const deleteId = event.target.dataset.delete;
  if (editId) {
    const record = state.data.find((item) => item.id === editId);
    if (!record) return;
    $("#data-id").value = record.id;
    $("#data-date").value = record.date;
    $("#data-value").value = record.value;
    $("#data-memo").value = record.memo;
    $("#data-submit").textContent = "저장";
    $("#data-cancel").classList.remove("hidden");
    $("#data-date").focus();
  }
  if (deleteId && window.confirm("이 데이터를 삭제할까요?")) {
    await request(`/api/data/${deleteId}`, { method: "DELETE" });
    toast("데이터를 삭제했습니다.");
    await Promise.all([loadData(), loadSummary()]);
  }
}

function renderMessages() {
  const initial = state.messages.length ? "" : '<div class="message assistant">새 대화를 시작했습니다. 데이터에 관해 질문해보세요.</div>';
  $("#messages").innerHTML = initial + state.messages.map((message) => `<div class="message ${message.role}">${escapeHtml(message.content)}</div>`).join("");
  $("#messages").scrollTop = $("#messages").scrollHeight;
}

async function sendChat(event) {
  event.preventDefault();
  const input = $("#chat-input");
  const question = input.value.trim();
  if (!question) return;
  const history = [...state.messages];
  state.messages.push({ role: "user", content: question });
  renderMessages();
  input.value = "";
  input.disabled = true;
  $("#chat-loading").classList.remove("hidden");
  try {
    const result = await request("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message: question, conversation_id: state.conversationId, history }),
    });
    state.messages.push({ role: "assistant", content: result.answer });
    state.conversationId = result.conversation_id;
    renderMessages();
    await loadConversations();
  } catch (error) {
    state.messages.push({ role: "assistant", content: `오류: ${error.message}` });
    renderMessages();
  } finally {
    input.disabled = false;
    input.focus();
    $("#chat-loading").classList.add("hidden");
  }
}

async function loadConversations() {
  state.conversations = await request("/api/conversations");
  $("#conversation-list").innerHTML = state.conversations.length ? state.conversations.map((conversation) => `
    <button type="button" class="conversation-item ${conversation.id === state.conversationId ? "active" : ""}" data-conversation="${conversation.id}">
      <strong>${escapeHtml(conversation.title)}</strong>
      <small>${new Date(conversation.updated_at).toLocaleDateString("ko-KR")} · ${conversation.messages.length}개 메시지</small>
    </button>`).join("") : '<p class="status">저장된 대화가 없습니다.</p>';
}

async function onConversationClick(event) {
  const id = event.target.closest("[data-conversation]")?.dataset.conversation;
  if (!id) return;
  const conversation = await request(`/api/conversations/${id}`);
  state.conversationId = id;
  state.messages = conversation.messages;
  renderMessages();
  await loadConversations();
}

function newChat() {
  state.conversationId = null;
  state.messages = [];
  renderMessages();
  loadConversations();
  $("#chat-input").focus();
}

function toggleTheme() {
  const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = next;
  localStorage.setItem("theme", next);
  drawChart(state.data.slice(-48));
}

async function initialize() {
  document.documentElement.dataset.theme = localStorage.getItem("theme") || "light";
  $("#csv-export").href = `${API}/api/data/export.csv`;
  $("#chat-form").addEventListener("submit", sendChat);
  $("#data-form").addEventListener("submit", saveData);
  $("#data-cancel").addEventListener("click", resetDataForm);
  $("#data-table").addEventListener("click", onDataTableClick);
  $("#conversation-list").addEventListener("click", onConversationClick);
  $("#new-chat").addEventListener("click", newChat);
  $("#theme-toggle").addEventListener("click", toggleTheme);
  window.addEventListener("resize", () => drawChart(state.data.slice(-48)));
  await checkHealth();
  try {
    await Promise.all([loadSummary(), loadData(), loadConversations()]);
  } catch (error) {
    toast(error.message);
  }
}

initialize();
