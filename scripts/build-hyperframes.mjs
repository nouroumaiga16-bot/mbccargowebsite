// Enveloppe chaque plan CSS (sequences/plan-N-*.html) dans une composition
// HyperFrames avec sa durée exacte :
//   16:9 -> hyperframes/plan-N/index.html           (1920x1080)
//   9:16 -> hyperframes/portrait/plan-N/index.html  (1080x1920, + sequences/portrait/plan-N.css)
import { readFileSync, writeFileSync, mkdirSync, readdirSync } from "node:fs";
import { join } from "node:path";

export const PLANS = [
  ["plan-1", 2], ["plan-2", 8], ["plan-3", 4], ["plan-4", 4],
  ["plan-5", 14], ["plan-6", 8], ["plan-7", 5],
];

const FORMATS = [
  { dir: "hyperframes", w: 1920, h: 1080, css: () => "" },
  {
    dir: "hyperframes/portrait", w: 1080, h: 1920,
    css: (id) => readFileSync(join("sequences/portrait", `${id}.css`), "utf8"),
  },
];

const files = readdirSync("sequences");
for (const [id, duration] of PLANS) {
  const src = files.find((f) => f.startsWith(id + "-") && f.endsWith(".html"));
  if (!src) throw new Error(`Plan introuvable : ${id}`);
  const source = readFileSync(join("sequences", src), "utf8");
  for (const { dir: base, w, h, css } of FORMATS) {
    const frame =
      `<style>html,body{width:${w}px;height:${h}px;margin:0;overflow:hidden}\n${css(id)}</style>\n`;
    const html = source
      .replace("</head>", frame + "</head>")
      .replace(/<body>([\s\S]*)<\/body>/, (_, inner) =>
        `<body>\n<div id="root" data-composition-id="${id}" data-start="0" data-no-timeline ` +
        `data-duration="${duration}" data-width="${w}" data-height="${h}">` +
        `${inner}</div>\n</body>`);
    const dir = join(base, id);
    mkdirSync(dir, { recursive: true });
    writeFileSync(join(dir, "index.html"), html);
    console.log(`${src} -> ${dir}/index.html (${w}x${h}, ${duration}s)`);
  }
}
