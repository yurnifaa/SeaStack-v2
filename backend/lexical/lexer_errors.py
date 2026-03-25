# backend/lexical/lexer_helpers.py
from backend.lexical.token import Token

class LexerErrors:

    def error(self, context=None, *, line=None, col=None):
        # Use the full accumulated token text as the error value.
        # Falls back to the bare current char only when nothing has been
        # buffered yet (e.g. a completely unexpected first character).
        token_text = self.current_token_text()
        if not token_text:
            token_text = self.current_char if self.current_char is not None else "EOF"

        # Default line/col to token_start so the error points at the
        # BEGINNING of the bad sequence, not at the offending character.
        line = line if line is not None else self.token_start_line
        col  = col  if col  is not None else self.token_start_col

        message = f"Invalid character/s '{token_text}'"
        if context:
            message += f" — {context}"

        err_token = Token("ERROR", token_text, line, col, message)
        self.errors.append(err_token)
        return None