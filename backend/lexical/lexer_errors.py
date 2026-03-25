from backend.lexical.token import Token

# =================================================================================================
# LEXER ERRORS CLASS: reads source code character by character and returns a list of tokens
# =================================================================================================

class LexerErrors:

    def error(self, context=None, *, line=None, col=None):
        token_text = self.current_token_text()
        if not token_text:
            token_text = self.current_char if self.current_char is not None else "EOF"

        line = line if line is not None else self.token_start_line
        col  = col  if col  is not None else self.token_start_col

        message = f"Invalid character/s '{token_text}'"
        if context:
            message += f" — {context}"

        err_token = Token("ERROR", token_text, line, col, message)
        self.errors.append(err_token)
        return None