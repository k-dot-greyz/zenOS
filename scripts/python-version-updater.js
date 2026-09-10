"use strict";

/**
 * standard-version custom updater for pyproject.toml [project].version
 * See: https://github.com/conventional-changelog/standard-version#custom-updaters
 */

const VERSION_RE = /^version\s*=\s*["']([^"']+)["']/m;

module.exports.readVersion = function readVersion(contents) {
  const match = contents.match(VERSION_RE);
  if (!match) {
    throw new Error('Could not find project version = "x.y.z" in pyproject.toml');
  }
  return match[1];
};

module.exports.writeVersion = function writeVersion(contents, version) {
  if (!VERSION_RE.test(contents)) {
    throw new Error('Could not find project version = "x.y.z" in pyproject.toml');
  }
  return contents.replace(VERSION_RE, `version = "${version}"`);
};
