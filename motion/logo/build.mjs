// Génère les projets HyperFrames du logo animé : motion/logo/build/{16x9,9x16,1x1}/index.html
import { readFileSync, writeFileSync, mkdirSync, cpSync, rmSync } from "node:fs";

const template = readFileSync("motion/logo/src/logo.template.html", "utf8");
const FORMATS = [
  { dir: "motion/logo/build/16x9", W: 1920, H: 1080, FMT: "land" },
  { dir: "motion/logo/build/9x16", W: 1080, H: 1920, FMT: "port" },
  { dir: "motion/logo/build/1x1", W: 1080, H: 1080, FMT: "sq" },
];
for (const f of FORMATS) {
  rmSync(f.dir, { recursive: true, force: true });
  mkdirSync(`${f.dir}/assets`, { recursive: true });
  cpSync("motion/logo/assets/calques", `${f.dir}/assets/calques`, { recursive: true });
  cpSync("motion/logo/assets/son-logo.m4a", `${f.dir}/assets/son-logo.m4a`);
  cpSync("motion/assets/gsap.min.js", `${f.dir}/assets/gsap.min.js`);
  mkdirSync(`${f.dir}/assets/fonts`, { recursive: true });
  cpSync("motion/assets/fonts/space-grotesk-latin-500-normal.woff2", `${f.dir}/assets/fonts/space-grotesk-latin-500-normal.woff2`);
  writeFileSync(`${f.dir}/index.html`, template.replace(/\{\{(W|H|FMT)\}\}/g, (_, k) => f[k]));
  console.log(`${f.dir}/index.html (${f.W}x${f.H})`);
}
