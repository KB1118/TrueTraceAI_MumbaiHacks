// // content.js - Full merged script
// // - Special X.com handler (exclusive on x.com)
// // - Generic site scanner (used on all other sites)
// // - Popup + styles + icon + message flow (compatible with your background script)

// // -------------------------------
// // 1) Styles (dark UI) - same as your original
// // -------------------------------
// const style = document.createElement('style');
// style.textContent = `
//   .missinfo-wrapper {
//     cursor: pointer;
//     margin-left: 8px;
//     vertical-align: middle;
//     display: inline-flex;
//     align-items: center;
//     transition: transform 0.2s ease, opacity 0.2s ease;
//     opacity: 0.6;
//     position: relative;
//     z-index: 10;
//   }
//   .missinfo-wrapper:hover {
//     transform: scale(1.15);
//     opacity: 1;
//   }

//   #missinfo-popup {
//     font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
//     position: absolute;
//     z-index: 2147483647;
//     background: #1e1e1e;
//     width: 320px;
//     padding: 0;
//     border-radius: 12px;
//     box-shadow: 0 10px 40px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.1);
//     display: none;
//     font-size: 14px;
//     line-height: 1.6;
//     color: #e0e0e0;
//     animation: missinfo-fadein 0.25s ease-out;
//     text-align: left;
//   }

//   @keyframes missinfo-fadein {
//     from { opacity: 0; transform: translateY(8px); }
//     to { opacity: 1; transform: translateY(0); }
//   }

//   .missinfo-header {
//     background: linear-gradient(135deg, #2d2d2d 0%, #252525 100%);
//     padding: 14px 18px;
//     border-bottom: 1px solid #333;
//     border-radius: 12px 12px 0 0;
//     font-weight: 600;
//     color: #fff;
//     display: flex;
//     justify-content: space-between;
//     align-items: center;
//     font-size: 15px;
//   }

//   .missinfo-body {
//     padding: 18px;
//     background: #1e1e1e;
//     border-radius: 0 0 12px 12px;
//   }

//   .missinfo-close {
//     cursor: pointer;
//     color: #888;
//     font-size: 20px;
//     line-height: 1;
//     padding: 0 4px;
//     transition: color 0.2s ease;
//     user-select: none;
//   }
//   .missinfo-close:hover { color: #fff; }

//   .missinfo-spinner {
//     border: 3px solid #333;
//     border-top: 3px solid #4a9eff;
//     border-radius: 50%;
//     width: 24px;
//     height: 24px;
//     animation: missinfo-spin 1s linear infinite;
//     margin: 12px auto;
//   }
//   @keyframes missinfo-spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

//   .truth-score-badge {
//     display: inline-block;
//     background: linear-gradient(135deg, #4a9eff 0%, #357abd 100%);
//     color: white;
//     padding: 4px 12px;
//     border-radius: 20px;
//     font-weight: 600;
//     font-size: 13px;
//     margin-bottom: 12px;
//     box-shadow: 0 2px 8px rgba(74, 158, 255, 0.3);
//   }

//   .missinfo-body b { color: #4a9eff; }
//   .missinfo-error { color: #ff6b6b; }
//   .missinfo-analyzing { text-align: center; color: #999; margin-top: 8px; }
// `;
// document.head.appendChild(style);

// // -------------------------------
// // 2) SVG Icon - same as your ICON_SVG
// // -------------------------------
// const ICON_SVG = `
// <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
// <circle cx="12" cy="12" r="11" fill="#2d5a7b" opacity="0.9"/>
// <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM13 17H11V15H13V17ZM13 13H11V7H13V13Z" fill="#4a9eff"/>
// </svg>
// `;

// // -------------------------------
// // 3) Popup element + outside click close
// // -------------------------------
// const popup = document.createElement("div");
// popup.id = "missinfo-popup";
// document.body.appendChild(popup);

// document.addEventListener("mousedown", (e) => {
//   if (popup.style.display === 'block' && !popup.contains(e.target) && !e.target.closest('.missinfo-wrapper')) {
//     popup.style.display = 'none';
//   }
// });

// // -------------------------------
// // 4) Helper utility functions (same logic)
// // -------------------------------
// function countWords(text) {
//   return text.trim().split(/\s+/).filter(w => w.length > 0).length;
// }

// function hasTextFormatting(element) {
//   const formattingTags = ['strong', 'b', 'em', 'i', 'u', 'mark', 'span', 'a'];
//   for (let tag of formattingTags) {
//     if (element.querySelector(tag)) return true;
//   }
//   return false;
// }

// function shouldAttachIcon(element, text) {
//   const tagName = element.tagName.toLowerCase();
//   const wordCount = countWords(text || '');
//   const charCount = (text || '').length;

//   if (tagName === 'p') {
//     return charCount >= 10;
//   }
//   if (tagName === 'div') {
//     if (hasTextFormatting(element)) return charCount >= 20;
//     return charCount >= 20 || wordCount >= 10;
//   }
//   if (wordCount >= 20) return true;
//   if (charCount < 10) return false;
//   if (wordCount <= 4) return false;
//   return true;
// }

// function showPopup(rect, title, contentHtml) {
//   popup.innerHTML = `
//     <div class="missinfo-header">
//       <span>${title}</span>
//       <span class="missinfo-close" id="missinfo-close-btn">&times;</span>
//     </div>
//     <div class="missinfo-body">${contentHtml}</div>
//   `;

//   const closeBtn = document.getElementById('missinfo-close-btn');
//   if (closeBtn) {
//     closeBtn.onclick = (ev) => {
//       ev.stopPropagation();
//       popup.style.display = 'none';
//     };
//   }

//   popup.style.display = 'block';
//   const scrollY = window.scrollY || window.pageYOffset;
//   const scrollX = window.scrollX || window.pageXOffset;
//   let top = rect.bottom + scrollY + 10;
//   let left = rect.left + scrollX;

//   // Prevent overflow right
//   const popupWidth = 320;
//   if (left + popupWidth > document.body.clientWidth) {
//     left = Math.max(8, document.body.clientWidth - popupWidth - 10);
//   }

//   // If popup would be off-screen bottom, show above
//   const viewportBottom = window.innerHeight + scrollY;
//   const estimatedPopupHeight = 220;
//   if (top + estimatedPopupHeight > viewportBottom) {
//     top = rect.top + scrollY - estimatedPopupHeight - 10;
//     if (top < 8) top = 8;
//   }

//   popup.style.top = `${top}px`;
//   popup.style.left = `${left}px`;
// }

// // -------------------------------
// // 5) Generic "attachIcon" for p/div and other sites
// // -------------------------------
// function attachIcon(element) {
//   try {
//     if (!element || element.nodeType !== 1) return;
//     if (element.dataset.missinfoAttached) return;

//     // Don't attach inside our popup or to our icons
//     if (element.id === 'missinfo-popup' || element.closest('#missinfo-popup') || element.closest('.missinfo-wrapper')) {
//       return;
//     }

//     const skipTags = ['script','style','noscript','iframe','svg','canvas','img','video','audio','input','textarea','button','select','br','hr','code','pre','kbd','samp','var','nav','header','footer','aside','form','label','path','g','circle','rect','line','polygon'];
//     const tagName = element.tagName.toLowerCase();
//     if (skipTags.includes(tagName)) return;

//     // Already has our icon?
//     if (element.querySelector('.missinfo-wrapper')) {
//       element.dataset.missinfoAttached = "true";
//       return;
//     }

//     // Avoid attaching inside code-like blocks
//     if (element.closest('pre, code, nav, header, footer, aside')) return;

//     const text = (element.innerText || element.textContent || '').trim();
//     if (!text) return;

//     if (!shouldAttachIcon(element, text)) return;

//     element.dataset.missinfoAttached = "true";

//     const wrapper = document.createElement('span');
//     wrapper.className = 'missinfo-wrapper';
//     wrapper.innerHTML = ICON_SVG;
//     wrapper.title = "Check for misinformation";

//     // Place wrapper at end of the element content, but avoid breaking inline-blocks: append is okay.
//     element.appendChild(wrapper);

//     wrapper.addEventListener('click', (e) => {
//       e.preventDefault();
//       e.stopPropagation();

//       const rect = wrapper.getBoundingClientRect();
//       showPopup(rect, "Fact Checking", '<div class="missinfo-spinner"></div><div class="missinfo-analyzing">Analyzing content...</div>');

//       // Use the same message format as your background expects
//       try {
//         chrome.runtime.sendMessage({ type: "CHECK_TEXT", payload: text }, (response) => {
//           if (chrome.runtime.lastError) {
//             console.error("Runtime error:", chrome.runtime.lastError);
//             showPopup(rect, "Error", `<span class="missinfo-error">Extension disconnected. Please refresh.</span>`);
//             return;
//           }

//           if (!response) {
//             showPopup(rect, "Error", `<span class="missinfo-error">No response from background.</span>`);
//             return;
//           }

//           if (response.error) {
//             showPopup(rect, "Error", `<span class="missinfo-error">${response.error}</span>`);
//             return;
//           }

//           let formatted = (response.result || "").replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');

//           if (response.truthScore && response.truthScore !== "N/A") {
//             const scoreValue = parseInt(response.truthScore) || null;
//             let color = '#4a9eff';
//             if (scoreValue !== null) {
//               if (scoreValue >= 8) color = '#51cf66';
//               else if (scoreValue >= 6) color = '#ffd43b';
//               else if (scoreValue < 6) color = '#ff6b6b';
//             }
//             formatted = `<div class="truth-score-badge" style="background:${color}">Truth Score: ${response.truthScore}/10</div>` + formatted;
//           }

//           showPopup(rect, "Analysis Result", formatted || "<i>No analysis returned.</i>");
//         });
//       } catch (err) {
//         console.error("Send message failed:", err);
//         showPopup(rect, "Error", `<span class="missinfo-error">Failed to contact background script.</span>`);
//       }
//     });
//   } catch (err) {
//     console.error("attachIcon error:", err);
//   }
// }

// // -------------------------------
// // 6) X.com specialized handling (exclusive on x.com)
// // -------------------------------
// function handleXPost(tweetDiv) {
//   try {
//     if (!tweetDiv || tweetDiv.nodeType !== 1) return;
//     if (tweetDiv.dataset.missinfoXAttached) return;

//     // find tweet text container
//     const textNode = tweetDiv.querySelector('[data-testid="tweetText"]');
//     if (!textNode) return;

//     const text = (textNode.innerText || textNode.textContent || '').trim();
//     if (!text || text.length < 10) return;

//     // Avoid double injection
//     if (tweetDiv.querySelector('.missinfo-wrapper')) {
//       tweetDiv.dataset.missinfoXAttached = "true";
//       return;
//     }

//     // Create icon and append to the end of tweet text element (safe spot)
//     const wrapper = document.createElement("span");
//     wrapper.className = "missinfo-wrapper";
//     wrapper.innerHTML = ICON_SVG;
//     wrapper.title = "Check post for misinformation";

//     // Append wrapper in a stable place: tweet text element
//     textNode.appendChild(wrapper);

//     wrapper.addEventListener("click", (e) => {
//       e.preventDefault();
//       e.stopPropagation();

//       const rect = wrapper.getBoundingClientRect();
//       showPopup(rect, "Fact Checking", '<div class="missinfo-spinner"></div><div class="missinfo-analyzing">Analyzing post...</div>');

//       try {
//         chrome.runtime.sendMessage({ type: "CHECK_TEXT", payload: text }, (response) => {
//           if (chrome.runtime.lastError) {
//             console.error("Runtime error:", chrome.runtime.lastError);
//             showPopup(rect, "Error", `<span class="missinfo-error">Extension disconnected. Please refresh.</span>`);
//             return;
//           }

//           if (!response) {
//             showPopup(rect, "Error", `<span class="missinfo-error">No response from background.</span>`);
//             return;
//           }

//           if (response.error) {
//             showPopup(rect, "Error", `<span class="missinfo-error">${response.error}</span>`);
//             return;
//           }

//           let formatted = (response.result || "").replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');

//           if (response.truthScore && response.truthScore !== "N/A") {
//             const scoreValue = parseInt(response.truthScore) || null;
//             let color = '#4a9eff';
//             if (scoreValue !== null) {
//               if (scoreValue >= 8) color = '#51cf66';
//               else if (scoreValue >= 6) color = '#ffd43b';
//               else if (scoreValue < 6) color = '#ff6b6b';
//             }
//             formatted = `<div class="truth-score-badge" style="background:${color}">Truth Score: ${response.truthScore}/10</div>` + formatted;
//           }

//           showPopup(rect, "Analysis Result", formatted || "<i>No analysis returned.</i>");
//         });
//       } catch (err) {
//         console.error("Send message failed:", err);
//         showPopup(rect, "Error", `<span class="missinfo-error">Failed to contact background script.</span>`);
//       }
//     });

//     tweetDiv.dataset.missinfoXAttached = "true";
//   } catch (err) {
//     console.error("handleXPost error:", err);
//   }
// }

// // -------------------------------
// // 7) Initialization and MutationObserver
// //    - If on x.com, use X-only logic (and skip generic scanner)
// //    - Otherwise, use generic scanner
// // -------------------------------
// const isXdotCom = (() => {
//   try {
//     const host = window.location.hostname || "";
//     // covers x.com and www.x.com
//     return host.toLowerCase().includes('x.com');
//   } catch (e) {
//     return false;
//   }
// })();

// function initGenericScan() {
//   // initial scan for paragraphs and divs
//   const paragraphs = document.querySelectorAll('p');
//   const divs = document.querySelectorAll('div');

//   console.log(`Miss Info Checker: Scanning ${paragraphs.length} <p> tags and ${divs.length} <div> tags...`);

//   let attached = 0;
//   paragraphs.forEach(p => { attachIcon(p); if (p.dataset.missinfoAttached) attached++; });
//   divs.forEach(d => { attachIcon(d); if (d.dataset.missinfoAttached) attached++; });

//   console.log(`Miss Info Checker: Attached ${attached} icons (generic).`);
// }

// function initXScan() {
//   // initial scan for tweet containers
//   const tweets = document.querySelectorAll('[data-testid="cellInnerDiv"]');
//   tweets.forEach(handleXPost);
//   console.log(`Miss Info Checker: Found ${tweets.length} X tweet containers (initial).`);
// }

// // MutationObserver logic: branching based on site
// const observer = new MutationObserver((mutations) => {
//   mutations.forEach((mutation) => {
//     mutation.addedNodes.forEach((node) => {
//       if (node.nodeType !== 1) return; // skip non-elements

//       if (isXdotCom) {
//         // X-specific: check node and its descendants for tweet containers
//         if (node.matches && node.matches('[data-testid="cellInnerDiv"]')) {
//           handleXPost(node);
//         }
//         if (node.querySelectorAll) {
//           node.querySelectorAll('[data-testid="cellInnerDiv"]').forEach(handleXPost);
//         }
//       } else {
//         // Generic: only process p and div (your original intention)
//         const tagName = (node.tagName || '').toLowerCase();
//         if (tagName === 'p' || tagName === 'div') {
//           attachIcon(node);
//         }
//         if (node.querySelectorAll) {
//           node.querySelectorAll('p, div').forEach(attachIcon);
//         }
//       }
//     });
//   });
// });

// // Start observing the body for dynamic changes (both modes)
// observer.observe(document.body, { childList: true, subtree: true });

// // Run appropriate init after a short delay (gives client-side frameworks time)
// setTimeout(() => {
//   if (isXdotCom) initXScan();
//   else initGenericScan();
// }, 800);

// // Also run a periodic scan (infrequent) to catch nodes missed due to strange lifecycle
// const periodicInterval = isXdotCom ? 2000 : 5000;
// const periodicHandle = setInterval(() => {
//   if (isXdotCom) {
//     document.querySelectorAll('[data-testid="cellInnerDiv"]').forEach(handleXPost);
//   } else {
//     document.querySelectorAll('p, div').forEach(attachIcon);
//   }
// }, periodicInterval);

// // ===============================
// // Highlight-to-Check Feature
// // ===============================

// document.addEventListener("mouseup", () => {
//     const selection = window.getSelection();
//     if (!selection) return;

//     const text = selection.toString().trim();
//     if (!text || text.length < 10) return; // require meaningful text

//     const range = selection.getRangeAt(0);
//     const rect = range.getBoundingClientRect();

//     if (!rect || rect.width === 0 || rect.height === 0) return;

//     // Show popup above selection
//     const popupRect = {
//         top: rect.top - 50,       // move popup above highlight
//         left: rect.left,
//         bottom: rect.top - 10     // fallback used by your showPopup()
//     };

//     showPopup(popupRect, "Fact Checking", `
//         <div class="missinfo-spinner"></div>
//         <div class="missinfo-analyzing">Analyzing highlighted text...</div>
//     `);

//     chrome.runtime.sendMessage(
//         { type: "CHECK_TEXT", payload: text },
//         (response) => {
//             if (!response || response.error) {
//                 showPopup(popupRect, "Error",
//                     `<span class="missinfo-error">${response?.error || "Unknown error"}</span>`
//                 );
//                 return;
//             }

//             let formatted = response.result.replace(/\*\*(.*?)\*\*/g, "<b>$1</b>");

//             if (response.truthScore && response.truthScore !== "N/A") {
//                 const scoreValue = parseInt(response.truthScore);
//                 let color = '#4a9eff';
//                 if (scoreValue >= 8) color = '#51cf66';
//                 else if (scoreValue >= 6) color = '#ffd43b';
//                 else color = '#ff6b6b';

//                 formatted = `
//                     <div class="truth-score-badge" style="background:${color}">
//                         Truth Score: ${response.truthScore}/10
//                     </div>
//                     ${formatted}
//                 `;
//             }

//             showPopup(popupRect, "Analysis Result", formatted);
//         }
//     );
// });


// // Bonus: clean up if the page unloads (prevents dangling timers)
// window.addEventListener('beforeunload', () => {
//   clearInterval(periodicHandle);
//   observer.disconnect();
// }

// );
