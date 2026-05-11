#!/usr/bin/env node
// Workaround for https://github.com/.../slidev-workspace plugin bug:
// its post-build regex `/^og-image-[a-zA-Z0-9]+\.png$/` rejects Vite hashes
// containing `_` or `-`, so og-image.png is not always copied to the dist
// root. Without this file the workspace homepage card preview shows no image.
//
// This script walks ./dist/<slide>/assets for any file matching
// og-image-*.png and ensures ./dist/<slide>/og-image.png exists.

import { existsSync, readdirSync, statSync, copyFileSync } from "node:fs";
import { join, resolve } from "node:path";

const OG_HASHED_RE = /^og-image-[A-Za-z0-9_-]+\.png$/;
const distDir = resolve(process.cwd(), "dist");

if (!existsSync(distDir)) {
  console.warn(`⚠ dist directory not found: ${distDir}`);
  process.exit(0);
}

const slideDirs = readdirSync(distDir, { withFileTypes: true })
  .filter((entry) => entry.isDirectory())
  .map((entry) => join(distDir, entry.name));

let copied = 0;
let alreadyPresent = 0;
let missingSource = 0;

for (const slideDir of slideDirs) {
  const assetsDir = join(slideDir, "assets");
  if (!existsSync(assetsDir) || !statSync(assetsDir).isDirectory()) continue;

  const destFile = join(slideDir, "og-image.png");
  if (existsSync(destFile)) {
    alreadyPresent++;
    continue;
  }

  const hashedOgImage = readdirSync(assetsDir).find((file) =>
    OG_HASHED_RE.test(file),
  );

  if (!hashedOgImage) {
    missingSource++;
    continue;
  }

  copyFileSync(join(assetsDir, hashedOgImage), destFile);
  console.log(`✅ Copied og-image for ${slideDir.replace(distDir + "/", "")}`);
  copied++;
}

console.log(
  `📦 og-image post-build: copied=${copied}, already_present=${alreadyPresent}, no_source=${missingSource}`,
);
