const state = {
  samples: [],
  activeSampleId: null,
  selectedCandidateId: null,
};

const sampleList = document.getElementById("sampleList");
const candidateList = document.getElementById("candidateList");
const statusSummary = document.getElementById("statusSummary");
const sampleTitle = document.getElementById("sampleTitle");
const sampleMeta = document.getElementById("sampleMeta");
const pageImage = document.getElementById("pageImage");
const boxLayer = document.getElementById("boxLayer");
const showBoxes = document.getElementById("showBoxes");
const showDebugImage = document.getElementById("showDebugImage");

async function loadSamples() {
  const response = await fetch("/api/samples");
  const data = await response.json();
  state.samples = data.samples || [];
  state.activeSampleId = state.samples[0]?.id || null;
  render();
}

function activeSample() {
  return state.samples.find((sample) => sample.id === state.activeSampleId);
}

function render() {
  renderSamples();
  renderActiveSample();
}

function renderSamples() {
  sampleList.innerHTML = "";
  state.samples.forEach((sample) => {
    const button = document.createElement("button");
    button.className = `sample-card ${sample.id === state.activeSampleId ? "active" : ""}`;
    button.innerHTML = `
      <div class="sample-name">${escapeHtml(sample.id)}</div>
      <div class="sample-detail">${sample.ocr_box_count} 个 OCR 框<br>${sample.image_size.width} x ${sample.image_size.height}</div>
    `;
    button.addEventListener("click", () => {
      state.activeSampleId = sample.id;
      state.selectedCandidateId = null;
      render();
    });
    sampleList.appendChild(button);
  });
}

function renderActiveSample() {
  const sample = activeSample();
  if (!sample) {
    sampleTitle.textContent = "没有可验收样本";
    sampleMeta.textContent = "";
    candidateList.innerHTML = '<div class="empty-state">请先运行 OCR 生成 JSON 和图片。</div>';
    return;
  }

  sampleTitle.textContent = sample.id;
  sampleMeta.textContent = `${sample.ocr_box_count} 个 OCR 框，${sample.question_candidates.length} 个题目候选`;
  pageImage.src = fileUrl(showDebugImage.checked ? sample.debug_image : sample.preprocessed_image);
  pageImage.onload = () => renderBoxes(sample);
  renderBoxes(sample);
  renderCandidates(sample);
}

function renderBoxes(sample) {
  boxLayer.innerHTML = "";
  boxLayer.style.display = showBoxes.checked && !showDebugImage.checked ? "block" : "none";
  const imageWidth = pageImage.naturalWidth || sample.image_size.width;
  const imageHeight = pageImage.naturalHeight || sample.image_size.height;
  const displayWidth = pageImage.clientWidth || imageWidth;
  const displayHeight = pageImage.clientHeight || imageHeight;
  boxLayer.setAttribute("viewBox", `0 0 ${imageWidth} ${imageHeight}`);
  boxLayer.style.width = `${displayWidth}px`;
  boxLayer.style.height = `${displayHeight}px`;

  sample.boxes.forEach((box, index) => {
    const points = box.points || [];
    if (!points.length) return;
    const xs = points.map((point) => Number(point[0]));
    const ys = points.map((point) => Number(point[1]));
    const x = Math.min(...xs);
    const y = Math.min(...ys);
    const width = Math.max(...xs) - x;
    const height = Math.max(...ys) - y;
    const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    rect.setAttribute("x", x);
    rect.setAttribute("y", y);
    rect.setAttribute("width", width);
    rect.setAttribute("height", height);
    rect.classList.add("ocr-box");
    if (selectedCandidate(sample)?.box_index === index) {
      rect.classList.add("selected");
    }
    boxLayer.appendChild(rect);
  });
}

function renderCandidates(sample) {
  candidateList.innerHTML = "";
  const counts = countStatuses(sample.question_candidates);
  statusSummary.innerHTML = `
    <span class="status-pill">待确认 ${counts.pending}</span>
    <span class="status-pill">正确 ${counts.correct}</span>
    <span class="status-pill">错误 ${counts.incorrect}</span>
  `;

  if (!sample.question_candidates.length) {
    candidateList.innerHTML = '<div class="empty-state">暂未抽取到题目候选。请查看 OCR 框和完整 JSON。</div>';
    return;
  }

  sample.question_candidates.forEach((candidate) => {
    const card = document.createElement("article");
    card.className = `candidate-card ${candidate.id === state.selectedCandidateId ? "selected" : ""}`;
    card.innerHTML = `
      <div class="candidate-head">
        <span class="candidate-label">${escapeHtml(candidate.label)}</span>
        <span class="status ${candidate.status}">${statusText(candidate.status)}</span>
      </div>
      <div class="candidate-text">${escapeHtml(candidate.text)}</div>
      <div class="candidate-meta">置信度 ${formatConfidence(candidate.confidence)}，位置 ${Math.round(candidate.bounds.x)}, ${Math.round(candidate.bounds.y)}</div>
      <div class="candidate-actions">
        <button data-status="correct">正确</button>
        <button data-status="incorrect">错误</button>
        <button data-status="pending">待确认</button>
      </div>
    `;
    card.addEventListener("click", () => {
      state.selectedCandidateId = candidate.id;
      renderBoxes(sample);
      renderCandidates(sample);
    });
    card.querySelectorAll("button[data-status]").forEach((button) => {
      button.addEventListener("click", async (event) => {
        event.stopPropagation();
        await updateStatus(sample.id, candidate.id, button.dataset.status);
      });
    });
    candidateList.appendChild(card);
  });
}

async function updateStatus(sampleId, candidateId, status) {
  const response = await fetch("/api/reviews", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({sample_id: sampleId, candidate_id: candidateId, status}),
  });
  if (!response.ok) return;
  const sample = activeSample();
  const candidate = sample.question_candidates.find((item) => item.id === candidateId);
  if (candidate) candidate.status = status;
  renderCandidates(sample);
}

function selectedCandidate(sample) {
  return sample.question_candidates.find((candidate) => candidate.id === state.selectedCandidateId);
}

function countStatuses(candidates) {
  return candidates.reduce(
    (counts, candidate) => {
      counts[candidate.status] = (counts[candidate.status] || 0) + 1;
      return counts;
    },
    {pending: 0, correct: 0, incorrect: 0},
  );
}

function fileUrl(path) {
  return `/files/${encodeURIComponent(path).replaceAll("%5C", "/").replaceAll("%2F", "/")}`;
}

function statusText(status) {
  if (status === "correct") return "正确";
  if (status === "incorrect") return "错误";
  return "待确认";
}

function formatConfidence(value) {
  return `${Math.round(Number(value || 0) * 100)}%`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

showBoxes.addEventListener("change", () => renderActiveSample());
showDebugImage.addEventListener("change", () => renderActiveSample());
window.addEventListener("resize", () => {
  const sample = activeSample();
  if (sample) renderBoxes(sample);
});

loadSamples();
