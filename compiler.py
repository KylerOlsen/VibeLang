import sys
import argparse
from lexer import lexer
from parser import parser
from codegen import CodeGenerator

def compile_file(input_file, output_file):
    try:
        with open(input_file, 'r') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: Could not open file '{input_file}'")
        sys.exit(1)

    # Lex and parse the source code
    lexer.input(source)
    ast = parser.parse(source, lexer=lexer)

    # Generate assembly code
    generator = CodeGenerator()
    generator.generate(ast)
    assembly = generator.get_code()

    # Write the assembly code to the output file
    try:
        with open(output_file, 'w') as f:
            f.write(assembly)
    except IOError:
        print(f"Error: Could not write to file '{output_file}'")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Compile VibeLang source code to NASM assembly')
    parser.add_argument('input', help='Input VibeLang source file')
    parser.add_argument('-o', '--output', help='Output assembly file', default='output.asm')
    args = parser.parse_args()

    compile_file(args.input, args.output)
    print(f"Compilation successful. Assembly code written to {args.output}")

if __name__ == '__main__':
    main() 