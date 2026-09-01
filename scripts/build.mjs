import { cp, mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "..");
const source = path.join(root, "frontend");
const output = path.join(root, "dist");
await mkdir(output, { recursive: true });
await cp(source, output, { recursive: true });
const apiBaseUrl = process.env.API_BASE_URL || "http://127.0.0.1:8000";
await writeFile(path.join(output, "config.js"), `window.APP_CONFIG = ${JSON.stringify({ API_BASE_URL: apiBaseUrl })};\n`, "utf8");
const index = await readFile(path.join(output, "index.html"), "utf8");
await writeFile(path.join(output, "index.html"), index, "utf8");
console.log(`Built frontend with API_BASE_URL=${apiBaseUrl}`);
