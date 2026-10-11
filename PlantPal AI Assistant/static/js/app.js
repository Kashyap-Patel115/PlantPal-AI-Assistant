/**
 * app.js - PlantPal Vanilla JavaScript Interactions
 * =================================================
 * Beginner-friendly script for handling:
 * - Mobile sidebar navigation toggle
 * - AJAX watering updates (no full page reload)
 * - Task status toggle
 * - Daily gardening challenge completion & progress bar
 * - Interactive AI Assistant chat with SmolLM2 360M & fallback rendering
 */

document.addEventListener("DOMContentLoaded", () => {
  initMobileNav();
  initFlashDismiss();
  initAjaxWatering();
  initTaskToggles();
  initChallengeToggles();
  initAiChat();
});

/* -------------------------------------------------------------
 * 1. Mobile Navigation Drawer Toggle
 * ----------------------------------------------------------- */
function initMobileNav() {
  const menuBtn = document.getElementById("mobileMenuBtn");
  const sidebar = document.getElementById("sidebar");

  if (menuBtn && sidebar) {
    menuBtn.addEventListener("click", () => {
      sidebar.classList.toggle("open");
    });

    // Close when clicking outside
    document.addEventListener("click", (e) => {
      if (sidebar.classList.contains("open") && !sidebar.contains(e.target) && !menuBtn.contains(e.target)) {
        sidebar.classList.remove("open");
      }
    });
  }
}

/* -------------------------------------------------------------
 * 2. Flash Message Auto-dismiss & Close Button
 * ----------------------------------------------------------- */
function initFlashDismiss() {
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach((alert) => {
    const closeBtn = alert.querySelector(".alert-close");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        alert.style.opacity = "0";
        setTimeout(() => alert.remove(), 250);
      });
    }

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      if (alert && alert.parentElement) {
        alert.style.opacity = "0";
        setTimeout(() => alert.remove(), 250);
      }
    }, 5000);
  });
}

/* -------------------------------------------------------------
 * 3. Asynchronous "Mark as Watered"
 * ----------------------------------------------------------- */
function initAjaxWatering() {
  document.querySelectorAll(".btn-water-ajax").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      e.preventDefault();
      const plantId = btn.getAttribute("data-plant-id");
      if (!plantId) return;

      const originalHtml = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = `<span style="font-size:12px;">Watering...</span>`;

      try {
        const response = await fetch(`/plants/${plantId}/water`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest"
          },
          body: JSON.stringify({ notes: "Watered via quick action" })
        });

        const data = await response.json();
        if (data.success) {
          btn.innerHTML = `✓ Watered!`;
          btn.classList.remove("btn-primary");
          btn.classList.add("btn-secondary");

          // Update any nearby badge or schedule text
          const card = btn.closest(".plant-card, .reminder-item, .scheduler-row");
          if (card) {
            const badge = card.querySelector(".plant-status-badge, .status-pill");
            if (badge) {
              badge.className = "plant-status-badge badge-upcoming";
              badge.textContent = data.status_label || "Due in upcoming days";
            }
          }

          setTimeout(() => {
            btn.innerHTML = `Watered Today`;
          }, 1500);
        } else {
          btn.innerHTML = originalHtml;
          btn.disabled = false;
          alert(data.error || "Could not water plant.");
        }
      } catch (err) {
        console.error("Watering error:", err);
        btn.innerHTML = originalHtml;
        btn.disabled = false;
      }
    });
  });
}

/* -------------------------------------------------------------
 * 4. Care Task Completion Toggle
 * ----------------------------------------------------------- */
function initTaskToggles() {
  document.querySelectorAll(".task-toggle-checkbox").forEach((checkbox) => {
    checkbox.addEventListener("change", async () => {
      const taskId = checkbox.getAttribute("data-task-id");
      const taskItem = checkbox.closest(".task-item");

      try {
        const res = await fetch(`/tasks/${taskId}/toggle`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest"
          }
        });

        if (res.ok) {
          if (taskItem) {
            taskItem.classList.toggle("completed", checkbox.checked);
          }
        } else {
          checkbox.checked = !checkbox.checked;
        }
      } catch (err) {
        console.error("Task toggle failed:", err);
        checkbox.checked = !checkbox.checked;
      }
    });
  });
}

/* -------------------------------------------------------------
 * 5. Daily Gardening Challenge Toggle
 * ----------------------------------------------------------- */
function initChallengeToggles() {
  document.querySelectorAll(".challenge-toggle-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const challengeKey = btn.getAttribute("data-challenge-key");
      const card = btn.closest(".challenge-card");

      try {
        const res = await fetch(`/challenges/${challengeKey}/toggle`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest"
          }
        });

        const data = await res.json();
        if (data.success) {
          // Toggle card visual state
          if (card) {
            const isCompleted = card.classList.toggle("is-completed");
            btn.textContent = isCompleted ? "✓ Completed" : "Mark as Done";
            btn.className = isCompleted
              ? "btn btn-secondary btn-sm challenge-toggle-btn"
              : "btn btn-outline btn-sm challenge-toggle-btn";
          }

          // Update progress bar
          const fill = document.getElementById("challengeProgressFill");
          const text = document.getElementById("challengeProgressText");
          if (fill) fill.style.width = `${data.progress_percent}%`;
          if (text) text.textContent = `${data.completed_count} of 5 completed (${data.progress_percent}%)`;
        }
      } catch (err) {
        console.error("Challenge update error:", err);
      }
    });
  });
}

/* -------------------------------------------------------------
 * 6. AI Gardening Assistant Chat UI
 * ----------------------------------------------------------- */
function initAiChat() {
  const chatForm = document.getElementById("chatForm");
  const chatInput = document.getElementById("chatInput");
  const messagesBox = document.getElementById("chatMessages");
  const chipButtons = document.querySelectorAll(".chip-btn");

  if (!chatForm || !chatInput || !messagesBox) return;

  // Handle clicking quick suggestion chips
  chipButtons.forEach((chip) => {
    chip.addEventListener("click", () => {
      const question = chip.getAttribute("data-prompt") || chip.textContent.trim();
      chatInput.value = question;
      chatForm.dispatchEvent(new Event("submit"));
    });
  });

  // Handle message submission
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query) return;

    // 1. Append User Message
    appendMessage({
      sender: "user",
      text: query
    });

    chatInput.value = "";
    chatInput.disabled = true;

    // 2. Show Animated Typing Indicator
    const typingElement = appendTypingIndicator();
    scrollToBottom();

    // 3. Send to Flask Backend
    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: query })
      });

      typingElement.remove();
      chatInput.disabled = false;
      chatInput.focus();

      if (response.ok) {
        const data = await response.json();
        appendMessage({
          sender: "ai",
          text: data.answer,
          isFallback: data.is_fallback,
          source: data.source,
          note: data.note
        });
      } else {
        appendMessage({
          sender: "ai",
          text: "I encountered a hiccup answering that question. Please try asking again!",
          isFallback: true,
          source: "error"
        });
      }
    } catch (err) {
      console.error("Chat API error:", err);
      typingElement.remove();
      chatInput.disabled = false;

      appendMessage({
        sender: "ai",
        text: "Could not reach the PlantPal server. Please ensure the app is running.",
        isFallback: true,
        source: "network_error"
      });
    }

    scrollToBottom();
  });

  function appendMessage({ sender, text, isFallback = false, source = "", note = "" }) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `chat-message ${sender}`;

    let avatarSvg = sender === "user"
      ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`
      : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a10 10 0 0 1 10 10c0 5.52-4.48 10-10 10S2 17.52 2 12 6.48 2 12 2z"/><path d="M12 6v6l4 2"/></svg>`;

    let tagHtml = "";
    if (sender === "ai") {
      if (isFallback) {
        tagHtml = `<div class="chat-source-tag fallback">🌿 Verified Gardening Guide (Offline Fallback)</div>`;
      } else {
        tagHtml = `<div class="chat-source-tag ai">⚡ Powered by SmolLM2 360M (Local)</div>`;
      }
    }

    msgDiv.innerHTML = `
      <div class="chat-avatar ${sender}">${avatarSvg}</div>
      <div class="chat-bubble">
        <div class="bubble-text">${escapeHtml(text)}</div>
        ${tagHtml}
      </div>
    `;

    messagesBox.appendChild(msgDiv);
    scrollToBottom();
  }

  function appendTypingIndicator() {
    const typingDiv = document.createElement("div");
    typingDiv.className = "chat-message ai";
    typingDiv.innerHTML = `
      <div class="chat-avatar ai">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a10 10 0 0 1 10 10c0 5.52-4.48 10-10 10S2 17.52 2 12 6.48 2 12 2z"/></svg>
      </div>
      <div class="chat-bubble">
        <div class="typing-dots">
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
        </div>
      </div>
    `;
    messagesBox.appendChild(typingDiv);
    return typingDiv;
  }

  function scrollToBottom() {
    messagesBox.scrollTop = messagesBox.scrollHeight;
  }

  function escapeHtml(string) {
    const div = document.createElement("div");
    div.innerText = string;
    return div.innerHTML;
  }
}
