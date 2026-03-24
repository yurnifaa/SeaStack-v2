# lexer_handlers/sp_lits_hndlr.py
import string
from backend.lexical.token import Token
from backend.lexical.handlers.delimiters import Delimiters
from backend.lexical.lexer_errors import LexerErrors

# =========================================================================================
# SCROLL and PARCH TD: States 285 - 294
# =========================================================================================

class Texts(LexerErrors):

    # --- Utility Functions ---
    def _get_parch_delims(self):
        return Delimiters._get_delimiters()["PARCH_DELIM"]

    def _get_scroll_body_allowed(self):
        # Allow everything except ", \, and Newline
        delims = Delimiters._get_delimiters()
        return delims["ASCII"] - set("\"\\\n\r")

    def _get_scroll_delims(self):
        return Delimiters._get_delimiters()["SCR_DELIM"]

    # --- Error Utility ---
    def _error_token(self, message, current_text=""):
        self.error(message, col=max(1, self.col - 1), text=current_text)
        return []

    # =========================================================================
    # PARCH LITERAL (Single Character) - States 285 to 289
    # =========================================================================

    # State 285: Opening Quote '
    def p285(self):
        if self.current_char == "'":
            self.advance()
            return self.p286()
        return None

    # State 286: The Content (Char or Backslash)
    def p286(self):
        # Check Empty ('')
        if self.current_char == "'":
            return self._error_token("Invalid PARCH Literal.")

        # Check Newline
        if self.current_char == '\n':
            return self._error_token("Invalid PARCH Literal.")

        # Check Escape Sequence Start
        if self.current_char == '\\':
            self.advance()
            return self.p287()  # Go to Escape Handler

        # Standard Character
        if self.current_char is not None:
            self.advance()
            return self.p288()  # Go to Closing Quote Check

        # EOF
        return self._error_token("Invalid PARCH Literal.")

    # State 287: PARCH Escape Sequence (s, n, t, 0, \)
    def p287(self):
        # Strict allowed list: s, n, t, 0, \
        valid_escapes = ['s', 'n', 't', '0', '\\']

        if self.current_char in valid_escapes:
            self.advance()
            return self.p288()  # Go to Closing Quote Check

        # Error 1: Invalid Escape
        # We fail immediately so the handler stops.
        return self._error_token("Invalid Character.")

    # State 288: Closing Quote '
    def p288(self):
        if self.current_char == "'":
            self.advance()
            return self.p289()  # Go to Delimiter Check

        # If we have chars but no closing quote
        return self._error_token("Invalid PARCH Literal.")

    # State 289: Delimiter Check & Accept
    def p289(self):
        if self._comp_delims(self._get_parch_delims()):
            return [Token("PARCH-lit", self.current_token_text(), self.line, self.col - 1)]

        err_token = Token(
            "ERROR",
            self.current_token_text(),
            self.line,
            self.col - 1,
            "Invalid PARCH Literal."
        )
        self.errors.append(err_token)
        return []

    # =========================================================================
    # SCROLL LITERAL (Double Quoted String) - States 290 to 294
    # =========================================================================

    # State 290: Opening Quote "
    def s290(self):
        if self.current_char == '"':
            self.advance()
            return self.s291(current_text='"', start_line=self.line, start_col=self.col-1)
        return None

    # State 291: SCROLL Body Loop
    def s291(self, current_text, start_line, start_col):
        while self.current_char is not None:

            # Closing Quote -> Transition to End
            if self.current_char == '"':
                # Check for Empty SCROLL Literal ("")
                if current_text == '"':
                    return self._error_token("Invalid SCROLL Literal.")

                self.advance()
                return self.s293(current_text + '"', start_line, start_col)

            # Escape Sequence Start -> Transition to s292
            if self.current_char == '\\':
                self.advance()
                return self.s292(current_text + '\\', start_line, start_col)

            # Newline -> Error
            if self.current_char == '\n':
                return self._error_token("Invalid SCROLL Literal.")

            # Valid Body Character
            if self._comp_delims(self._get_scroll_body_allowed()):
                current_text += self.current_char
                self.advance()
                continue

            # Invalid Character (Unprintable or disallowed)
            self.advance()
            return self._error_token("Invalid SCROLL Literal.")

        # EOF
        return self._error_token("Invalid SCROLL Literal.")

    # State 292: SCROLL Escape Sequence (d, n, t, 0, \)
    def s292(self, current_text, start_line, start_col):
        # Strict allowed list: d, n, t, 0, \
        valid_escapes = ['d', 'n', 't', '0', '\\']

        if self.current_char in valid_escapes:
            char = self.current_char
            self.advance()
            # Return to Body Loop (s291)
            return self.s291(current_text + char, start_line, start_col)

        return self._error_token("Invalid SCROLL Literal.")

    # State 293: Delimiter Check
    def s293(self, current_text, start_line, start_col):
        if self._comp_delims(self._get_scroll_delims()):
            return self.s294(current_text, start_line, start_col)

        err_token = Token(
            "ERROR",
            current_text,
            start_line,
            start_col,
            "Invalid SCROLL literal."
        )
        self.errors.append(err_token)
        return []

    # State 294: Accept
    def s294(self, current_text, start_line, start_col):
        return [Token("SCROLL-lit", current_text, start_line, start_col)]
