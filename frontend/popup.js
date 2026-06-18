const API_URL = "http://localhost:8000/query";
let currentLanguage = "en";

// ═══════════════════════════════
//  Guided Flow — PCC / CVR
// ═══════════════════════════════

const PORTAL_URL = "https://pcccvr.delhipolice.gov.in/";

const PCC_PURPOSES_INDIVIDUAL = [
  { id: "emigration",          label: "Emigration" },
  { id: "licensing",           label: "Licensing" },
  { id: "employment",          label: "Employment / Private Firm Employees" },
  { id: "directors",           label: "Directors / Board Members" },
  { id: "journalists",         label: "Journalists / PIB" },
  { id: "commercial_vehicles", label: "Commercial Vehicles / PSV Badges" },
  { id: "adoption",            label: "Adoption of Child" },
  { id: "agents",              label: "Agents (Post Office / Govt Services)" },
  { id: "psara",               label: "Security Agency Directors / Employees (PSARA)" },
  { id: "misc",                label: "Miscellaneous" },
];
const PCC_PURPOSES_ORG = PCC_PURPOSES_INDIVIDUAL.filter(p => p.id !== "adoption");

const PCC_DOCS = [
  "Applicant's Photo / Firm Logo — JPEG, JPG or PNG, under 20 KB",
  "Photo Identity Proof / Registration Certificate — PDF / JPEG / JPG / PNG, under 200 KB (PAN Card, Driving Licence, Election ID, or Aadhaar Card)",
  "Residential Address Proof — PDF / JPEG / JPG / PNG, under 200 KB (Aadhaar, Bank Passbook, Driving Licence, Election ID, Passport, Electricity Bill, Telephone Bill, Ration Card, or Rent Agreement)",
  "Forwarding Letter from Govt / PSU / Semi-Govt / Others — PDF / JPEG / JPG / PNG, under 200 KB",
];

const PCC_STEPS = [
  "Open the PCC & CVR portal",
  "Register: enter name, mobile, email, password and captcha",
  "Receive and enter the OTP",
  "Log in",
  "Click \"Apply New\"",
  "Select Individual or Organisation",
  "Select the PCC type and verification mode",
  "Fill your present address; add up to 5 previous Delhi addresses if applicable",
  "Fill criminal case details if any (up to 10 cases; multiple states allowed)",
  "Upload the 4 documents listed above",
  "Review the form preview and edit if needed",
  "Accept the two consent checkboxes",
  "Click \"Pay and Submit\" and complete payment",
  "You will receive a PCC number — application enters \"Under Verification\" status",
  "Download the certificate once it is approved",
];

const CVR_DOCS = [
  "Applicant's Photo — JPEG, JPG or PNG, under 20 KB",
  "10th Certificate or Marksheet — PDF / JPEG / JPG / PNG, under 200 KB",
  "Photo Identity Proof — PDF / JPEG / JPG / PNG, under 200 KB",
  "Residential Address Proof — PDF / JPEG / JPG / PNG, under 200 KB",
  "Forwarding Letter — PDF / JPEG / JPG / PNG, under 200 KB",
];

const CVR_STEPS = [
  "Open the PCC & CVR portal",
  "Register as \"Character Verification Report\": fill Organisation Name, Mobile, Email, Password and Captcha",
  "Receive and enter the OTP",
  "Log in",
  "Click \"Apply New\"",
  "Select Government Employee",
  "Verifier details (organisation name, address, contact) are auto-filled from registration — confirm them",
  "Fill applicant details",
  "Fill educational details",
  "Fill present address; add up to 5 previous Delhi addresses if applicable",
  "Fill criminal case details if any (up to 10 cases)",
  "Upload the 5 documents listed above",
  "Review the form preview",
  "Accept the two consent checkboxes",
  "Click \"Submit\"",
  "You will receive a CVR number — application enters \"Under Verification\" status",
  "The certificate becomes available for download once approved",
];

const FLOW_STEP_ORDER = {
  pcc: ["applicantType", "purpose", "verificationMode"],
  cvr: ["isGovtEmployee"],
};

let guidedFlow = null;

function startGuidedFlow(type) {
  guidedFlow = { type, selections: {} };
  const inputEl = document.getElementById("input-query");
  if (inputEl) inputEl.value = "";
  document.getElementById("welcome-instruction").classList.add("hidden");
  document.getElementById("response-container").classList.add("hidden");
  document.getElementById("guided-flow-container").classList.remove("hidden");
  renderGuidedFlow();
}

function advanceFlow(key, value) {
  guidedFlow.selections[key] = value;
  renderGuidedFlow();
}

function goBackToFlowStep(key) {
  const order = FLOW_STEP_ORDER[guidedFlow.type];
  const idx = order.indexOf(key);
  for (let i = idx; i < order.length; i++) delete guidedFlow.selections[order[i]];
  renderGuidedFlow();
}

function renderGuidedFlow() {
  const container = document.getElementById("guided-flow-container");
  container.innerHTML = "";
  const wrapper = document.createElement("div");
  wrapper.className = "flow-wrapper";
  container.appendChild(wrapper);
  if (guidedFlow.type === "pcc") renderPCCFlow(wrapper);
  else renderCVRFlow(wrapper);
}

function renderBreadcrumb(container, crumbs, flowLabel) {
  const bc = document.createElement("div");
  bc.className = "flow-breadcrumb";

  const tag = document.createElement("span");
  tag.className = "flow-crumb-type";
  tag.textContent = flowLabel;
  bc.appendChild(tag);

  crumbs.forEach(crumb => {
    const sep = document.createElement("span");
    sep.className = "flow-crumb-sep";
    sep.textContent = "›";
    bc.appendChild(sep);

    const chip = document.createElement("button");
    chip.className = "flow-crumb-btn";
    chip.textContent = crumb.label;
    chip.title = "Click to change";
    chip.addEventListener("click", () => goBackToFlowStep(crumb.key));
    bc.appendChild(chip);
  });

  container.appendChild(bc);
}

function renderQuestion(container, questionText, options, note) {
  if (note) {
    const noteEl = document.createElement("div");
    noteEl.className = "flow-note";
    noteEl.textContent = note;
    container.appendChild(noteEl);
  }

  const q = document.createElement("p");
  q.className = "flow-question";
  q.textContent = questionText;
  container.appendChild(q);

  const optWrap = document.createElement("div");
  optWrap.className = options.length <= 2 ? "flow-options flow-options-row" : "flow-options flow-options-col";

  options.forEach(opt => {
    const btn = document.createElement("button");
    btn.className = "flow-option-btn";
    btn.textContent = opt.label;
    btn.addEventListener("click", opt.action);
    optWrap.appendChild(btn);
  });

  container.appendChild(optWrap);
}

function renderFlowAnswer(container, title, docs, steps, note) {
  if (note) {
    const noteEl = document.createElement("div");
    noteEl.className = "flow-note";
    noteEl.textContent = note;
    container.appendChild(noteEl);
  }

  const titleEl = document.createElement("p");
  titleEl.className = "flow-answer-title";
  titleEl.textContent = title;
  container.appendChild(titleEl);

  const docLabel = document.createElement("p");
  docLabel.className = "flow-section-label";
  docLabel.textContent = "Documents Required";
  container.appendChild(docLabel);

  const docList = document.createElement("div");
  docs.forEach(doc => {
    const item = document.createElement("div");
    item.className = "flow-doc-item";
    item.textContent = doc;
    docList.appendChild(item);
  });
  container.appendChild(docList);

  const stepsLabel = document.createElement("p");
  stepsLabel.className = "flow-section-label";
  stepsLabel.textContent = "Step-by-Step Procedure";
  container.appendChild(stepsLabel);

  const stepsList = document.createElement("div");
  steps.forEach((step, i) => {
    const item = document.createElement("div");
    item.className = "flow-step-item";
    const num = document.createElement("span");
    num.className = "flow-step-num";
    num.textContent = i + 1;
    const text = document.createElement("span");
    text.textContent = step;
    item.appendChild(num);
    item.appendChild(text);
    stepsList.appendChild(item);
  });
  container.appendChild(stepsList);

  const portalBtn = document.createElement("a");
  portalBtn.className = "flow-portal-btn";
  portalBtn.href = PORTAL_URL;
  portalBtn.target = "_blank";
  portalBtn.rel = "noopener noreferrer";
  portalBtn.textContent = "Open PCC & CVR Portal →";
  container.appendChild(portalBtn);
}

function renderPCCFlow(container) {
  const { applicantType, purpose, verificationMode } = guidedFlow.selections;

  // Build breadcrumb from completed steps
  const crumbs = [];
  if (applicantType) {
    crumbs.push({ label: applicantType === "individual" ? "Individual" : "Organisation", key: "applicantType" });
  }
  if (purpose) {
    const list = applicantType === "individual" ? PCC_PURPOSES_INDIVIDUAL : PCC_PURPOSES_ORG;
    const found = list.find(p => p.id === purpose);
    if (found) crumbs.push({ label: found.label, key: "purpose" });
  }
  if (verificationMode) {
    crumbs.push({ label: verificationMode === "field" ? "Field Verification" : "No Field Visit", key: "verificationMode" });
  }
  if (crumbs.length) renderBreadcrumb(container, crumbs, "PCC");

  // Step 1 — applicant type
  if (!applicantType) {
    renderQuestion(container, "Are you applying as an Individual or an Organisation?", [
      { label: "Individual",    action: () => advanceFlow("applicantType", "individual") },
      { label: "Organisation",  action: () => advanceFlow("applicantType", "organisation") },
    ]);
    return;
  }

  // Step 2 — purpose
  if (!purpose) {
    const list = applicantType === "individual" ? PCC_PURPOSES_INDIVIDUAL : PCC_PURPOSES_ORG;
    renderQuestion(container, "What is the purpose of the PCC?",
      list.map(p => ({ label: p.label, action: () => advanceFlow("purpose", p.id) }))
    );
    return;
  }

  // Emigration forces field verification — auto-advance without asking
  if (!verificationMode && purpose === "emigration") {
    guidedFlow.selections.verificationMode = "field";
    renderGuidedFlow();
    return;
  }

  // Step 3 — verification mode
  if (!verificationMode) {
    renderQuestion(container, "Which verification mode do you need?", [
      { label: "Address + Antecedent Verification (Field Verification)", action: () => advanceFlow("verificationMode", "field") },
      { label: "Antecedents Verification Only (No Field Visit)",          action: () => advanceFlow("verificationMode", "nofield") },
    ]);
    return;
  }

  // Final answer
  const list = applicantType === "individual" ? PCC_PURPOSES_INDIVIDUAL : PCC_PURPOSES_ORG;
  const purposeLabel = list.find(p => p.id === purpose)?.label || purpose;
  const applicantLabel = applicantType === "individual" ? "Individual" : "Organisation";
  const verLabel = verificationMode === "field" ? "Address + Antecedent Verification" : "Antecedents Verification Only";
  const emigrationNote = purpose === "emigration"
    ? "ℹ️ Address + Antecedent Verification (Field Verification) is mandatory for Emigration applications."
    : null;

  renderFlowAnswer(
    container,
    `Since you're applying as an ${applicantLabel} for ${purposeLabel} with ${verLabel}, here's what you need:`,
    PCC_DOCS,
    PCC_STEPS,
    emigrationNote
  );
}

function renderCVRFlow(container) {
  const { isGovtEmployee } = guidedFlow.selections;

  const crumbs = [];
  if (isGovtEmployee !== undefined) {
    crumbs.push({ label: isGovtEmployee ? "Government Employee" : "Not Govt Employee", key: "isGovtEmployee" });
  }
  if (crumbs.length) renderBreadcrumb(container, crumbs, "CVR");

  // Step 1 — eligibility check
  if (isGovtEmployee === undefined) {
    renderQuestion(
      container,
      "Is this application being made by a Ministry or State Government, on behalf of a government employee?",
      [
        { label: "Yes", action: () => advanceFlow("isGovtEmployee", true) },
        { label: "No",  action: () => advanceFlow("isGovtEmployee", false) },
      ]
    );
    return;
  }

  // Not eligible
  if (!isGovtEmployee) {
    const msg = document.createElement("div");
    const q = document.createElement("p");
    q.className = "flow-question";
    q.textContent = "CVR is only available for government employees, applied for through their Ministry or State Government department.";
    msg.appendChild(q);
    const sub = document.createElement("p");
    sub.className = "flow-not-eligible-sub";
    sub.innerHTML = "For your situation, you likely need a <strong>Police Clearance Certificate (PCC)</strong> instead.";
    msg.appendChild(sub);
    container.appendChild(msg);

    const switchBtn = document.createElement("button");
    switchBtn.className = "flow-switch-btn";
    switchBtn.textContent = "Switch to PCC →";
    switchBtn.addEventListener("click", () => startGuidedFlow("pcc"));
    container.appendChild(switchBtn);
    return;
  }

  // Final answer
  renderFlowAnswer(
    container,
    "Your Ministry / State Government can apply for a Character Verification Report (CVR) on behalf of the government employee. Here's what's needed:",
    CVR_DOCS,
    CVR_STEPS,
    null
  );
}

const TRANSLATIONS = {
  en: {
    title: "Delhi Police Assistant",
    botLabel: "AI Chatbot",
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
    helplinesTitle: "Emergency Helplines",
    quickLabels: {
      lost:  "Lost Report",
      mv:    "MV Theft e-FIR",
      theft: "Theft e-FIR",
      pcc:   "PCC",
      cvr:   "CVR"
    }
  },
  hi: {
    title: "दिल्ली पुलिस सहायक",
    botLabel: "AI चैटबॉट",
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
    helplinesTitle: "आपातकालीन हेल्पलाइन",
    quickLabels: {
      lost:  "खोया रिपोर्ट",
      mv:    "वाहन चोरी ई-FIR",
      theft: "चोरी ई-FIR",
      pcc:   "PCC (पुलिस सत्यापन)",
      cvr:   "CVR (चरित्र सत्यापन)"
    }
  }
};

document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
});

function setupEventListeners() {
  const btnEn = document.getElementById("btn-lang-en");
  const btnHi = document.getElementById("btn-lang-hi");
  if (btnEn) btnEn.addEventListener("click", () => enterApp("en"));
  if (btnHi) btnHi.addEventListener("click", () => enterApp("hi"));

  const btnToggle = document.getElementById("btn-toggle-lang");
  if (btnToggle) {
    btnToggle.addEventListener("click", () => {
      updateLanguageUI(currentLanguage === "en" ? "hi" : "en");
    });
  }

  document.querySelectorAll(".btn-quick").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const query = e.currentTarget.getAttribute("data-query");
      if (query === "police clearance") { startGuidedFlow("pcc"); return; }
      if (query === "character verification") { startGuidedFlow("cvr"); return; }
      const inputEl = document.getElementById("input-query");
      if (inputEl) inputEl.value = e.currentTarget.textContent;
      runSearch(query);
    });
  });

  const btnSearch  = document.getElementById("btn-search");
  const inputQuery = document.getElementById("input-query");
  if (btnSearch)  btnSearch.addEventListener("click",  () => { if (inputQuery) runSearch(inputQuery.value); });
  if (inputQuery) inputQuery.addEventListener("keypress", (e) => { if (e.key === "Enter") runSearch(inputQuery.value); });

  const btnHelplines = document.getElementById("btn-helplines");
  if (btnHelplines) {
    btnHelplines.addEventListener("click", () => {
      const panel = document.getElementById("helplines-panel");
      const arrow = document.getElementById("hl-arrow");
      if (panel) panel.classList.toggle("hidden");
      if (arrow) arrow.classList.toggle("open");
    });
  }
}

function enterApp(lang) {
  updateLanguageUI(lang);
  document.getElementById("screen-lang").classList.remove("active");
  document.getElementById("screen-main").classList.add("active");
}

function updateLanguageUI(lang) {
  currentLanguage = lang;
  const t = TRANSLATIONS[lang];

  const titleEl = document.getElementById("header-title");
  if (titleEl) titleEl.textContent = t.title;

  const botLabelEl = document.getElementById("header-bot-label");
  if (botLabelEl) botLabelEl.textContent = t.botLabel;

  const toggleBtn = document.getElementById("btn-toggle-lang");
  if (toggleBtn) toggleBtn.textContent = t.toggleText;

  const qsTitle = document.getElementById("quick-services-title");
  if (qsTitle) qsTitle.textContent = t.quickServices;

  const btnLost  = document.getElementById("btn-quick-lost");
  const btnMv    = document.getElementById("btn-quick-mv");
  const btnTheft = document.getElementById("btn-quick-theft");
  const btnPcc   = document.getElementById("btn-quick-pcc");
  const btnCvr   = document.getElementById("btn-quick-cvr");
  if (btnLost)  btnLost.textContent  = t.quickLabels.lost;
  if (btnMv)    btnMv.textContent    = t.quickLabels.mv;
  if (btnTheft) btnTheft.textContent = t.quickLabels.theft;
  if (btnPcc)   btnPcc.textContent   = t.quickLabels.pcc;
  if (btnCvr)   btnCvr.textContent   = t.quickLabels.cvr;

  const inputEl = document.getElementById("input-query");
  if (inputEl) inputEl.placeholder = t.placeholder;

  const welcomeText = document.getElementById("welcome-text");
  if (welcomeText) welcomeText.textContent = t.welcome;

  const badgeEl = document.getElementById("response-badge");
  if (badgeEl) badgeEl.textContent = t.badge;

  const hlTitle = document.getElementById("helplines-title");
  if (hlTitle) hlTitle.textContent = t.helplinesTitle;

  // Re-run search if input already has a query
  if (inputEl && inputEl.value.trim() !== "") {
    let query = inputEl.value.trim();
    const en = TRANSLATIONS.en.quickLabels;
    const hi = TRANSLATIONS.hi.quickLabels;
    if      (query === en.lost  || query === hi.lost)  query = "lost report";
    else if (query === en.mv    || query === hi.mv)    query = "motor vehicle theft";
    else if (query === en.theft || query === hi.theft) query = "theft report";
    else if (query === en.pcc   || query === hi.pcc)   query = "police clearance";
    else if (query === en.cvr   || query === hi.cvr)   query = "character verification";
    runSearch(query);
  }
}

async function runSearch(queryText) {
  if (!queryText || queryText.trim() === "") return;

  // Clear any active guided flow
  if (guidedFlow) {
    guidedFlow = null;
    document.getElementById("guided-flow-container").classList.add("hidden");
  }

  const responseContainer   = document.getElementById("response-container");
  const welcomeInstruction  = document.getElementById("welcome-instruction");
  const answerEl            = document.getElementById("response-answer");
  const servicesList        = document.getElementById("services-list");

  welcomeInstruction.classList.add("hidden");
  responseContainer.classList.remove("hidden");
  answerEl.textContent = TRANSLATIONS[currentLanguage].searching;
  answerEl.classList.add("loading");
  servicesList.innerHTML = "";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: queryText, language: currentLanguage })
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    answerEl.classList.remove("loading");
    renderResults(data);
  } catch (error) {
    console.error("Fetch failed:", error);
    answerEl.classList.remove("loading");
    answerEl.innerHTML = currentLanguage === "en"
      ? `<div class="error-msg"><strong>Unable to connect to assistant backend.</strong><br>Please make sure the FastAPI server is running on localhost:8000 and try again.</div>`
      : `<div class="error-msg"><strong>असिस्टेंट सर्वर से कनेक्ट नहीं हो सका।</strong><br>कृपया सुनिश्चित करें कि FastAPI सर्वर localhost:8000 पर चल रहा है।</div>`;
  }
}

function renderResults(data) {
  const answerEl     = document.getElementById("response-answer");
  const servicesList = document.getElementById("services-list");
  const t            = TRANSLATIONS[currentLanguage];

  answerEl.textContent = data.answer;
  servicesList.innerHTML = "";

  if (!data.services || data.services.length === 0) {
    const noMatch = document.createElement("div");
    noMatch.className = "no-matches";
    noMatch.textContent = t.noMatches;
    servicesList.appendChild(noMatch);
    return;
  }

  data.services.forEach(service => {
    const card = document.createElement("div");
    card.className = "service-card";

    const cardHeader = document.createElement("div");
    cardHeader.className = "service-card-header";

    const title = document.createElement("h4");
    title.className = "service-title";
    title.textContent = service.name;
    cardHeader.appendChild(title);

    const badge = document.createElement("span");
    badge.className = service.requires_login ? "badge badge-warning" : "badge badge-success";
    badge.textContent = service.requires_login ? t.loginRequired : t.directAccess;
    cardHeader.appendChild(badge);
    card.appendChild(cardHeader);

    const desc = document.createElement("p");
    desc.className = "service-desc";
    desc.textContent = service.description;
    card.appendChild(desc);

    const actionBtn = document.createElement("a");
    actionBtn.className = "btn btn-card-action";
    actionBtn.href = service.url;
    actionBtn.target = "_blank";
    actionBtn.rel = "noopener noreferrer";
    actionBtn.textContent = t.openService;
    card.appendChild(actionBtn);

    servicesList.appendChild(card);
  });
}
