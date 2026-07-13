import {
  carouselPlan,
  gridDesignSize,
  gridPlan,
  type SlicePlan,
} from "./geometry.ts";
import {
  downloadBlob,
  downloadZip,
  releaseGroups,
  safeBaseName,
  splitFile,
  type SplitGroup,
} from "./images.ts";

type Mode = "carousel" | "grid";
type QueuedFile = { file: File; id: string; url: string };

const MAX_FILE_SIZE = 30 * 1024 * 1024;
const IMAGE_TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);
const modeCopy = {
  carousel: {
    badge: "NO GAP",
    description:
      "Create consecutive, swipe-ready slides from one wide image. Every slide is exported as a lossless PNG at Instagram-ready width.",
    kicker: "CAROUSEL / 2–10 SLIDES",
    splitLabel: "Split carousel",
    title: "Carousel split",
  },
  grid: {
    badge: "3 × N",
    description:
      "Turn a mural into profile posts while accounting for the visual space between Instagram grid tiles.",
    kicker: "PROFILE GRID / GAP AWARE",
    splitLabel: "Make grid",
    title: "Grid maker",
  },
} satisfies Record<Mode, Record<string, string>>;

const byId = <T extends HTMLElement>(id: string) => {
  const element = document.getElementById(id);
  if (!element) throw new Error(`Missing #${id}`);
  return element as T;
};

const homeView = byId<HTMLElement>("home-view");
const toolView = byId<HTMLElement>("tool-view");
const toolKicker = byId<HTMLElement>("tool-kicker");
const toolTitle = byId<HTMLElement>("tool-title");
const toolDescription = byId<HTMLElement>("tool-description");
const modeBadge = byId<HTMLElement>("mode-badge");
const carouselSettings = byId<HTMLElement>("carousel-settings");
const gridSettings = byId<HTMLElement>("grid-settings");
const carouselAspect = byId<HTMLSelectElement>("carousel-aspect");
const carouselCount = byId<HTMLSelectElement>("carousel-count");
const gridRows = byId<HTMLInputElement>("grid-rows");
const gridGap = byId<HTMLInputElement>("grid-gap");
const gridSize = byId<HTMLElement>("grid-size");
const dropzone = byId<HTMLElement>("dropzone");
const fileInput = byId<HTMLInputElement>("file-input");
const fileQueue = byId<HTMLElement>("file-queue");
const fileError = byId<HTMLElement>("file-error");
const splitButton = byId<HTMLButtonElement>("split-button");
const splitLabel = byId<HTMLElement>("split-label");
const downloadAllButton = byId<HTMLButtonElement>("download-all");
const emptyResults = byId<HTMLElement>("empty-results");
const processing = byId<HTMLElement>("processing");
const processingLabel = byId<HTMLElement>("processing-label");
const resultsElement = byId<HTMLElement>("results");
const status = byId<HTMLElement>("status");

let mode: Mode | null = null;
let queue: QueuedFile[] = [];
let groups: SplitGroup[] = [];
let busy = false;

const formatBytes = (bytes: number) => {
  if (bytes < 1024 * 1024) return `${Math.ceil(bytes / 1024)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
};

const currentGrid = () =>
  gridDesignSize(Number(gridRows.value), Number(gridGap.value));

function updateGridSize() {
  const design = currentGrid();
  gridSize.textContent = `${Math.round(design.width)} × ${Math.round(design.height)} px`;
}

function showError(message: string) {
  fileError.className = "alert alert-warning rounded-2xl text-sm";
  fileError.textContent = message;
}

function clearError() {
  fileError.className = "alert hidden rounded-2xl text-sm";
  fileError.textContent = "";
}

function resetResults() {
  releaseGroups(groups);
  groups = [];
  resultsElement.replaceChildren();
  resultsElement.classList.add("hidden");
  downloadAllButton.classList.add("hidden");
  emptyResults.classList.remove("hidden");
}

function renderQueue() {
  fileQueue.replaceChildren();
  fileQueue.classList.toggle("hidden", queue.length === 0);

  for (const item of queue) {
    const row = document.createElement("div");
    row.className = "queue-item";

    const image = document.createElement("img");
    image.src = item.url;
    image.alt = "";

    const copy = document.createElement("div");
    copy.className = "min-w-0";
    const name = document.createElement("p");
    name.className = "queue-name";
    name.textContent = item.file.name;
    const meta = document.createElement("p");
    meta.className = "queue-meta";
    meta.textContent = formatBytes(item.file.size);
    copy.append(name, meta);

    const remove = document.createElement("button");
    remove.className = "queue-remove";
    remove.type = "button";
    remove.setAttribute("aria-label", `Remove ${item.file.name}`);
    remove.textContent = "×";
    remove.addEventListener("click", () => {
      URL.revokeObjectURL(item.url);
      queue = queue.filter(({ id }) => id !== item.id);
      renderQueue();
      resetResults();
      updateActions();
    });

    row.append(image, copy, remove);
    fileQueue.append(row);
  }
}

function updateActions() {
  splitButton.disabled = queue.length === 0 || busy;
  if (mode) splitLabel.textContent = busy ? "Working locally…" : modeCopy[mode].splitLabel;
}

function addFiles(files: File[]) {
  clearError();
  const issues: string[] = [];

  for (const file of files) {
    if (!IMAGE_TYPES.has(file.type)) {
      issues.push(`${file.name}: use JPG, PNG, or WebP.`);
      continue;
    }
    if (file.size > MAX_FILE_SIZE) {
      issues.push(`${file.name}: larger than 30 MB.`);
      continue;
    }
    if (
      queue.some(
        ({ file: existing }) =>
          existing.name === file.name &&
          existing.size === file.size &&
          existing.lastModified === file.lastModified,
      )
    ) {
      continue;
    }

    queue.push({ file, id: crypto.randomUUID(), url: URL.createObjectURL(file) });
  }

  if (issues.length) showError(issues.join(" "));
  renderQueue();
  resetResults();
  updateActions();
}

function applyMode(nextMode: Mode | null) {
  if (mode && nextMode && mode !== nextMode) resetResults();
  mode = nextMode;

  if (!mode) {
    homeView.classList.remove("hidden");
    toolView.classList.add("hidden");
    document.title = "IG Splitter — crisp carousels and grids";
    return;
  }

  const copy = modeCopy[mode];
  homeView.classList.add("hidden");
  toolView.classList.remove("hidden");
  carouselSettings.classList.toggle("hidden", mode !== "carousel");
  gridSettings.classList.toggle("hidden", mode !== "grid");
  toolKicker.textContent = copy.kicker;
  toolTitle.textContent = copy.title;
  toolDescription.textContent = copy.description;
  modeBadge.textContent = copy.badge;
  document.title = `${copy.title} — IG Splitter`;
  updateActions();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function applyHash() {
  const hash = window.location.hash.slice(1);
  applyMode(hash === "carousel" || hash === "grid" ? hash : null);
}

const downloadIcon = () => {
  const icon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  icon.setAttribute("viewBox", "0 0 24 24");
  icon.setAttribute("aria-hidden", "true");
  icon.innerHTML = '<path d="M12 4v11m0 0 4-4m-4 4-4-4M5 19h14"/>';
  return icon;
};

function renderResults() {
  resultsElement.replaceChildren();

  for (const group of groups) {
    const section = document.createElement("section");
    const header = document.createElement("div");
    header.className = "result-group-header";
    const headingCopy = document.createElement("div");
    headingCopy.className = "min-w-0";
    const heading = document.createElement("h3");
    heading.textContent = group.fileName;
    const meta = document.createElement("p");
    meta.textContent = `${group.sourceWidth} × ${group.sourceHeight} source · ${group.results.length} outputs`;
    headingCopy.append(heading, meta);
    const format = document.createElement("span");
    format.className = "badge badge-success badge-sm rounded-full font-bold";
    format.textContent = "LOSSLESS PNG";
    header.append(headingCopy, format);

    const preview = document.createElement("div");
    preview.className = `result-preview ${mode === "grid" ? "grid-preview" : "carousel-preview"}`;
    if (mode === "grid") {
      preview.style.gap = `${Math.min(8, Math.max(1, currentGrid().gap / 2))}px`;
    }

    for (const result of group.results) {
      const tile = document.createElement("div");
      tile.className = "result-tile";
      tile.style.setProperty("--tile-aspect", `${result.width} / ${result.height}`);
      const image = document.createElement("img");
      image.src = result.url;
      image.alt = `${mode === "grid" ? "Grid post" : "Carousel slide"} ${result.postOrder}`;
      const number = document.createElement("span");
      number.className = "tile-number";
      number.textContent = String(result.postOrder).padStart(2, "0");
      const download = document.createElement("button");
      download.className = "tile-download";
      download.type = "button";
      download.title = `Download ${result.name}`;
      download.setAttribute("aria-label", `Download ${result.name}`);
      download.append(downloadIcon());
      download.addEventListener("click", () => downloadBlob(result.blob, result.name));
      tile.append(image, number, download);
      preview.append(tile);
    }

    const note = document.createElement("p");
    note.className = "output-note";
    note.textContent =
      mode === "grid"
        ? "Preview uses the centered 3:4 profile crop. Files are full 1080 × 1350 posts; upload 01 first."
        : "Shown left to right. Upload slide 01, then 02, and continue in order.";
    section.append(header, preview, note);
    resultsElement.append(section);
  }

  const hasResults = groups.length > 0;
  emptyResults.classList.toggle("hidden", hasResults);
  resultsElement.classList.toggle("hidden", !hasResults);
  downloadAllButton.classList.toggle("hidden", !hasResults);
}

function planFor(width: number, height: number): SlicePlan[] {
  if (mode === "grid") {
    const design = currentGrid();
    return gridPlan(width, height, design.rows, design.gap).slices;
  }

  const aspect = Number(carouselAspect.value);
  const count = carouselCount.value === "auto" ? "auto" : Number(carouselCount.value);
  return carouselPlan(width, height, aspect, count).slices;
}

async function processQueue() {
  if (!mode || busy || queue.length === 0) return;

  busy = true;
  clearError();
  resetResults();
  emptyResults.classList.add("hidden");
  processing.classList.remove("hidden");
  updateActions();
  const completed: SplitGroup[] = [];
  const errors: string[] = [];

  for (const [index, item] of queue.entries()) {
    processingLabel.textContent = `Splitting ${index + 1} of ${queue.length}: ${item.file.name}`;
    const base = safeBaseName(item.file.name);

    try {
      completed.push(
        await splitFile(item.file, planFor, (plan) => {
          const order = String(plan.postOrder).padStart(2, "0");
          return `${order}-${base}-${mode}.png`;
        }),
      );
    } catch (error) {
      errors.push(error instanceof Error ? error.message : `${item.file.name} failed.`);
    }
  }

  groups = completed;
  processing.classList.add("hidden");
  busy = false;
  renderResults();
  updateActions();
  status.textContent = `${groups.reduce((sum, group) => sum + group.results.length, 0)} images are ready to download.`;
  if (errors.length) showError(errors.join(" "));
}

for (const button of document.querySelectorAll<HTMLElement>("[data-open-mode]")) {
  button.addEventListener("click", () => {
    window.location.hash = button.dataset.openMode ?? "home";
  });
}

byId<HTMLButtonElement>("back-button").addEventListener("click", () => {
  window.location.hash = "home";
});

dropzone.addEventListener("click", () => fileInput.click());
dropzone.addEventListener("keydown", (event) => {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    fileInput.click();
  }
});

for (const eventName of ["dragenter", "dragover"]) {
  dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.add("is-dragging");
  });
}

for (const eventName of ["dragleave", "drop"]) {
  dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.remove("is-dragging");
  });
}

dropzone.addEventListener("drop", (event) => {
  if (event instanceof DragEvent && event.dataTransfer) {
    addFiles([...event.dataTransfer.files]);
  }
});

fileInput.addEventListener("change", () => {
  addFiles([...(fileInput.files ?? [])]);
  fileInput.value = "";
});

for (const control of [carouselAspect, carouselCount, gridRows, gridGap]) {
  control.addEventListener("change", () => {
    updateGridSize();
    resetResults();
  });
}

gridRows.addEventListener("input", updateGridSize);
gridGap.addEventListener("input", updateGridSize);
splitButton.addEventListener("click", processQueue);

downloadAllButton.addEventListener("click", async () => {
  if (!mode || groups.length === 0 || busy) return;
  downloadAllButton.disabled = true;
  downloadAllButton.textContent = "Packing locally…";
  try {
    await downloadZip(groups, `ig-${mode}-split.zip`);
  } catch {
    showError("The ZIP could not be created. Download the tiles individually instead.");
  } finally {
    downloadAllButton.disabled = false;
    downloadAllButton.textContent = "Download all .zip";
  }
});

window.addEventListener("hashchange", applyHash);
window.addEventListener("beforeunload", () => {
  for (const item of queue) URL.revokeObjectURL(item.url);
  releaseGroups(groups);
});

updateGridSize();
applyHash();
