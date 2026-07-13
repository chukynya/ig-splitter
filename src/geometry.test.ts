import assert from "node:assert/strict";
import test from "node:test";
import {
  carouselPlan,
  gridDesignSize,
  gridPlan,
} from "./geometry.ts";

test("a 3240x1350 panorama becomes three exact 4:5 slides", () => {
  const plan = carouselPlan(3240, 1350, 4 / 5, "auto");

  assert.equal(plan.count, 3);
  assert.deepEqual(plan.crop, { x: 0, y: 0, width: 3240, height: 1350 });
  assert.deepEqual(
    plan.slices.map(({ x, width, outputWidth, outputHeight }) => ({
      x,
      width,
      outputWidth,
      outputHeight,
    })),
    [
      { x: 0, width: 1080, outputWidth: 1080, outputHeight: 1350 },
      { x: 1080, width: 1080, outputWidth: 1080, outputHeight: 1350 },
      { x: 2160, width: 1080, outputWidth: 1080, outputHeight: 1350 },
    ],
  );
});

test("grid planning leaves the chosen design gap and reverses upload order", () => {
  const design = gridDesignSize(3, 10);
  assert.deepEqual(design, {
    rows: 3,
    gap: 10,
    width: 3130,
    height: 4080,
  });

  const plan = gridPlan(3240, 4050, 3, 10);
  assert.equal(plan.slices.length, 9);
  assert.deepEqual(
    plan.slices.map(({ postOrder }) => postOrder),
    [9, 8, 7, 6, 5, 4, 3, 2, 1],
  );
  assert.ok(
    plan.slices.every(
      ({ width, height, outputWidth, outputHeight }) =>
        width === 1072 &&
        height === 1340 &&
        outputWidth === 1072 &&
        outputHeight === 1340,
    ),
  );
  assert.deepEqual(
    [0, 1, 2].map((column) => plan.slices[column].x),
    [66, 1083, 2100],
  );
  assert.deepEqual(
    [0, 1, 2].map((row) => plan.slices[row * 3].y),
    [10, 1360, 2710],
  );
});
