// Runtime message passthrough — error messages are handled by the backend.
// This only sanitizes any Python keywords that may slip through edge cases.

export function simplifyRuntimeMessage(msg) {
  if (!msg) return "An error occurred during program execution.";
  return msg
    .replace(/\bbreak\b/gi, 'LAND!!')
    .replace(/\bcontinue\b/gi, 'SAIL!!')
    .replace(/\breturn\b/gi, 'BACK');
}
