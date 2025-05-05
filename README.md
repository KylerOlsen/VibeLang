# VibeLang Compiler

A simple programming language compiler that targets x86_64 Linux assembly using NASM.

## Requirements
- Python 3.6+
- NASM (Netwide Assembler)
- GCC (for linking)

## Setup
1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install NASM:
```bash
# On Ubuntu/Debian
sudo apt-get install nasm
# On Fedora
sudo dnf install nasm
```

## Usage
To compile a VibeLang program:
```bash
python compiler.py input.vibe -o output.asm
nasm -f elf64 output.asm
gcc -no-pie output.o -o output
```

## Language Features
- Basic arithmetic operations
- Variable declarations and assignments
- Print statements
- Simple control flow (if/else)
- Function definitions and calls

## Example
```vibe
fn main() {
    let x = 42;
    print(x);
}
``` 