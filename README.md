# IG Splitter

A fully static, browser-only Instagram carousel splitter and profile grid maker.

## What it does

- Splits a panorama into 2–10 adjacent carousel slides.
- Splits a mural into a 3 × N profile grid with configurable gap compensation.
- Accepts JPG, PNG, and WebP by file picker or drag and drop.
- Exports lossless PNG files individually or in a ZIP.
- Keeps every source and generated image on the visitor's device.
- Includes a sourced guide separating official Instagram limits from practical grid assumptions.

## Stack

- TypeScript
- Vite
- Tailwind CSS 4
- daisyUI 5
- fflate for client-side ZIP packaging

There is no server, database, upload endpoint, React runtime, or analytics script.

## Run locally

```bash
npm install
npm run dev
```

## Verify and build

```bash
npm test
npm run build
```

The deployable static site is generated in `dist/`.

## Image-quality boundary

The splitter uses high-quality Canvas resampling and exports PNG to avoid an added lossy JPEG generation. Input that does not match the selected target shape is center-cropped and resized to the selected 1080 px-wide output. Instagram can still crop, resize, or recompress files after upload.
