# backend/lexical/lexer_helpers.py
from backend.lexical.token import Token

class LexerErrors:

    def error(self, context=None, *, line=None, col=None):
        char    = self.current_char if self.current_char is not None else "EOF"
        line    = line if line is not None else self.line
        col     = col  if col  is not None else self.col - 1
        message = f"Invalid character '{char}'"
        if context:
            message += f" — {context}"

        err_token = Token("ERROR", char, line, col, message)
        self.errors.append(err_token)
        return None