from parser import Program, Function, Block, VariableDeclaration, Assignment, Print, BinaryOp, Number, Identifier, If

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
            self.emit("global main")
            self.emit("")

            for func in node.functions:
                self.generate(func)

        elif isinstance(node, Function):
            self.emit(f"{node.name}:")
            self.emit("    push rbp")
            self.emit("    mov rbp, rsp")
            self.generate(node.body)
            self.emit("    mov rax, 0")  # Return 0 from main
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

        elif isinstance(node, If):
            # Generate condition
            self.generate(node.condition)
            self.emit("    test rax, rax")
            
            # Create labels
            else_label = self.new_label()
            end_label = self.new_label()
            
            # Jump to else or end if condition is false
            self.emit(f"    jz {else_label if node.else_block else end_label}")
            
            # Generate then block
            self.generate(node.then_block)
            
            if node.else_block:
                self.emit(f"    jmp {end_label}")
                self.emit(f"{else_label}:")
                self.generate(node.else_block)
            
            self.emit(f"{end_label}:")

        elif isinstance(node, BinaryOp):
            if node.op in ('&&', '||'):
                # For logical operations, we need to evaluate left operand first
                self.generate(node.left)
                self.emit("    test rax, rax")
                if node.op == '&&':
                    self.emit("    jz .false")
                else:  # ||
                    self.emit("    jnz .true")
                
                self.generate(node.right)
                self.emit("    test rax, rax")
                if node.op == '&&':
                    self.emit("    jz .false")
                    self.emit("    mov rax, 1")
                    self.emit("    jmp .end")
                    self.emit(".false:")
                    self.emit("    mov rax, 0")
                    self.emit(".end:")
                else:  # ||
                    self.emit("    jnz .true")
                    self.emit("    mov rax, 0")
                    self.emit("    jmp .end")
                    self.emit(".true:")
                    self.emit("    mov rax, 1")
                    self.emit(".end:")
            else:
                # For other operations, evaluate right operand first
                self.generate(node.right)
                self.emit("    push rax")
                self.generate(node.left)
                self.emit("    pop rbx")

                if node.op == '+':
                    self.emit("    add rax, rbx")
                elif node.op == '-':
                    self.emit("    sub rax, rbx")
                elif node.op == '*':
                    self.emit("    imul rax, rbx")
                elif node.op == '/':
                    self.emit("    cqo")
                    self.emit("    idiv rbx")
                elif node.op == '==':
                    self.emit("    cmp rax, rbx")
                    self.emit("    sete al")
                    self.emit("    movzx rax, al")
                elif node.op == '!=':
                    self.emit("    cmp rax, rbx")
                    self.emit("    setne al")
                    self.emit("    movzx rax, al")
                elif node.op == '<':
                    self.emit("    cmp rax, rbx")
                    self.emit("    setl al")
                    self.emit("    movzx rax, al")
                elif node.op == '>':
                    self.emit("    cmp rax, rbx")
                    self.emit("    setg al")
                    self.emit("    movzx rax, al")
                elif node.op == '<=':
                    self.emit("    cmp rax, rbx")
                    self.emit("    setle al")
                    self.emit("    movzx rax, al")
                elif node.op == '>=':
                    self.emit("    cmp rax, rbx")
                    self.emit("    setge al")
                    self.emit("    movzx rax, al")

        elif isinstance(node, Number):
            self.emit(f"    mov rax, {node.value}")

        elif isinstance(node, Identifier):
            self.emit(f"    mov rax, [rbp-{self.variables[node.name]}]")

    def get_code(self):
        # Add print_int function
        self.emit("print_int:")
        self.emit("    push rbp")
        self.emit("    mov rbp, rsp")
        self.emit("    sub rsp, 32")  # Reserve space for local variables
        
        # Convert number to ASCII
        self.emit("    mov rax, rdi")  # Get the number to print
        self.emit("    mov rcx, 10")   # Base 10
        self.emit("    mov rdi, rbp")
        self.emit("    sub rdi, 1")    # Point to end of buffer
        self.emit("    mov byte [rdi], 0")  # Null terminator
        
        self.emit("convert_loop:")
        self.emit("    xor rdx, rdx")  # Clear rdx for division
        self.emit("    div rcx")       # Divide by 10
        self.emit("    add dl, '0'")   # Convert to ASCII
        self.emit("    dec rdi")       # Move buffer pointer
        self.emit("    mov [rdi], dl") # Store digit
        self.emit("    test rax, rax") # Check if quotient is zero
        self.emit("    jnz convert_loop")
        
        # Calculate string length
        self.emit("    mov rsi, rdi")  # Start of string
        self.emit("    mov rdx, rbp")
        self.emit("    sub rdx, rdi")  # Length = end - start
        
        # Write to stdout
        self.emit("    mov rax, 1")    # sys_write
        self.emit("    mov rdi, 1")    # stdout
        self.emit("    syscall")
        
        # Add newline
        self.emit("    mov rax, 1")    # sys_write
        self.emit("    mov rdi, 1")    # stdout
        self.emit("    mov rsi, newline")
        self.emit("    mov rdx, 1")    # length
        self.emit("    syscall")
        
        self.emit("    add rsp, 32")   # Restore stack
        self.emit("    pop rbp")
        self.emit("    ret")
        
        # Add data section for newline
        self.emit("section .data")
        self.emit("newline: db 10")    # ASCII newline

        return "\n".join(self.output) 