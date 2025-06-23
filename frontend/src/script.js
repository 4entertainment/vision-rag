const API_URL = window.location.origin;
let lastText = null;
let recognizing = false;
const video = document.getElementById('video');

function appendMessage(text, sender) {
  const chat = document.getElementById('chatWindow');
  const msg = document.createElement('div');
  msg.className = `message ${sender}`;
  msg.innerText = text;
  chat.appendChild(msg);
  chat.scrollTop = chat.scrollHeight;
}

document.getElementById('sendBtn').onclick = async () => {
  const input = document.getElementById('textInput');
  const text = input.value.trim(); if (!text) return;
  appendMessage(text, 'user'); input.value = '';
  const res = await fetch(`${API_URL}/query`, {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ text })
  });
  const data = await res.json();
  appendMessage(data.response, 'bot');
};

document.querySelector('#docUpload').onchange = async (e) => {
  const file = e.target.files[0]; if (!file) return;
  const form = new FormData(); form.append('file', file);
  await fetch(`${API_URL}/upload_doc`, { method: 'POST', body: form });
  appendMessage('Doküman yüklendi ve indekslendi.', 'bot');
};

document.getElementById('cameraBtn').onclick = async () => {
  if (!recognizing) {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
    recognizing = true;
    processFrame();
  }
};

async function processFrame() {
  if (!recognizing) return;
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);
  canvas.toBlob(async blob => {
    const form = new FormData();
    form.append('file', blob, 'frame.png');
    const res = await fetch(`${API_URL}/ocr`, { method: 'POST', body: form });
    const { text } = await res.json();
    const clean = text.trim();
    if (clean && clean !== lastText) {
      lastText = clean;
      appendMessage(`Detected: ${clean}`, 'user');
      const qr = await fetch(`${API_URL}/query`, {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ text: clean })
      });
      const data = await qr.json();
      appendMessage(data.response, 'bot');
      recognizing = false;
      video.srcObject.getTracks().forEach(t => t.stop());
    } else {
      setTimeout(processFrame, 2000);
    }
  }, 'image/png');
}
