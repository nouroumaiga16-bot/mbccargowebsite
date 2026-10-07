// Enveloppe chaque plan CSS (sequences/plan-N-*.html) dans une composition
// HyperFrames : hyperframes/plan-N/index.html, avec sa durée exacte.
import { readFileSync, writeFileSync, mkdirSync, readdirSync } from "node:fs";
import { join } from "node:path";

export const PLANS = [
  ["plan-1", 2], ["plan-2", 8], ["plan-3", 4], ["plan-4", 4],
  ["plan-5", 14], ["plan-6", 8], ["plan-7", 5],
];

const files = readdirSync("sequences");
for (const [id, duration] of PLANS) {
  const src = files.find((f) => f.startsWith(id + "-") && f.endsWith(".html"));
  if (!src) throw new Error(`Plan introuvable : ${id}`);
  let html = readFileSync(join("sequences", src), "utf8");
  const frame =
    "<style>html,body{width:1920px;height:1080px;margin:0;overflow:hidden}</style>\n";
  html = html.replace("</head>", frame + "</head>");
  html = html.replace(/<body>([\s\S]*)<\/body>/, (_, inner) =>
    `<body>\n<div id="root" data-composition-id="${id}" data-start="0" data-no-timeline ` +
    `data-duration="${duration}" data-width="1920" data-height="1080">` +
    `${inner}</div>\n</body>`);
  const dir = join("hyperframes", id);
  mkdirSync(dir, { recursive: true });
  writeFileSync(join(dir, "index.html"), html);
  console.log(`${src} -> ${dir}/index.html (${duration}s)`);
}
