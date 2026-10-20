import ast
import operator
import tkinter as tk

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_eval(expression: str):
    """Evaluate a math expression using only numbers and + - * / %."""

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
            return OPERATORS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in OPERATORS:
            return OPERATORS[type(node.op)](_eval(node.operand))
        raise ValueError("Invalid expression")

    tree = ast.parse(expression, mode="eval")
    return _eval(tree)


def format_result(value) -> str:
    """Show whole numbers without .0 and trim long floats."""
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:.10g}"
    return str(value)


# ---------- GUI ----------
class Calculator(tk.Tk):
    BG = "#1e1e2e"
    DISPLAY_BG = "#11111b"
    TEXT = "#cdd6f4"
    NUM_BTN = "#313244"
    OP_BTN = "#fab387"
    FUNC_BTN = "#45475a"
    EQ_BTN = "#a6e3a1"

    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.configure(bg=self.BG)
        self.resizable(False, False)

        self.expression = ""
        self.just_evaluated = False

        self._build_display()
        self._build_buttons()
        self._bind_keys()

    def _build_display(self):
        frame = tk.Frame(self, bg=self.BG)
        frame.pack(fill="x", padx=10, pady=(10, 0))

        self.history_var = tk.StringVar()
        tk.Label(
            frame, textvariable=self.history_var, anchor="e",
            font=("Segoe UI", 11), bg=self.DISPLAY_BG, fg="#7f849c",
            padx=10, pady=4,
        ).pack(fill="x")

        self.display_var = tk.StringVar(value="0")
        tk.Label(
            frame, textvariable=self.display_var, anchor="e",
            font=("Segoe UI", 28, "bold"), bg=self.DISPLAY_BG, fg=self.TEXT,
            padx=10, pady=10,
        ).pack(fill="x")

    def _build_buttons(self):
        layout = [
            ["C", "⌫", "%", "/"],
            ["7", "8", "9", "*"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["+/-", "0", ".", "="],
        ]
        grid = tk.Frame(self, bg=self.BG)
        grid.pack(padx=10, pady=10)

        for r, row in enumerate(layout):
            for c, label in enumerate(row):
                if label == "=":
                    color, fg = self.EQ_BTN, "#11111b"
                elif label in "+-*/%":
                    color, fg = self.OP_BTN, "#11111b"
                elif label in ("C", "⌫", "+/-"):
                    color, fg = self.FUNC_BTN, self.TEXT
                else:
                    color, fg = self.NUM_BTN, self.TEXT

                tk.Button(
                    grid, text=label, width=5, height=2,
                    font=("Segoe UI", 14, "bold"),
                    bg=color, fg=fg, activebackground=color,
                    relief="flat", bd=0,
                    command=lambda ch=label: self.on_press(ch),
                ).grid(row=r, column=c, padx=3, pady=3)

    def _bind_keys(self):
        self.bind("<Key>", self._on_key)
        self.bind("<Return>", lambda e: self.on_press("="))
        self.bind("<KP_Enter>", lambda e: self.on_press("="))
        self.bind("<BackSpace>", lambda e: self.on_press("⌫"))
        self.bind("<Escape>", lambda e: self.on_press("C"))

    def _on_key(self, event):
        if event.char in "0123456789.+-*/%":
            self.on_press(event.char)

    # ---------- Logic ----------
    def on_press(self, ch: str):
        if ch == "C":
            self.expression = ""
            self.history_var.set("")
            self.just_evaluated = False
        elif ch == "⌫":
            if self.just_evaluated:
                self.expression = ""
                self.just_evaluated = False
            else:
                self.expression = self.expression[:-1]
        elif ch == "=":
            self._evaluate()
            return
        elif ch == "+/-":
            self._toggle_sign()
        else:
            if self.just_evaluated and ch not in "+-*/%":
                self.expression = ""
            self.just_evaluated = False

            if ch in "+-*/%" and self.expression and self.expression[-1] in "+-*/%":
                self.expression = self.expression[:-1]
            if ch in "*/%" and not self.expression:
                return
            self.expression += ch

        self.display_var.set(self.expression or "0")


    def _toggle_sign(self):
        if not self.expression:
            return
        
        
        i = len(self.expression)
        while i > 0 and (self.expression[i - 1].isdigit() or self.expression[i - 1] == "."):
            i -= 1
        if i > 0 and self.expression[i - 1] == "-" and (i == 1 or self.expression[i - 2] in "+-*/%"):
            self.expression = self.expression[: i - 1] + self.expression[i:]
        else:
            self.expression = self.expression[:i] + "-" + self.expression[i:]

    def _evaluate(self):
        if not self.expression:
            return
        try:
            result = format_result(safe_eval(self.expression))
            self.history_var.set(self.expression + " =")
            self.expression = result
            self.display_var.set(result)
            self.just_evaluated = True
        except ZeroDivisionError:
            self._show_error("Cannot divide by 0")
        except Exception:
            self._show_error("Invalid input")

    def _show_error(self, message: str):
        self.history_var.set(self.expression)
        self.display_var.set(message)
        self.expression = ""
        self.just_evaluated = False


if __name__ == "__main__":
    Calculator().mainloop()