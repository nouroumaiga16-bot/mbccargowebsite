// Génère les deux projets HyperFrames à partir du gabarit unique :
//   motion/build/16x9/index.html  (1920x1080)
//   motion/build/9x16/index.html  (1080x1920)
// Chaque projet reçoit sa copie de motion/assets/ (GSAP, polices).
import { readFileSync, writeFileSync, mkdirSync, cpSync, rmSync } from "node:fs";

const template = readFileSync("motion/src/mbc-cargo.template.html", "utf8");
const FORMATS = [
  { dir: "motion/build/16x9", W: 1920, H: 1080, FMT: "land" },
  { dir: "motion/build/9x16", W: 1080, H: 1920, FMT: "port" },
];
for (const f of FORMATS) {
  rmSync(f.dir, { recursive: true, force: true });
  mkdirSync(f.dir, { recursive: true });
  cpSync("motion/assets", `${f.dir}/assets`, { recursive: true });
  writeFileSync(`${f.dir}/index.html`, template.replace(/\{\{(W|H|FMT)\}\}/g, (_, k) => f[k]));
  console.log(`${f.dir}/index.html (${f.W}x${f.H})`);
}
