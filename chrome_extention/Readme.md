

# **TrueTraceAI Chrome Extention – Real-Time Web Content Verification**

TrueTraceAI is a browser extension that adds smart, contextual verification tools directly into the websites you browse.
It enhances online reading by offering **on-the-spot credibility checks** for Tweets, selected text, and highlighted content across the web.

---

## **Core Features**

### **1. Tweet Verification on X.com**

TrueTraceAI automatically detects posts on **X.com** and adds a subtle inline verification icon.
Clicking the icon opens a modern, draggable popup showing:

* A step-by-step analysis
* A progress indicator
* A truth-score badge (0–10)
* Cleanly formatted insights
* Extracted URLs shown as collapsible “chiplets”

---

### **2. Highlight → Verify**

When you highlight any text on any website, a floating **“Verify?”** button appears near your selection.

Click it to instantly open a verification popup containing:

* A progress spinner
* A dynamic progress bar
* A breakdown of claims, explanations, and references
* Visual truth-score indicators

This works on *all* websites, not just social platforms.

---

### **3. Beautiful Dark Floating UI**

The extension includes:

* A fully custom dark-mode popup
* Draggable header
* Smooth hover states
* Inline URL chips
* Collapsible long-URL sections
* Clean typography
* Animated loading spinner
* Rounded, modern surfaces and shadows

The UI is injected cleanly into the page using safe content-script styles.

---

### **4. Real-Time Progress Updates**

The extension listens for background-script progress updates and updates:

* The progress bar
* The progress status message
* The overall state of the popup

This gives a responsive, task-loading feel while the analysis is running.

---

### **5. X.com-Specific Enhancements**

TrueTraceAI includes special logic for X.com:

* Detects tweet containers
* Extracts visible text only
* Adds inline SVG icon
* Ensures clean re-injection as you scroll
* Uses a MutationObserver for infinite loading feeds

---

### **6. Smart Text Processing**

Before results are displayed, content is cleaned and enhanced:

* Markdown `**bold**` → converted to `<b>`
* URLs → converted into interactive chiplets
* Extra-long reference lists → collapsed into “Show More” sections
* Error messages rendered cleanly and safely

---

## **Project Structure**

```
TrueTraceAI/
│── manifest.json       # Browser extension config
│── content.js          # UI injection, tweet handler, highlight handler
│── background.js       # Fetching, analysis, progress streaming
│── config.js           # Local key/config (ignored in repo)
│── icon.png            # Toolbar/badge icon
│── README.md
```

---

## **Installation (Local Build)**

1. Download or clone the project
2. Open **chrome://extensions**
3. Enable **Developer Mode**
4. Click **Load Unpacked**
5. Select the project folder

TrueTraceAI will immediately begin working on supported sites.

---

## **How It Works (Overview)**

* Runs as a **Manifest V3** extension
* Listens for user actions (Tweet click, text highlight)
* Sends the selected content to a background process
* Streams progress updates back to the UI
* Renders a floating, draggable popup overlay with results
* Watches pages for dynamic elements via MutationObserver

---

## **Roadmap**

Planned improvements:

* Adaptive trust scoring
* History of recent checks
* Multi-source cross-referencing
* Mobile browser support
* Settings panel (sensitivity, themes, disable per-site)

---

# **License**

All rights are owned by Power Buff Gurls.
This project is not open-source and may not be redistributed, modified, or used commercially without explicit permission.