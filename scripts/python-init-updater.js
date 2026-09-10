"use strict";

/**
 * standard-version custom updater for zen/__init__.py __version__
 * See: https://github.com/conventional-changelog/standard-version#custom-updaters
 */

const VERSION_RE = /^__version__\s*=\s*["']([^"']+)["']/m;

module.exports.readVersion = function readVersion(contents) {
  const match = contents.match(VERSION_RE);
  if (!match) {
    throw new Error('Could not find __version__ = "x.y.z" in zen/__init__.py');
  }
  return match[1];
};

module.exports.writeVersion = function writeVersion(contents, version) {
  if (!VERSION_RE.test(contents)) {
    throw new Error('Could not find __version__ = "x.y.z" in zen/__init__.py');
  }
  return contents.replace(VERSION_RE, `__version__ = "${version}"`);
};
