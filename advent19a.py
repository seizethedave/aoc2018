import advent16_ops

OPCODES = 16

ops = {op.__name__: op for op in advent16_ops.ops}

def iter_inputs():
    """
    Yields one instruction register, followed by a series of (op, (arg1, arg2, arg3)) tuples.
    """
    with open("advent19.txt", "r") as f:
        file_iter = iter(f)
        ip = int(next(file_iter).rstrip("\n")[-1])
        yield ip

        for line in f:
            op, args_str = line.rstrip("\n").split(" ", 1)
            yield op, tuple(int(a) for a in args_str.split(" "))

def interpret(instruction_register, instructions):
    register_file = [0, 0, 0, 0, 0, 0]
    instruction_pointer = 0

    while True:
        register_file[instruction_register] = instruction_pointer

        try:
            op_str, args = instructions[instruction_pointer]
        except IndexError:
            break # Halt.

        ops[op_str](register_file, *args)
        instruction_pointer = register_file[instruction_register] + 1

    return register_file

def go():
    input_stream = iter_inputs()
    reg = interpret(next(input_stream), list(input_stream))
    print reg[0]

if __name__ == "__main__":
    go()
