#!/usr/bin/env node
// Compatibility shim. Canonical file lives under dex/ops/scripts/javascript/.
const { spawnSync } = require("child_process");
const path = require("path");
const target = path.join(__dirname, "..", "dex/ops/scripts/javascript/extract-download-urls.js");
const result = spawnSync(process.execPath, [target, ...process.argv.slice(2)], {
  stdio: "inherit",
});
process.exit(result.status === null ? 1 : result.status);
