"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PUSH = 0b01000101
POP  = 0b01000110
ADD  = 0b10100000
CALL = 0b01010000
RET  = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

SP = 7

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.branchtable = {}
        self.branchtable[LDI] = self.handle_LDI
        self.branchtable[PRN] = self.handle_PRN
        self.branchtable[MUL] = self.handle_MUL
        self.branchtable[PUSH] = self.handle_PUSH
        self.branchtable[POP] = self.handle_POP
        self.branchtable[ADD] = self.handle_ADD
        self.branchtable[CALL] = self.handle_CALL
        self.branchtable[RET] = self.handle_RET
        self.branchtable[CMP] = self.handle_CMP
        self.branchtable[JMP] = self.handle_JMP
        self.branchtable[JEQ] = self.handle_JEQ
        self.branchtable[JNE] = self.handle_JNE

        self.pc = 0
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[SP] = 0xF4
        self.fl = 0b00000000

    def load(self, filename):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

        try:
            with open(filename) as f:
                for line in f:
                    comment_split = line.split("#")
                    num = comment_split[0].strip()
                    if num == '':
                        continue
                    instruction = int(num, 2)
                    self.ram[address] = instruction
                    address += 1

            print(self.ram)

        except FileNotFoundError:
            print("File not found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            val1 = self.reg[reg_a]
            val2 = self.reg[reg_b]
            if val1 == val2:
                self.fl = 0b00000001
            elif val1 < val2:
                self.fl = 0b00000100
            elif val1 > val2:
                self.fl = 0b00000010
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mdr, mar):
        self.ram[mar] = mdr

    def handle_LDI(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b
        self.pc +=3

    def handle_PRN(self, operand_a, operand_b):
        print(self.reg[operand_a])
        self.pc +=2

    def handle_MUL(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)
        self.pc += 3

    def handle_PUSH(self, operand_a, operand_b):
        self.reg[SP] -= 1
        self.ram_write(self.reg[operand_a], self.reg[SP])
        self.pc += 2

    def handle_POP(self, operand_a, operand_b):
        self.reg[operand_a] = self.ram[self.reg[SP]]
        self.reg[SP] += 1
        self.pc += 2

    def handle_ADD(self, operand_a, operand_b):
        self.alu("ADD", operand_a, operand_b)
        self.pc += 3

    def handle_CALL(self, operand_a, operand_b):
        self.reg[SP] -= 1
        self.ram[self.reg[SP]] = self.pc + 2 
        self.pc = self.reg[operand_a]

    def handle_RET(self, operand_a, operand_b):
        self.pc = self.ram[self.reg[SP]]
        self.reg[SP] += 1

    def handle_CMP(self, operand_a, operand_b):
        self.alu("CMP", operand_a, operand_b)
        self.pc += 3

    def handle_JMP(self, operand_a, operand_b):
        self.pc = self.reg[operand_a]

    def handle_JEQ(self, operand_a, operand_b):
        if self.fl == 1:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2

    def handle_JNE(self, operand_a, operand_b):
        if self.fl != 1:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2
        
    def run(self):
        """Run the CPU."""
        running = True
        while running:
            ir = self.ram[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if ir == HLT:
                running = False
                sys.exit(1)

            self.branchtable[ir](operand_a, operand_b)

            # elif ir == LDI:
            #     self.reg[operand_a] = operand_b
            #     self.pc += 3

            # elif ir == PRN:
            #     print(self.reg[operand_a])
            #     self.pc += 2

            # elif ir == MUL:
            #     self.alu("MUL", operand_a, operand_b)
            #     self.pc += 3

            # else:
            #     print(f"Unknown command: {ir}")
            #     sys.exit(1)