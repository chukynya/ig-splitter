import { zip } from "fflate";
import type { SlicePlan } from "./geometry.ts";

export type SplitResult = {
  blob: Blob;
  height: number;
  name: string;
  postOrder: number;
  url: string;
  width: number;
};

export type SplitGroup = {
  fileName: string;
  sourceHeight: number;
  sourceWidth: number;
  results: SplitResult[];
};

const canvasBlob = (canvas: HTMLCanvasElement) =>
  new Promise<Blob>((resolve, reject) => {
    // PNG is intentional: exporting JPEG here would add another lossy generation.
    canvas.toBlob(
      (blob) => (blob ? resolve(blob) : reject(new Error("PNG export failed."))),
      "image/png",
    );
  });

const loadImage = async (file: File) => {
  const url = URL.createObjectURL(file);
  const image = new Image();
  image.decoding = "async";
  image.src = url;

  try {
    await image.decode();
    return image;
  } catch {
    throw new Error(`${file.name} could not be decoded by this browser.`);
  } finally {
    URL.revokeObjectURL(url);
  }
};

export async function splitFile(
  file: File,
  planFor: (width: number, height: number) => SlicePlan[],
  nameFor: (plan: SlicePlan) => string,
): Promise<SplitGroup> {
  const source = await loadImage(file);
  const plans = planFor(source.naturalWidth, source.naturalHeight);
  const results: SplitResult[] = [];

  for (const plan of plans) {
    const canvas = document.createElement("canvas");
    canvas.width = plan.outputWidth;
    canvas.height = plan.outputHeight;
    const context = canvas.getContext("2d", { alpha: true });

    if (!context) throw new Error("Canvas is not available in this browser.");

    context.imageSmoothingEnabled = true;
    context.imageSmoothingQuality = "high";
    context.drawImage(
      source,
      plan.x,
      plan.y,
      plan.width,
      plan.height,
      0,
      0,
      plan.outputWidth,
      plan.outputHeight,
    );

    const blob = await canvasBlob(canvas);
    results.push({
      blob,
      height: plan.outputHeight,
      name: nameFor(plan),
      postOrder: plan.postOrder,
      url: URL.createObjectURL(blob),
      width: plan.outputWidth,
    });
  }

  return {
    fileName: file.name,
    sourceHeight: source.naturalHeight,
    sourceWidth: source.naturalWidth,
    results,
  };
}

export function downloadBlob(blob: Blob, name: string) {
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);
  link.href = url;
  link.download = name;
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1_000);
}

export async function downloadZip(
  groups: SplitGroup[],
  name: string,
): Promise<void> {
  const duplicateNames = new Set<string>();
  const files: Record<string, Uint8Array> = {};

  for (const group of groups) {
    const folder = safeBaseName(group.fileName);
    const prefix = groups.length > 1 ? `${folder}/` : "";

    for (const result of [...group.results].sort(
      (a, b) => a.postOrder - b.postOrder,
    )) {
      let entryName = `${prefix}${result.name}`;
      let suffix = 2;
      while (duplicateNames.has(entryName)) {
        entryName = `${prefix}${suffix}-${result.name}`;
        suffix += 1;
      }
      duplicateNames.add(entryName);
      files[entryName] = new Uint8Array(await result.blob.arrayBuffer());
    }
  }

  const archive = await new Promise<Uint8Array>((resolve, reject) => {
    zip(files, { level: 0 }, (error, data) =>
      error ? reject(error) : resolve(data),
    );
  });

  const bytes = new Uint8Array(archive.byteLength);
  bytes.set(archive);
  downloadBlob(new Blob([bytes.buffer], { type: "application/zip" }), name);
}

export function safeBaseName(name: string) {
  return (
    name
      .replace(/\.[^/.]+$/, "")
      .normalize("NFKD")
      .replace(/[^a-zA-Z0-9_-]+/g, "-")
      .replace(/^-+|-+$/g, "")
      .toLowerCase() || "image"
  );
}

export function releaseGroups(groups: SplitGroup[]) {
  for (const group of groups) {
    for (const result of group.results) URL.revokeObjectURL(result.url);
  }
}
