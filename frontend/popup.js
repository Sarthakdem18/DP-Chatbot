const API_URL = "http://localhost:8000/query";
let currentLanguage = "en";

// UI Text Translation Database
const TRANSLATIONS = {
  en: {
    title: "Delhi Police Assistant",
    motto: "शान्ति • सेवा • न्याय",
    quickServices: "Quick Services",
    placeholder: "Describe your issue (e.g. I lost my phone)...",
    welcome: "Select a quick service above or type your query below to get instant guidance and service links.",
    badge: "Assistant Response",
    noMatches: "No matching services found. Please try a different query.",
    searching: "Searching the catalog...",
    openService: "Open Service →",
    loginRequired: "🔑 Login Required",
    directAccess: "✅ Direct Access",
    toggleText: "हिन्दी",
    quickLabels: {
      lost: "Lost Report",
      mv: "MV Theft e-FIR",
      theft: "Theft e-FIR",
      pcc: "PCC",
      cvr: "CVR"
    }
  },
  hi: {
    title: "दिल्ली पुलिस सहायक",
    motto: "शान्ति • सेवा • न्याय",
    quickServices: "त्वरित सेवाएँ",
    placeholder: "अपनी समस्या बताएं (जैसे: मेरा फोन खो गया)...",
    welcome: "त्वरित सेवा लिंक और मार्गदर्शन के लिए ऊपर दी गई सेवाओं पर क्लिक करें या नीचे अपना प्रश्न लिखें।",
    badge: "सहायक का उत्तर",
    noMatches: "आपकी खोज से मेल खाती कोई सेवा नहीं मिली। कृपया पुनः प्रयास करें।",
    searching: "खोज की जा रही है...",
    openService: "सेवा खोलें →",
    loginRequired: "🔑 लॉगिन आवश्यक",
    directAccess: "✅ सीधी पहुँच",
    toggleText: "English",
    quickLabels: {
      lost: "खोया रिपोर्ट",
      mv: "वाहन चोरी ई-FIR",
      theft: "चोरी ई-FIR",
      pcc: "PCC (पुलिस सत्यापन)",
      cvr: "CVR (चरित्र सत्यापन)"
    }
  }
};

// Initialize Chrome Extension
document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
});

// Setup event listeners securely, avoiding inline event handlers (CSP requirement)
function setupEventListeners() {
  // Screen 1: Language Selection Buttons
  const btnEn = document.getElementById("btn-lang-en");
  const btnHi = document.getElementById("btn-lang-hi");
  
  if (btnEn) btnEn.addEventListener("click", () => enterApp("en"));
  if (btnHi) btnHi.addEventListener("click", () => enterApp("hi"));

  // Screen 2: Language Toggle in Header
  const btnToggle = document.getElementById("btn-toggle-lang");
  if (btnToggle) {
    btnToggle.addEventListener("click", () => {
      const targetLang = currentLanguage === "en" ? "hi" : "en";
      updateLanguageUI(targetLang);
    });
  }

  // Quick Action Buttons
  const quickBtns = document.querySelectorAll(".btn-quick");
  quickBtns.forEach(btn => {
    btn.addEventListener("click", (e) => {
      const query = e.currentTarget.getAttribute("data-query");
      // Pre-fill input box with selected service name for context
      const inputEl = document.getElementById("input-query");
      if (inputEl) {
        inputEl.value = e.currentTarget.textContent;
      }
      runSearch(query);
    });
  });

  // Main Search Input & Button
  const btnSearch = document.getElementById("btn-search");
  const inputQuery = document.getElementById("input-query");
  
  if (btnSearch) {
    btnSearch.addEventListener("click", () => {
      if (inputQuery) runSearch(inputQuery.value);
    });
  }
  
  if (inputQuery) {
    inputQuery.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        runSearch(inputQuery.value);
      }
    });
  }
}

// Enter the main assistant screen
function enterApp(lang) {
  updateLanguageUI(lang);
  
  document.getElementById("screen-lang").classList.remove("active");
  document.getElementById("screen-main").classList.add("active");
}

// Update UI Text elements to reflect language selection
function updateLanguageUI(lang) {
  currentLanguage = lang;
  const content = TRANSLATIONS[lang];

  // Header Title and Motto
  const h2 = document.querySelector(".header-title-group h2");
  if (h2) h2.textContent = content.title;

  // Language Toggle Button Text
  const toggleBtn = document.getElementById("btn-toggle-lang");
  if (toggleBtn) toggleBtn.textContent = content.toggleText;

  // Quick Services Title
  const qsTitle = document.getElementById("quick-services-title");
  if (qsTitle) qsTitle.textContent = content.quickServices;

  // Quick Buttons
  const btnLost = document.getElementById("btn-quick-lost");
  const btnMv = document.getElementById("btn-quick-mv");
  const btnTheft = document.getElementById("btn-quick-theft");
  const btnPcc = document.getElementById("btn-quick-pcc");
  const btnCvr = document.getElementById("btn-quick-cvr");

  if (btnLost) btnLost.textContent = content.quickLabels.lost;
  if (btnMv) btnMv.textContent = content.quickLabels.mv;
  if (btnTheft) btnTheft.textContent = content.quickLabels.theft;
  if (btnPcc) btnPcc.textContent = content.quickLabels.pcc;
  if (btnCvr) btnCvr.textContent = content.quickLabels.cvr;

  // Input Placeholder
  const inputEl = document.getElementById("input-query");
  if (inputEl) inputEl.placeholder = content.placeholder;

  // Welcome Instruction Text
  const welcomeText = document.getElementById("welcome-text");
  if (welcomeText) welcomeText.textContent = content.welcome;

  // Assistant Response Badge
  const badgeEl = document.getElementById("response-badge");
  if (badgeEl) badgeEl.textContent = content.badge;
  
  // Re-run search if there's already active content in input box to refresh translation results
  if (inputEl && inputEl.value.trim() !== "") {
    // We map quick labels text back to queries if they clicked one
    let query = inputEl.value.trim();
    if (query === TRANSLATIONS.en.quickLabels.lost || query === TRANSLATIONS.hi.quickLabels.lost) query = "lost report";
    else if (query === TRANSLATIONS.en.quickLabels.mv || query === TRANSLATIONS.hi.quickLabels.mv) query = "motor vehicle theft";
    else if (query === TRANSLATIONS.en.quickLabels.theft || query === TRANSLATIONS.hi.quickLabels.theft) query = "theft report";
    else if (query === TRANSLATIONS.en.quickLabels.pcc || query === TRANSLATIONS.hi.quickLabels.pcc) query = "police clearance";
    else if (query === TRANSLATIONS.en.quickLabels.cvr || query === TRANSLATIONS.hi.quickLabels.cvr) query = "character verification";
    
    runSearch(query);
  }
}

// Fetch matches from API and render response
async function runSearch(queryText) {
  if (!queryText || queryText.trim() === "") return;

  const responseContainer = document.getElementById("response-container");
  const welcomeInstruction = document.getElementById("welcome-instruction");
  const answerEl = document.getElementById("response-answer");
  const servicesList = document.getElementById("services-list");

  // Show response box with searching message
  welcomeInstruction.classList.add("hidden");
  responseContainer.classList.remove("hidden");
  
  answerEl.textContent = TRANSLATIONS[currentLanguage].searching;
  servicesList.innerHTML = "";

  // Add loading skeleton styling
  answerEl.classList.add("loading");

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        query: queryText,
        language: currentLanguage
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    // Stop loading state
    answerEl.classList.remove("loading");
    
    renderResults(data);
  } catch (error) {
    console.error("Fetch failed:", error);
    answerEl.classList.remove("loading");
    
    // Render offline/error alert
    answerEl.innerHTML = currentLanguage === "en" 
      ? `<div class="error-msg"><strong>Unable to connect to assistant backend.</strong><br>Please make sure the FastAPI server is running on localhost:8000 and try again.</div>`
      : `<div class="error-msg"><strong>असिस्टेंट सर्वर से कनेक्ट नहीं हो सका।</strong><br>कृपया सुनिश्चित करें कि FastAPI सर्वर localhost:8000 पर चल रहा है और पुनः प्रयास करें।</div>`;
  }
}

// Render the backend results to DOM
function renderResults(data) {
  const answerEl = document.getElementById("response-answer");
  const servicesList = document.getElementById("services-list");
  const content = TRANSLATIONS[currentLanguage];

  // Set the assistant's verbal reply
  answerEl.textContent = data.answer;

  // Clear services list
  servicesList.innerHTML = "";

  if (!data.services || data.services.length === 0) {
    const noMatch = document.createElement("div");
    noMatch.className = "no-matches";
    noMatch.textContent = content.noMatches;
    servicesList.appendChild(noMatch);
    return;
  }

  // Loop through recommended services and render cards
  data.services.forEach(service => {
    const card = document.createElement("div");
    card.className = "service-card";

    // Header section of card (Title + Badges)
    const cardHeader = document.createElement("div");
    cardHeader.className = "service-card-header";

    const title = document.createElement("h4");
    title.className = "service-title";
    title.textContent = service.name;
    cardHeader.appendChild(title);

    // Login requirement badge
    const badge = document.createElement("span");
    if (service.requires_login) {
      badge.className = "badge badge-warning";
      badge.textContent = content.loginRequired;
    } else {
      badge.className = "badge badge-success";
      badge.textContent = content.directAccess;
    }
    cardHeader.appendChild(badge);
    card.appendChild(cardHeader);

    // Description text
    const desc = document.createElement("p");
    desc.className = "service-desc";
    desc.textContent = service.description;
    card.appendChild(desc);

    // Action button
    const actionBtn = document.createElement("a");
    actionBtn.className = "btn btn-card-action";
    actionBtn.href = service.url;
    actionBtn.target = "_blank";
    actionBtn.textContent = content.openService;
    card.appendChild(actionBtn);

    servicesList.appendChild(card);
  });
}
