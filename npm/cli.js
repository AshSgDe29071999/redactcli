#!/usr/bin/env node
"use strict";

/**
 * npx / npm bin for redactcli.
 *
 * Prefers a GitHub-release binary, then an already-installed CLI, then uvx,
 * then python -m. No extra npm runtime dependencies.
 */

const { spawnSync } = require("node:child_process");
const fs = require("node:fs");
const https = require("node:https");
const os = require("node:os");
const path = require("node:path");

const VERSION = "0.1.1";
const REPO = "AshSgDe29071999/redactcli";
const args = process.argv.slice(2);

function run(command, commandArgs) {
  return spawnSync(command, commandArgs, { stdio: "inherit" });
}

function has(command) {
  const probe = process.platform === "win32" ? "where" : "which";
  const result = spawnSync(probe, [command], { stdio: "ignore" });
  return result.status === 0;
}

function cacheDir() {
  const base =
    process.env.XDG_CACHE_HOME ||
    (process.platform === "win32"
      ? path.join(process.env.LOCALAPPDATA || os.tmpdir(), "redactcli")
      : path.join(os.homedir(), ".cache"));
  return path.join(base, "redactcli", VERSION);
}

function assetName() {
  const platform = process.platform;
  const arch = process.arch;
  if (platform === "linux" && (arch === "x64" || arch === "arm64")) {
    return `redactcli-linux-${arch === "x64" ? "x86_64" : "arm64"}`;
  }
  if (platform === "darwin" && (arch === "x64" || arch === "arm64")) {
    return `redactcli-macos-${arch === "x64" ? "x86_64" : "arm64"}`;
  }
  if (platform === "win32" && arch === "x64") {
    return "redactcli-windows-x86_64.exe";
  }
  return null;
}

function download(url, dest) {
  return new Promise((resolve, reject) => {
    const request = (current) => {
      https
        .get(
          current,
          {
            headers: {
              "User-Agent": "redactcli-npx",
              Accept: "application/octet-stream",
            },
          },
          (res) => {
            if (res.statusCode && res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
              request(res.headers.location);
              return;
            }
            if (res.statusCode !== 200) {
              reject(new Error(`download failed: ${res.statusCode} ${current}`));
              return;
            }
            const tmp = `${dest}.part`;
            const out = fs.createWriteStream(tmp);
            res.pipe(out);
            out.on("finish", () => {
              out.close(() => {
                fs.renameSync(tmp, dest);
                resolve();
              });
            });
          },
        )
        .on("error", reject);
    };
    request(url);
  });
}

async function ensureBinary() {
  const name = assetName();
  if (!name) {
    return null;
  }
  const dir = cacheDir();
  fs.mkdirSync(dir, { recursive: true });
  const dest = path.join(dir, name);
  if (fs.existsSync(dest) && fs.statSync(dest).size > 0) {
    return dest;
  }
  const url = `https://github.com/${REPO}/releases/download/v${VERSION}/${name}`;
  try {
    await download(url, dest);
    fs.chmodSync(dest, 0o755);
    return dest;
  } catch {
    try {
      fs.rmSync(dest, { force: true });
      fs.rmSync(`${dest}.part`, { force: true });
    } catch {
      // ignore
    }
    return null;
  }
}

async function main() {
  const binary = await ensureBinary();
  if (binary) {
    const result = run(binary, args);
    process.exit(result.status === null ? 1 : result.status);
  }

  const fallbacks = [];
  if (has("redactcli")) {
    fallbacks.push(["redactcli", args]);
  }
  if (has("uvx")) {
    fallbacks.push(["uvx", ["redactcli", ...args]]);
  }
  if (has("python3")) {
    fallbacks.push(["python3", ["-m", "redactcli", ...args]]);
  }
  if (has("python")) {
    fallbacks.push(["python", ["-m", "redactcli", ...args]]);
  }

  for (const [command, commandArgs] of fallbacks) {
    const result = run(command, commandArgs);
    if (result.status === 0 || result.status === 1) {
      process.exit(result.status);
    }
  }

  process.stderr.write(
    "redactcli: no binary, uvx, or Python CLI found.\n" +
      "Install one of:\n" +
      "  brew tap ashsgde29071999/redactcli && brew install redactcli\n" +
      "  uvx redactcli --help\n" +
      "  pipx install redactcli\n",
  );
  process.exit(127);
}

main().catch((error) => {
  process.stderr.write(`redactcli: ${error.message}\n`);
  process.exit(1);
});
