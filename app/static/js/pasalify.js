// Pasalify main JS
document.addEventListener('DOMContentLoaded', function () {

  // Notification count polling
  if (document.getElementById('notif-count')) {
    function fetchNotifCount() {
      fetch('/customer/notifications/count')
        .then(r => r.json())
        .then(d => {
          const el = document.getElementById('notif-count');
          if (d.count > 0) { el.textContent = d.count; el.style.display = 'inline'; }
          else el.style.display = 'none';
        }).catch(() => {});
    }
    fetchNotifCount();
    setInterval(fetchNotifCount, 30000);
  }

  // Promo code AJAX
  const promoBtn = document.getElementById('apply-promo-btn');
  if (promoBtn) {
    promoBtn.addEventListener('click', function () {
      const code     = document.getElementById('promo_code').value.trim();
      const subtotal = parseFloat(document.getElementById('subtotal-val').value || 0);
      if (!code) return;
      fetch('/customer/promo/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ code, subtotal,
          [document.querySelector('[name=csrf_token]').name]:
           document.querySelector('[name=csrf_token]').value })
      })
      .then(r => r.json())
      .then(d => {
        const el = document.getElementById('promo-msg');
        el.style.display = 'block';
        if (d.valid) {
          el.className = 'alert alert-success';
          el.textContent = d.message;
          const tot = document.getElementById('total-display');
          if (tot) tot.textContent = 'Rs. ' + (subtotal - d.discount).toFixed(2);
          document.getElementById('discount-row').style.display = 'flex';
          document.getElementById('discount-val').textContent  = '- Rs. ' + d.discount.toFixed(2);
        } else {
          el.className = 'alert alert-danger';
          el.textContent = d.message;
        }
      });
    });
  }

  // Support chatbot
  const chatForm = document.getElementById('chatbot-form');
  if (chatForm) {
    chatForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const inp = document.getElementById('chat-input');
      const msg = inp.value.trim();
      if (!msg) return;
      appendMsg(msg, 'me');
      inp.value = '';
      fetch('/customer/support/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ message: msg,
          [document.querySelector('[name=csrf_token]').name]:
           document.querySelector('[name=csrf_token]').value })
      })
      .then(r => r.json())
      .then(d => appendMsg(d.reply, 'bot'));
    });
    function appendMsg(text, who) {
      const box = document.getElementById('chat-messages');
      const div = document.createElement('div');
      div.className = 'msg-bubble ' + (who === 'me' ? 'msg-me' : 'msg-other');
      div.innerHTML = `<span>${text}</span><span class="msg-time">${new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})}</span>`;
      box.appendChild(div);
      box.scrollTop = box.scrollHeight;
    }
  }

  // Store color preview
  const colorInp = document.getElementById('theme_color');
  const preview  = document.getElementById('color-preview');
  if (colorInp && preview) {
    colorInp.addEventListener('input', () => {
      preview.style.background = colorInp.value;
    });
  }

  // Image preview on file select
  document.querySelectorAll('.img-upload').forEach(inp => {
    inp.addEventListener('change', function () {
      const prev = document.getElementById(inp.dataset.preview);
      if (!prev) return;
      const file = this.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = e => { prev.src = e.target.result; prev.style.display = 'block'; };
        reader.readAsDataURL(file);
      }
    });
  });

  // Auto-scroll chat box to bottom
  document.querySelectorAll('.chat-box').forEach(b => { b.scrollTop = b.scrollHeight; });

  // Rating star interaction
  document.querySelectorAll('.star-rating label').forEach(lbl => {
    lbl.addEventListener('mouseover', () => lbl.style.color = '#F59E0B');
    lbl.addEventListener('mouseout',  () => lbl.style.color = '');
  });
});
