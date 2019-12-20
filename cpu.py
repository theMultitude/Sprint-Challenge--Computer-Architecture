"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):

        self.registers = [0] * 8
        self.ram = [0] * 256

        self.spl = -1
        self.registers[self.spl] = 0xF4
        self.halt = False
        self.pc = 0
        self.eq = None

        self.flag = {}

        self.OPCODES = {0b10000010: 'LDI',
                        0b01000111: 'PRN',
                        0b00000001: 'HLT',
                        0b10100010: 'MUL',
                        0b01000110: 'POP',
                        0b01000101: 'PUSH',
                        0b10000100: 'ST',
                        0b10100111: 'CMP',
                        0b01010100: 'JMP',
                        0b01010110: 'JNE',
                        0b01010101: 'JEQ',
        }

    def load(self, filename:str):
        """Load a program into memory."""

        try:
            with open(filename, 'r') as f:
                address = 0
                for line in f:
                    line = line.split('#')[0]
                    line = line.strip()

                    if line == '':
                        continue

                    value = int(line, 2)

                    self.ram[address] = value
                    address += 1
        except FileNotFoundError as e:
            print(e)
            sys.exit()


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.registers[reg_a] += self.registers[reg_b]

        elif op == "MUL":
            self.registers[reg_a] *= self.registers[reg_b]

        elif op == 'CMP':
            if self.registers[reg_a] == self.registers[reg_b]:
                self.flag['E'] = 1
            else:
                self.flag['E'] = 0
            if self.registers[reg_a] > self.registers[reg_b]:
                self.flag['G'] = 1
            else:
                self.flag['G'] = 0
            if self.registers[reg_a] < self.registers[reg_b]:
                self.flag['L'] = 1
            else:
                self.flag['L'] = 0

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

    def run(self):
        """Run the CPU."""
        running = True
        while running:
            self.ir = self.ram[self.pc]

            try:
                op = self.OPCODES[self.ir]

                if op == 'LDI':
                    reg = self.ram[self.pc+1]
                    val = self.ram[self.pc+2]
                    self.registers[reg] = val
                    self.pc += 3

                elif op == 'PRN':
                    reg = self.ram[self.pc + 1]
                    val = self.registers[reg]
                    print(f"hex val: {val:x}\tdec val: {val}\tbin val: {val:b}")
                    self.pc += 2

                elif op == 'ADD' or op == 'MUL' or op == 'CMP':
                    reg_a = self.ram[self.pc+1]
                    reg_b = self.ram[self.pc+2]
                    self.alu(op, reg_a, reg_b)
                    self.pc += 3

                elif op == 'PUSH':
                    reg = self.ram[self.pc + 1]
                    val = self.reg[reg]

                    self.ram[self.registers[self.spl]] = val

                    self.registers[self.spl] -= 1
                    self.pc += 2

                elif op == 'POP':
                    reg = self.ram[self.pc + 1]
                    val = self.ram[self.reg[self.spl]]

                    self.registers[reg] = val

                    self.registers[self.spl] += 1
                    self.pc += 2

                elif op == 'JMP':
                    reg = self.ram[self.pc + 1]
                    val = self.registers[reg]
                    self.pc = val

                elif op == 'JEQ':
                    if self.flag['E'] == 1:
                        reg = self.ram[self.pc + 1]
                        val = self.registers[reg]
                        self.pc = val
                    else:
                        self.pc += 2

                elif op == 'JNE':
                    if self.flag['E'] == 0:
                        reg = self.ram[self.pc + 1]
                        val = self.registers[reg]
                        self.pc = val
                    else:
                        self.pc += 2

                elif op == 'HLT':
                    running = False

            except KeyError as e:
                print(f"unknown command {self.ir}")
                self.pc += 1

    def ram_read(self, location):
        return self.ram[location]

    def ram_write(self, location, value):
        self.ram[location] = value
