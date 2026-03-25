// Runtime exception message

export function simplifyRuntimeMessage(msg) {
  if (!msg) return "An error occurred during program execution.";
  const m = msg.toLowerCase();

  // --- Input digit limits ---
  if (m.includes('coin input exceeds 16 digits'))
    return "COIN input exceeds 16 digits.";
  if (m.includes('dime input exceeds 8 digits'))
    return "DIME input exceeds 8 digits.";

  // --- Division by zero ---
  if (m.includes('division by zero') || m.includes('zerodivisionerror'))
    return "Cannot divide by zero.";

  // --- Type conversion / value errors ---
  if (m.includes('invalid literal for int') || m.includes('base 10') || (m.includes('invalid') && m.includes('int')))
    return "Expected a COIN but got an different value.";
  if ((m.includes('could not convert') && m.includes('float')) || (m.includes('valueerror') && m.includes('float')))
    return "Expected a DIME but got an different value.";
  if (m.includes('expected aye or nay'))
    return "Expected a BOOL (AYE or NAY).";

  // --- Null / None dereference ---
  if (m.includes('nonetype') || (m.includes('attributeerror') && m.includes('none')))
    return "Accessed a value that has not been set (null).";

  // --- Index out of bounds ---
  if (m.includes('list index out of range') || m.includes('indexerror'))
    return "Array index is out of bounds.";

  // --- Struct key not found ---
  if (m.includes('keyerror'))
    return "Struct field does not exist.";

  // --- Recursion / stack overflow ---
  if (m.includes('recursionerror') || m.includes('maximum recursion') || m.includes('stack overflow'))
    return "Too many nested function calls (infinite recursion?).";

  // --- Memory ---
  if (m.includes('memoryerror') || m.includes('out of memory'))
    return "Program ran out of memory.";

  // --- Overflow ---
  if (m.includes('overflowerror'))
    return "Number is too large to process.";

  // --- Name / attribute errors ---
  if (m.includes('nameerror'))
    return "Variable or function is not defined.";
  if (m.includes('attributeerror'))
    return "Accessed an attribute that does not exist.";

  // --- Control flow misuse ---
  if (m.includes("'break' outside loop") || (m.includes('break') && m.includes('outside')))
    return "LAND!! can only be used inside a loop or CHART block.";
  if (m.includes("'continue' outside loop") || (m.includes('continue') && m.includes('outside')))
    return "SAIL!! can only be used inside a loop.";
  if (m.includes("'return' outside function") || (m.includes('return') && m.includes('outside')))
    return "BACK can only be used inside a function.";

  // --- General value / type errors ---
  if (m.includes('valueerror'))
    return "Invalid value encountered during execution.";
  if (m.includes('typeerror'))
    return "A value of the wrong type was used in an operation.";

  return msg
    .replace(/\bbreak\b/gi, 'LAND!!')
    .replace(/\bcontinue\b/gi, 'SAIL!!')
    .replace(/\breturn\b/gi, 'BACK');
}
