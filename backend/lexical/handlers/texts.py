import string
from backend.lexical.token import Token
from backend.lexical.handlers.delimiters import Delimiters
from backend.lexical.lexer_errors import LexerErrors

# =========================================================================================
# SCROLL and PARCH: States 285 - 294
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
            return self.error()

        # Check Newline
        if self.current_char == '\n':
            return self.error()

        # Check Escape Sequence Start
        if self.current_char == '\\':
            self.advance()
            return self.p287()  # Go to Escape Handler

        # Standard Character
        if self.current_char is not None:
            self.advance()
            return self.p288()  # Go to Closing Quote Check

        # EOF
        return self.error()

    # State 287: PARCH Escape Sequence (s, n, t, 0, \)
    def p287(self):
        # Strict allowed list: s, n, t, 0, \
        valid_escapes = ['s', 'n', 't', '0', '\\']

        if self.current_char in valid_escapes:
            self.advance()
            return self.p288()  # Go to Closing Quote Check

        # Error 1: Invalid Escape
        # We fail immediately so the handler stops.
        return self.error()

    # State 288: Closing Quote '
    def p288(self):
        if self.current_char == "'":
            self.advance()
            return self.p289()  # Go to Delimiter Check

        # If we have chars but no closing quote
        return self.error()

    # State 289: Delimiter Check & Accept
    def p289(self):
        if self._comp_delims(self._get_parch_delims()):
            return Token("PARCH-lit", self.current_token_text(), self.line, self.col - 1)

        return self.error()

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
                    return self.error()

                self.advance()
                return self.s293(current_text + '"', start_line, start_col)

            # Escape Sequence Start -> Transition to s292
            if self.current_char == '\\':
                self.advance()
                return self.s292(current_text + '\\', start_line, start_col)

            # Newline -> Error
            if self.current_char == '\n':
                return self.error()

            # Valid Body Character
            if self._comp_delims(self._get_scroll_body_allowed()):
                current_text += self.current_char
                self.advance()
                continue

            # Invalid Character (Unprintable or disallowed)
            self.advance()
            return self.error()

        # EOF
        return self.error()

    # State 292: SCROLL Escape Sequence (d, n, t, 0, \)
    def s292(self, current_text, start_line, start_col):
        # Strict allowed list: d, n, t, 0, \
        valid_escapes = ['d', 'n', 't', '0', '\\']

        if self.current_char in valid_escapes:
            char = self.current_char
            self.advance()
            # Return to Body Loop (s291)
            return self.s291(current_text + char, start_line, start_col)

        return self.error()

    # State 293: Delimiter Check
    def s293(self, current_text, start_line, start_col):
        if self._comp_delims(self._get_scroll_delims()):
            return self.s294(current_text, start_line, start_col)

        return self.error()

    # State 294: Accept
    def s294(self, current_text, start_line, start_col):
        return Token("SCROLL-lit", current_text, start_line, start_col)
