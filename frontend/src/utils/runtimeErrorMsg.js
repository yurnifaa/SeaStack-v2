// Runtime exception message simplifier

export function simplifyRuntimeMessage(msg) {
  if (!msg) return "An error occurred during program execution.";
  const m = msg.toLowerCase();
  if (m.includes('coin input exceeds 16 digits'))
    return "COIN input exceeds 16 digits.";
  if (m.includes('dime input exceeds 8 digits'))
    return "DIME input exceeds 8 digits.";
  if (m.includes('division by zero') || m.includes('zerodivisionerror'))
    return "Cannot divide by zero.";
  if (m.includes('invalid literal for int') || m.includes('base 10') || (m.includes('invalid') && m.includes('int')))
    return "COIN was expected but the value entered cannot be converted.";
  if ((m.includes('could not convert') && m.includes('float')) || (m.includes('valueerror') && m.includes('float')))
    return "DIME was expected but the value entered cannot be converted.";
  if (m.includes('expected aye or nay'))
    return "a BOOL value was expected.";
  if (m.includes('list index out of range') || m.includes('indexerror'))
    return "Array index is out of bounds.";
  if (m.includes('keyerror'))
    return "Struct member not found. A field was accessed that does not exist in the struct.";
  if (m.includes('recursionerror') || m.includes('maximum recursion') || m.includes('stack overflow'))
    return "too many nested function calls.";
  if (m.includes('valueerror'))
    return "Invalid value encountered during execution.";
  if (m.includes('typeerror'))
    return "A value of the wrong type was used in an operation.";
  return msg;
}
