// Génère les projets HyperFrames de l'ensemble running : motion/tenue/build/{9x16,1x1,16x9}/index.html
import { readFileSync, writeFileSync, mkdirSync, cpSync, rmSync } from "node:fs";

const template = readFileSync("motion/tenue/src/tenue.template.html", "utf8");
const FORMATS = [
  { dir: "motion/tenue/build/9x16", W: 1080, H: 1920, FMT: "port" },
  { dir: "motion/tenue/build/1x1", W: 1080, H: 1080, FMT: "sq" },
  { dir: "motion/tenue/build/16x9", W: 1920, H: 1080, FMT: "land" },
];
for (const f of FORMATS) {
  rmSync(f.dir, { recursive: true, force: true });
  mkdirSync(f.dir, { recursive: true });
  cpSync("motion/tenue/assets", `${f.dir}/assets`, { recursive: true });
  cpSync("motion/assets/gsap.min.js", `${f.dir}/assets/gsap.min.js`);
  writeFileSync(`${f.dir}/index.html`, template.replace(/\{\{(W|H|FMT)\}\}/g, (_, k) => f[k]));
  console.log(`${f.dir}/index.html (${f.W}x${f.H})`);
}
