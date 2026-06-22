// Pasalify main JS
// Small, focused behaviours for pages that need a bit of interactivity
// without a full frontend framework: notification polling, two AJAX
// forms (promo codes + the support chatbot), live previews, and a
// couple of small UX touches (chat auto-scroll, star-rating hover).
// Everything below runs once the DOM is ready, and each block checks
// for its own target element first, so this one file can safely be
// included on every page even if a given block's elements aren't present.
document.addEventListener('DOMContentLoaded', function () {

  // ── Notification bell badge ──────────────────────────────────────────
  // Polls the unread-count endpoint every 30 seconds and shows/hides
  // the little red badge on the bell icon in the navbar.
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

  // ── Promo code "Apply" button on the checkout page ──────────────────
  // Sends the typed code + current subtotal to the server via AJAX
  // (instead of a full page reload) and updates the total/discount
  // row in place based on the JSON response.
  const promoBtn = document.getElementById('apply-promo-btn');
  if (promoBtn) {
    promoBtn.addEventListener('click', function () {
      const code     = document.getElementById('promo_code').value.trim();
      const subtotal = parseFloat(document.getElementById('subtotal-val').value || 0);
      if (!code) return;
      fetch('/customer/promo/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        // The CSRF token field's name/value are read straight off the
        // form so this still works no matter what Flask-WTF names it.
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

  // ── Support chatbot widget ───────────────────────────────────────────
  // Submitting the chat form doesn't reload the page: the user's
  // message is appended immediately, then the bot's keyword-matched
  // reply (from CustomerController.support_chat) is appended once it
  // comes back from the server.
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
    // Builds one chat bubble (mine or the bot's) with a timestamp,
    // then scrolls the box down so the newest message is visible.
    function appendMsg(text, who) {
      const box = document.getElementById('chat-messages');
      const div = document.createElement('div');
      div.className = 'msg-bubble ' + (who === 'me' ? 'msg-me' : 'msg-other');
      div.innerHTML = `<span>${text}</span><span class="msg-time">${new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})}</span>`;
      box.appendChild(div);
      box.scrollTop = box.scrollHeight;
    }
  }

  // ── Live theme-color preview on the seller's store customization page ─
  // As the seller drags the color picker, the swatch next to it updates
  // immediately so they can see the color before saving.
  const colorInp = document.getElementById('theme_color');
  const preview  = document.getElementById('color-preview');
  if (colorInp && preview) {
    colorInp.addEventListener('input', () => {
      preview.style.background = colorInp.value;
    });
  }

  // ── Image preview before upload (product photos, logos, banners) ────
  // Reads the chosen file straight off the disk via FileReader and
  // shows it in an <img> immediately — no server round-trip needed
  // just to preview what was selected.
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

  // ── Auto-scroll any chat box to its most recent message on load ─────
  document.querySelectorAll('.chat-box').forEach(b => { b.scrollTop = b.scrollHeight; });

  // ── Star-rating hover effect on the review form ─────────────────────
  // Highlights a star gold on hover, then reverts to its default
  // color when the mouse leaves (the actual "selected" rating is
  // handled by the radio inputs themselves, in CSS).
  document.querySelectorAll('.star-rating label').forEach(lbl => {
    lbl.addEventListener('mouseover', () => lbl.style.color = '#F59E0B');
    lbl.addEventListener('mouseout',  () => lbl.style.color = '');
  });
});
