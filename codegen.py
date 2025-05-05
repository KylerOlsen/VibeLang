from parser import Program, Function, Block, VariableDeclaration, Assignment, Print, BinaryOp, Number, Identifier

class CodeGenerator:
    def __init__(self):
        self.output = []
        self.label_count = 0
        self.variables = {}
        self.stack_offset = 0

    def new_label(self):
        self.label_count += 1
        return f"label_{self.label_count}"

    def emit(self, code):
        self.output.append(code)

    def generate(self, node):
        if isinstance(node, Program):
            self.emit("section .text")
            self.emit("global _start")
            self.emit("")
            self.emit("_start:")
            self.emit("    call main")
            self.emit("    mov rax, 60")  # sys_exit
            self.emit("    mov rdi, 0")   # exit code
            self.emit("    syscall")
            self.emit("")

            for func in node.functions:
                self.generate(func)

        elif isinstance(node, Function):
            self.emit(f"{node.name}:")
            self.emit("    push rbp")
            self.emit("    mov rbp, rsp")
            self.generate(node.body)
            self.emit("    pop rbp")
            self.emit("    ret")
            self.emit("")

        elif isinstance(node, Block):
            for stmt in node.statements:
                self.generate(stmt)

        elif isinstance(node, VariableDeclaration):
            self.variables[node.name] = self.stack_offset
            self.stack_offset += 8
            self.generate(node.value)
            self.emit(f"    mov [rbp-{self.variables[node.name]}], rax")

        elif isinstance(node, Assignment):
            self.generate(node.value)
            self.emit(f"    mov [rbp-{self.variables[node.name]}], rax")

        elif isinstance(node, Print):
            self.generate(node.value)
            self.emit("    mov rdi, rax")
            self.emit("    call print_int")

        elif isinstance(node, BinaryOp):
            self.generate(node.left)
            self.emit("    push rax")
            self.generate(node.right)
            self.emit("    pop rbx")

            if node.op == '+':
                self.emit("    add rax, rbx")
            elif node.op == '-':
                self.emit("    sub rbx, rax")
                self.emit("    mov rax, rbx")
            elif node.op == '*':
                self.emit("    imul rax, rbx")
            elif node.op == '/':
                self.emit("    xchg rax, rbx")
                self.emit("    cqo")
                self.emit("    idiv rbx")
            elif node.op == '==':
                self.emit("    cmp rbx, rax")
                self.emit("    sete al")
                self.emit("    movzx rax, al")
            elif node.op == '!=':
                self.emit("    cmp rbx, rax")
                self.emit("    setne al")
                self.emit("    movzx rax, al")
            elif node.op == '<':
                self.emit("    cmp rbx, rax")
                self.emit("    setl al")
                self.emit("    movzx rax, al")
            elif node.op == '>':
                self.emit("    cmp rbx, rax")
                self.emit("    setg al")
                self.emit("    movzx rax, al")
            elif node.op == '<=':
                self.emit("    cmp rbx, rax")
                self.emit("    setle al")
                self.emit("    movzx rax, al")
            elif node.op == '>=':
                self.emit("    cmp rbx, rax")
                self.emit("    setge al")
                self.emit("    movzx rax, al")

        elif isinstance(node, Number):
            self.emit(f"    mov rax, {node.value}")

        elif isinstance(node, Identifier):
            self.emit(f"    mov rax, [rbp-{self.variables[node.name]}]")

    def get_code(self):
        # Add print_int function
        self.emit("print_int:")
        self.emit("    mov rsi, rdi")
        self.emit("    mov rdi, 1")  # stdout
        self.emit("    mov rdx, 1")  # length
        self.emit("    mov rax, 1")  # sys_write
        self.emit("    syscall")
        self.emit("    ret")

        return "\n".join(self.output) 