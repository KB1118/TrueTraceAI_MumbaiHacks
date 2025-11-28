// content.js — Clean version
// Only:
// 1) X.com tweet checker
// 2) Highlight → "Verify?" floating button → full analysis popup

// -------------------------------
// 1) Styles (dark UI)
// -------------------------------
const style = document.createElement("style");
style.textContent = `
  .missinfo-wrapper {
    cursor: pointer;
    margin-left: 8px;
    display: inline-flex;
    align-items: center;
    transition: transform 0.2s ease, opacity 0.2s ease;
    opacity: 0.6;
    position: relative;
    z-index: 10;
  }
  .missinfo-wrapper:hover {
    transform: scale(1.15);
    opacity: 1;
  }

  #missinfo-popup {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI';
    position: fixed;
    z-index: 2147483647;
    background: #1e1e1e;
    width: 320px;
    padding: 0;
    border-radius: 12px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    display: none;
    font-size: 14px;
    color: #e0e0e0;
    max-height: 80vh;
    overflow-y: auto;
  }

  .missinfo-header {
    background: #2b2b2b;
    padding: 14px 18px;
    border-bottom: 1px solid #333;
    border-radius: 12px 12px 0 0;
    display: flex;
    justify-content: space-between;
    font-weight: 600;
    position: sticky;
    top: 0;
    z-index: 10;
    cursor: move;
    user-select: none;
  }

  .missinfo-header:active {
    cursor: grabbing;
  }

  .missinfo-body {
    padding: 18px;
  }

  .missinfo-close {
    cursor: pointer;
    font-size: 20px;
    color: #aaa;
  }
  .missinfo-close:hover { color: #fff; }

  .missinfo-spinner {
    border: 3px solid #333;
    border-top: 3px solid #4a9eff;
    border-radius: 50%;
    width: 26px;
    height: 26px;
    animation: spin 1s linear infinite;
    margin: 16px auto;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* Progress Bar Styles */
  .progress-container {
    margin: 16px 0;
  }

  .progress-bar-bg {
    width: 100%;
    height: 8px;
    background: #333;
    border-radius: 10px;
    overflow: hidden;
    position: relative;
  }

  .progress-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #4a9eff, #6bb6ff);
    border-radius: 10px;
    transition: width 0.3s ease;
    width: 0%;
  }

  .progress-status {
    margin-top: 8px;
    font-size: 12px;
    color: #aaa;
    text-align: center;
  }

  .truth-score-badge {
    display: inline-block;
    background: #4a9eff;
    padding: 5px 13px;
    border-radius: 20px;
    font-weight: 600;
    margin-bottom: 12px;
  }

  /* URL Chiplet Styles */
  .url-chiplet {
    display: inline-flex;
    align-items: center;
    background: #2b2b2b;
    border: 1px solid #4a9eff;
    color: #4a9eff;
    padding: 4px 10px;
    border-radius: 16px;
    text-decoration: none;
    font-size: 12px;
    margin: 2px 4px 2px 0;
    transition: all 0.2s ease;
    max-width: 250px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  .url-chiplet:hover {
    background: #4a9eff;
    color: white;
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(74, 158, 255, 0.3);
  }
  
  .url-chiplet::before {
    content: "🔗";
    margin-right: 4px;
    font-size: 10px;
  }

  /* URL Container and Expand Button */
  .url-container {
    margin: 8px 0;
  }

  .url-list {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-bottom: 8px;
  }

  .url-list.collapsed .url-chiplet:nth-child(n+5) {
    display: none;
  }

  .expand-urls-btn {
    background: #2b2b2b;
    border: 1px solid #4a9eff;
    color: #4a9eff;
    padding: 6px 12px;
    border-radius: 16px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-weight: 500;
  }

  .expand-urls-btn:hover {
    background: #4a9eff;
    color: white;
  }

  .expand-urls-btn::after {
    content: "▼";
    font-size: 10px;
    transition: transform 0.2s ease;
  }

  .expand-urls-btn.expanded::after {
    transform: rotate(180deg);
  }

  /* Floating Verify button */
  #verify-btn {
    position: fixed;
    z-index: 2147483647;
    background: #4a9eff;
    color: white;
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(0,0,0,0.25);
    opacity: 0.95;
  }
`;
document.head.appendChild(style);

// -------------------------------
// 2) Icon SVG
// -------------------------------
const ICON_SVG = `
<svg width="20" height="20" viewBox="0 0 24 24" fill="none">
<circle cx="12" cy="12" r="11" fill="#2d5a7b" opacity="0.9"/>
<path d="M12 2C6.48 2 2 6.48 2 12C2 
17.52 6.48 22 12 22C17.52 22 22 17.52 
22 12C22 6.48 17.52 2 12 2ZM13 17H11V15H13V17ZM13 13H11V7H13V13Z" fill="#4a9eff"/>
</svg>`;

// -------------------------------
// 3) Popup element
// -------------------------------
const popup = document.createElement("div");
popup.id = "missinfo-popup";
document.body.appendChild(popup);

// Variables for dragging
let isDragging = false;
let currentX;
let currentY;
let initialX;
let initialY;
let xOffset = 0;
let yOffset = 0;

// Flag to prevent popup from closing during verify button click
let isVerifyButtonClicked = false;

// Listen for progress updates from background script
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "PROGRESS_UPDATE") {
    updateProgress(msg.progress, msg.status);
  }
});

// Function to update progress bar
function updateProgress(progress, status) {
  const progressFill = document.querySelector('.progress-bar-fill');
  const progressStatus = document.querySelector('.progress-status');
  
  if (progressFill) {
    progressFill.style.width = `${progress}%`;
  }
  
  if (progressStatus) {
    progressStatus.textContent = status;
  }
}

// Dragging functions
function dragStart(e) {
  const header = e.target.closest('.missinfo-header');
  if (!header) return;
  
  // Don't drag if clicking close button
  if (e.target.closest('.missinfo-close')) return;
  
  initialX = e.clientX - xOffset;
  initialY = e.clientY - yOffset;

  if (e.target === header || header.contains(e.target)) {
    isDragging = true;
  }
}

function drag(e) {
  if (isDragging) {
    e.preventDefault();
    
    currentX = e.clientX - initialX;
    currentY = e.clientY - initialY;

    xOffset = currentX;
    yOffset = currentY;

    setTranslate(currentX, currentY, popup);
  }
}

function dragEnd(e) {
  initialX = currentX;
  initialY = currentY;

  isDragging = false;
}

function setTranslate(xPos, yPos, el) {
  el.style.transform = `translate(${xPos}px, ${yPos}px)`;
}

// Close popup when clicking outside
document.addEventListener("mousedown", (e) => {
  console.log("🔴 MOUSEDOWN FIRED", {
    target: e.target,
    popupVisible: popup.style.display === "block",
    isInPopup: popup.contains(e.target),
    isWrapper: e.target.closest(".missinfo-wrapper"),
    isVerifyBtn: e.target.closest("#verify-btn")
  });

  // Start dragging if clicking header
  if (popup.contains(e.target) && e.target.closest('.missinfo-header')) {
    dragStart(e);
    return;
  }

  if (popup.style.display === "block" &&
      !popup.contains(e.target) &&
      !e.target.closest(".missinfo-wrapper")) {
    console.log("🔴 CLOSING POPUP");
    popup.style.display = "none";
    // Reset transform when closing
    popup.style.transform = "translate(0px, 0px)";
    xOffset = 0;
    yOffset = 0;
  }
});

// Add drag event listeners
document.addEventListener("mousemove", drag);
document.addEventListener("mouseup", dragEnd);

// -------------------------------
// 4) Popup logic with URL conversion
// -------------------------------
function convertUrlsToChiplets(text) {
  // Regular expression to match URLs
  const urlRegex = /(https?:\/\/[^\s<]+[^\s<.,;:!?'")])/gi;
  
  // Extract all URLs first
  const urls = [];
  let match;
  const regex = new RegExp(urlRegex);
  while ((match = regex.exec(text)) !== null) {
    const cleanUrl = match[1].replace(/[.,;:!?'")\]]+$/, '');
    urls.push(cleanUrl);
  }
  
  // If there are more than 4 URLs, create a collapsible container
  if (urls.length > 4) {
    const chiplets = urls.map(url => {
      let displayText = url;
      try {
        const urlObj = new URL(url);
        displayText = urlObj.hostname.replace('www.', '');
      } catch (e) {
        // If URL parsing fails, use the cleaned URL
      }
      return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="url-chiplet" title="${url}">${displayText}</a>`;
    }).join('');
    
    // Replace all URLs in the text with a placeholder
    let textWithoutUrls = text.replace(urlRegex, '');
    
    // Create container with expand button
    const urlSection = `
      <div class="url-container">
        <div class="url-list collapsed" id="url-list-${Date.now()}">
          ${chiplets}
        </div>
        <button class="expand-urls-btn" onclick="this.classList.toggle('expanded'); this.previousElementSibling.classList.toggle('collapsed'); this.innerHTML = this.classList.contains('expanded') ? 'Show Less' : 'Show More (' + ${urls.length - 4} + ')'">
          Show More (${urls.length - 4})
        </button>
      </div>
    `;
    
    return textWithoutUrls + urlSection;
  } else {
    // Less than 4 URLs, just convert them inline
    return text.replace(urlRegex, (url) => {
      const cleanUrl = url.replace(/[.,;:!?'")\]]+$/, '');
      
      let displayText = cleanUrl;
      try {
        const urlObj = new URL(cleanUrl);
        displayText = urlObj.hostname.replace('www.', '');
      } catch (e) {
        // If URL parsing fails, use the cleaned URL
      }
      
      return `<a href="${cleanUrl}" target="_blank" rel="noopener noreferrer" class="url-chiplet" title="${cleanUrl}">${displayText}</a>`;
    });
  }
}

function showPopup(rect, title, contentHtml) {
  console.log("📦 showPopup called", { rect, title });
  
  // Reset transform when showing new popup
  popup.style.transform = "translate(0px, 0px)";
  xOffset = 0;
  yOffset = 0;
  
  // Convert URLs to chiplets in the content
  const processedContent = convertUrlsToChiplets(contentHtml);
  
  popup.innerHTML = `
    <div class="missinfo-header">
      <span>${title}</span>
      <span class="missinfo-close" id="missinfo-close-btn">&times;</span>
    </div>
    <div class="missinfo-body">${processedContent}</div>
  `;

  document.getElementById("missinfo-close-btn").onclick = () => {
    popup.style.display = "none";
    popup.style.transform = "translate(0px, 0px)";
    xOffset = 0;
    yOffset = 0;
  };

  popup.style.display = "block";
  console.log("📦 Popup display set to block");

  // Position popup near the element (using fixed positioning)
  // Determine if there's enough space below, otherwise show above
  const viewportHeight = window.innerHeight;
  const popupHeight = 400; // estimated max height
  const spaceBelow = viewportHeight - rect.bottom;
  const spaceAbove = rect.top;
  
  let top, left;
  
  if (spaceBelow >= 300 || spaceBelow > spaceAbove) {
    // Show below
    top = rect.bottom + 10;
  } else {
    // Show above
    top = rect.top - popupHeight - 10;
  }
  
  // Adjust horizontal position to keep popup in viewport
  left = Math.max(10, Math.min(rect.left, window.innerWidth - 340));
  
  popup.style.top = `${top}px`;
  popup.style.left = `${left}px`;
  
  console.log("📦 Popup positioned at:", {
    top: popup.style.top,
    left: popup.style.left
  });
}

// -------------------------------
// 5) X.com Tweet Handler
// -------------------------------
function handleXPost(tweetDiv) {
  if (tweetDiv.dataset.missinfoXAttached) return;

  const textNode = tweetDiv.querySelector('[data-testid="tweetText"]');
  if (!textNode) return;

  const text = textNode.innerText.trim();
  if (text.length < 10) return;

  const wrapper = document.createElement("span");
  wrapper.className = "missinfo-wrapper";
  wrapper.innerHTML = ICON_SVG;
  wrapper.title = "Check misinformation";
  textNode.appendChild(wrapper);

  wrapper.onclick = () => {
    const rect = wrapper.getBoundingClientRect();

    showPopup(rect, "Analyzing", `
      <div class="missinfo-spinner"></div>
      <div class="progress-container">
        <div class="progress-bar-bg">
          <div class="progress-bar-fill"></div>
        </div>
        <div class="progress-status">Starting analysis...</div>
      </div>
    `);

    chrome.runtime.sendMessage(
      { type: "CHECK_TEXT", payload: text },
      (res) => {
        if (!res || res.error) {
          showPopup(rect, "Error",
            `<span class="missinfo-error">${res?.error || "Unknown error"}</span>`
          );
          return;
        }

        let formatted = res.result.replace(/\*\*(.*?)\*\*/g, "<b>$1</b>");

        if (res.truthScore) {
          formatted = `
            <div class="truth-score-badge">Truth Score: ${res.truthScore}/10</div>
            ${formatted}
          `;
        }

        showPopup(rect, "Analysis Result", formatted);
      }
    );
  };

  tweetDiv.dataset.missinfoXAttached = "true";
}

// -------------------------------
// 6) MutationObserver — X.com ONLY
// -------------------------------
if (location.hostname.includes("x.com")) {
  const observer = new MutationObserver((mut) => {
    mut.forEach(m => {
      m.addedNodes.forEach(node => {
        if (node.nodeType !== 1) return;

        if (node.matches?.('[data-testid="cellInnerDiv"]'))
          handleXPost(node);

        if (node.querySelectorAll)
          node.querySelectorAll('[data-testid="cellInnerDiv"]').forEach(handleXPost);
      });
    });
  });

  observer.observe(document.body, { childList: true, subtree: true });

  setTimeout(() => {
    document.querySelectorAll('[data-testid="cellInnerDiv"]').forEach(handleXPost);
  }, 500);
}

// ======================================================
// 7) HIGHLIGHT → "VERIFY?" BUTTON → FACT CHECK POPUP
// ======================================================

let verifyBtn = null;

function showVerifyButton(rect, text) {
  console.log("🔵 showVerifyButton called", { rect, text });
  
  if (verifyBtn) verifyBtn.remove();

  verifyBtn = document.createElement("div");
  verifyBtn.id = "verify-btn";
  verifyBtn.innerText = "Verify?";
  document.body.appendChild(verifyBtn);
  
  console.log("🔵 Verify button created and appended");

  // Position button above the selection using fixed positioning
  const top = rect.top - 40;
  const left = rect.left;

  verifyBtn.style.left = `${left}px`;
  verifyBtn.style.top = `${top}px`;
  
  console.log("🔵 Verify button positioned at:", {
    left: verifyBtn.style.left,
    top: verifyBtn.style.top
  });

  // CLICK → SHOW POPUP IMMEDIATELY + send request
  verifyBtn.onmousedown = (e) => {
    console.log("🟢 VERIFY BUTTON CLICKED");
    
    // Prevent the document mousedown listener from firing
    e.stopPropagation();
    
    console.log("🟢 Propagation stopped");
    
    const btnRect = verifyBtn.getBoundingClientRect();

    console.log("🟢 Button rect:", btnRect);

    // Remove verify button
    verifyBtn.remove();
    verifyBtn = null;
    
    console.log("🟢 Button removed");

    // Popup will appear near the highlighted text
    const popupRect = {
      top: btnRect.top + 30,
      bottom: btnRect.bottom + 30,
      left: btnRect.left
    };

    console.log("🟢 Showing popup at:", popupRect);

    // Instant popup
    showPopup(popupRect, "Fact Checking", `
      <div class="missinfo-spinner"></div>
      <div class="progress-container">
        <div class="progress-bar-bg">
          <div class="progress-bar-fill"></div>
        </div>
        <div class="progress-status">Starting analysis...</div>
      </div>
    `);
    
    console.log("🟢 Popup display:", popup.style.display);

    // Send text to background
    chrome.runtime.sendMessage(
      { type: "CHECK_TEXT", payload: text },
      (res) => {
        console.log("🟢 Response received:", res);
        
        if (!res || res.error) {
          showPopup(popupRect, "Error",
            `<span class="missinfo-error">${res?.error || "Unknown error"}</span>`
          );
          return;
        }

        let formatted = res.result.replace(/\*\*(.*?)\*\*/g, "<b>$1</b>");

        if (res.truthScore) {
          formatted = `
            <div class="truth-score-badge">Truth Score: ${res.truthScore}/10</div>
            ${formatted}
          `;
        }

        showPopup(popupRect, "Analysis Result", formatted);
      }
    );
  };
}

// Trigger verify button on selection
document.addEventListener("mouseup", () => {
  const sel = window.getSelection();
  if (!sel) return;

  const text = sel.toString().trim();
  if (!text || text.length < 10) {
    if (verifyBtn) verifyBtn.remove();
    verifyBtn = null;
    return;
  }

  const range = sel.getRangeAt(0);
  const rect = range.getBoundingClientRect();
  if (!rect || rect.width === 0) return;

  showVerifyButton(rect, text);
});