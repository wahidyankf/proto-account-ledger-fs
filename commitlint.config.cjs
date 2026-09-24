// Commitlint loads CommonJS configuration here; conventional commits provide a
// shared, machine-checkable history format without custom repository rules.
module.exports = {
  extends: ["@commitlint/config-conventional"],
  rules: {
    // Footers carry OSE-Rules-Source provenance trailers whose values are
    // repository paths; a path cannot be wrapped, so footer lines are exempt
    // from the 100-character ceiling that still applies to header and body.
    "footer-max-line-length": [0],
  },
};
