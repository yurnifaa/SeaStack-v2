# lexer_handlers/comment_handler.py
from backend.lexical.token import Token
from backend.lexical.lexer_errors import LexerErrors

class Comments(LexerErrors):

    # =========================================================================
    # ENTRY POINT (State 295)
    # =========================================================================
    def cm295(self):
        # State 295: Expects '~'
        if self.current_char == '~':
            self.advance()
            return self.cm296()
        return None

    # =========================================================================
    # STATE 296: Decision Point (Single vs Multi)
    # =========================================================================
    def cm296(self):
        char = self.current_char

        # Path 3: ASCII except newline and ~ -> State 297 (Single Line Body)
        # Note: If we see '~' here, it's technically allowed in single line text
        # unless rules forbid it, but usually single line consumes everything until \n.
        if char is not None:
            return self.cm297()

        # Path 2: newline -> State 298 (Empty Single Line Accept)
        if char == '\n':
            return self.cm298()
        
        # Path 1: '(' -> State 299 (Start Multi-line)
        if char == '(':
            return self.cm299()
        
        return self.error(line=self.token_start_line, col=self.token_start_col)

    # =========================================================================
    # STATE 297: Single-Line Body Loop
    # =========================================================================
    def cm297(self):
        self.advance()  # Consume previous char

        # Self-Loop: Consume everything until newline
        while self.current_char is not None and self.current_char != '\n':
            self.advance()

        # Transition: newline -> 298 (Accept)
        if self.current_char == '\n':
            return self.cm298()

        return self.error(line=self.token_start_line, col=self.token_start_col)

    # =========================================================================
    # STATE 298: Single-Line Final (Accepting)
    # =========================================================================
    def cm298(self):
        self.advance()  # Consume the newline
        return Token(
            "single-comment",
            self.current_token_text(),
            self.token_start_line,
            self.token_start_col
        )

    # =========================================================================
    # STATE 299: Multi-Line Start (After '~)(')
    # =========================================================================
    def cm299(self):
        self.advance()  # Consume '('

        char = self.current_char

        # Check empty multi-line cases or straight to body
        if char is not None:
            return self.cm300()

        return self.error(line=self.token_start_line, col=self.token_start_col)

    # =========================================================================
    # STATE 300: Multi-Line Body Loop
    # =========================================================================
    def cm300(self):
        # Loop until we see ')'
        while self.current_char is not None and self.current_char != ')':
            self.advance()

        # Transition: ) -> 301
        if self.current_char == ')':
            return self.cm301()

        return self.error(line=self.token_start_line, col=self.token_start_col)

    # =========================================================================
    # STATE 301: Check Closing Tilde (After ')')
    # =========================================================================
    def cm301(self):
        self.advance()  # Consume ')'

        char = self.current_char

        # Transition: ~ -> 302 (Accept)
        if char == '~':
            return self.cm302()

        # False alarm (e.g., "( text ) more text" )
        # Go back to body loop
        if char is not None:
            return self.cm300()

        return self.error(line=self.token_start_line, col=self.token_start_col)

    # =========================================================================
    # STATE 302: Multi-Line Final (Accepting)
    # =========================================================================
    def cm302(self):
        self.advance()  # Consume '~'

        return Token(
            "multi-comment",
            self.current_token_text(),
            self.token_start_line,
            self.token_start_col
        )
