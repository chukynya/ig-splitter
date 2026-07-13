export const OUTPUT_WIDTH = 1080;
export const FEED_HEIGHT = 1350;
export const PROFILE_PREVIEW_WIDTH = 1015;
export const GRID_COLUMNS = 3;

export type Rect = {
  x: number;
  y: number;
  width: number;
  height: number;
};

export type SlicePlan = Rect & {
  index: number;
  postOrder: number;
  outputWidth: number;
  outputHeight: number;
};

export type CarouselPlan = {
  count: number;
  crop: Rect;
  slices: SlicePlan[];
};

export type GridPlan = {
  crop: Rect;
  designWidth: number;
  designHeight: number;
  slices: SlicePlan[];
};

const validDimension = (value: number) => Number.isFinite(value) && value > 0;

export function coverCrop(
  sourceWidth: number,
  sourceHeight: number,
  targetRatio: number,
): Rect {
  if (![sourceWidth, sourceHeight, targetRatio].every(validDimension)) {
    throw new RangeError("Image dimensions and target ratio must be positive.");
  }

  const sourceRatio = sourceWidth / sourceHeight;
  if (Math.abs(sourceRatio - targetRatio) < 1e-12) {
    return { x: 0, y: 0, width: sourceWidth, height: sourceHeight };
  }

  if (sourceRatio > targetRatio) {
    const width = sourceHeight * targetRatio;
    return { x: (sourceWidth - width) / 2, y: 0, width, height: sourceHeight };
  }

  const height = sourceWidth / targetRatio;
  return { x: 0, y: (sourceHeight - height) / 2, width: sourceWidth, height };
}

export function carouselPlan(
  sourceWidth: number,
  sourceHeight: number,
  slideAspect: number,
  requestedCount: number | "auto",
): CarouselPlan {
  const count =
    requestedCount === "auto"
      ? Math.min(
          10,
          Math.max(2, Math.round(sourceWidth / sourceHeight / slideAspect)),
        )
      : Math.min(10, Math.max(2, Math.round(requestedCount)));
  const outputHeight = Math.round(OUTPUT_WIDTH / slideAspect);
  const crop = coverCrop(sourceWidth, sourceHeight, count * slideAspect);
  const sliceWidth = crop.width / count;

  return {
    count,
    crop,
    slices: Array.from({ length: count }, (_, index) => ({
      x: crop.x + sliceWidth * index,
      y: crop.y,
      width: sliceWidth,
      height: crop.height,
      index,
      postOrder: index + 1,
      outputWidth: OUTPUT_WIDTH,
      outputHeight,
    })),
  };
}

export function gridDesignSize(rows: number, gap: number) {
  const safeRows = Math.min(12, Math.max(1, Math.round(rows)));
  const safeGap = Math.min(200, Math.max(0, Math.round(gap)));

  return {
    rows: safeRows,
    gap: safeGap,
    width:
      OUTPUT_WIDTH +
      (GRID_COLUMNS - 1) * (PROFILE_PREVIEW_WIDTH + safeGap),
    height: safeRows * (FEED_HEIGHT + safeGap),
  };
}

export function gridPlan(
  sourceWidth: number,
  sourceHeight: number,
  rows: number,
  gap: number,
): GridPlan {
  const design = gridDesignSize(rows, gap);
  const rowAspect = design.width / (FEED_HEIGHT + design.gap);
  const heightFromWidth = sourceWidth / rowAspect;
  const rowHeight =
    heightFromWidth * design.rows > sourceHeight
      ? Math.floor(sourceHeight / design.rows)
      : Math.round(heightFromWidth);

  if (rowHeight < 1) {
    throw new RangeError("Image is too short for the selected number of rows.");
  }

  const rowWidth = rowHeight * rowAspect;
  const cropX =
    heightFromWidth * design.rows > sourceHeight
      ? Math.floor((sourceWidth - rowWidth) / 2)
      : 0;
  const gapWidth = Math.round(
    (design.gap / (FEED_HEIGHT + design.gap)) * rowHeight,
  );
  const cutoffWidth = Math.round(
    ((OUTPUT_WIDTH - PROFILE_PREVIEW_WIDTH) /
      (FEED_HEIGHT + design.gap)) *
      rowHeight,
  );
  const outputWidth = Math.round(
    (OUTPUT_WIDTH / (FEED_HEIGHT + design.gap)) * rowHeight,
  );
  const outputHeight = rowHeight - gapWidth;
  const cropY = sourceHeight - rowHeight * design.rows + gapWidth;

  if (outputWidth < 1 || outputHeight < 1) {
    throw new RangeError("Image is too small for the selected gap and rows.");
  }

  const crop = {
    x: cropX,
    y: cropY - gapWidth,
    width: rowWidth,
    height: rowHeight * design.rows,
  };
  const slices: SlicePlan[] = [];

  for (let row = 0; row < design.rows; row += 1) {
    for (let column = 0; column < GRID_COLUMNS; column += 1) {
      const index = row * GRID_COLUMNS + column;
      slices.push({
        x:
          cropX +
          column * (outputWidth + gapWidth - cutoffWidth),
        y: cropY + row * (outputHeight + gapWidth),
        width: outputWidth,
        height: outputHeight,
        index,
        postOrder: design.rows * GRID_COLUMNS - index,
        outputWidth,
        outputHeight,
      });
    }
  }

  return {
    crop,
    designWidth: design.width,
    designHeight: design.height,
    slices,
  };
}
