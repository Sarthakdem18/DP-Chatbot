console.log("Delhi Police Assistant Content Script loaded");

function injectAssistant() {
  // Create outer widget wrapper
  const widget = document.createElement("div");
  widget.className = "dp-assistant-widget";

  // Create launcher button
  const launcher = document.createElement("div");
  launcher.className = "dp-assistant-launcher";
  
  const launcherIcon = document.createElement("img");
  launcherIcon.className = "dp-launcher-emblem";
  launcherIcon.src = chrome.runtime.getURL("icon.png");
  launcher.appendChild(launcherIcon);

  // Create overlay panel container
  const panel = document.createElement("div");
  panel.className = "dp-assistant-panel";

  // Create drag-and-drop header bar
  const header = document.createElement("div");
  header.className = "dp-assistant-header";
  header.innerHTML = `
    <div class="dp-header-grip">
      <span class="dp-grip-dots">⋮⋮</span> S.H.A.N.T.I
    </div>
    <div class="dp-header-close">×</div>
  `;

  // Create iframe pointing to the extension popup html
  const iframe = document.createElement("iframe");
  iframe.className = "dp-assistant-iframe";
  iframe.src = chrome.runtime.getURL("popup.html");

  panel.appendChild(header);
  panel.appendChild(iframe);
  
  widget.appendChild(panel);
  widget.appendChild(launcher);
  document.body.appendChild(widget);

  // Toggle panel visibility
  launcher.addEventListener("click", () => {
    const isVisible = panel.classList.contains("visible");
    if (isVisible) {
      panel.classList.remove("visible");
    } else {
      panel.classList.add("visible");
    }
  });

  // Close button trigger
  const closeBtn = header.querySelector(".dp-header-close");
  closeBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    panel.classList.remove("visible");
  });

  // HTML5 Dragging Logic
  let isDragging = false;
  let startX, startY;
  let initialX, initialY;

  header.addEventListener("mousedown", dragStart);

  function dragStart(e) {
    if (e.target.classList.contains("dp-header-close")) return;
    
    // Prevent text highlight when dragging
    e.preventDefault();

    isDragging = true;
    startX = e.clientX;
    startY = e.clientY;

    const rect = widget.getBoundingClientRect();
    initialX = rect.left;
    initialY = rect.top;

    // Convert fixed bottom/right layout to fixed top/left layout for smooth absolute dragging
    widget.style.bottom = "auto";
    widget.style.right = "auto";
    widget.style.left = initialX + "px";
    widget.style.top = initialY + "px";

    document.addEventListener("mousemove", drag);
    document.addEventListener("mouseup", dragEnd);
  }

  function drag(e) {
    if (!isDragging) return;

    const dx = e.clientX - startX;
    const dy = e.clientY - startY;

    let newX = initialX + dx;
    let newY = initialY + dy;

    // Constrain the panel inside the viewport boundaries
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    const widgetRect = widget.getBoundingClientRect();

    newX = Math.max(10, Math.min(newX, viewportWidth - widgetRect.width - 10));
    newY = Math.max(10, Math.min(newY, viewportHeight - widgetRect.height - 10));

    widget.style.left = newX + "px";
    widget.style.top = newY + "px";
  }

  function dragEnd() {
    isDragging = false;
    document.removeEventListener("mousemove", drag);
    document.removeEventListener("mouseup", dragEnd);
  }
}

// Inject on load if document is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", injectAssistant);
} else {
  injectAssistant();
}
