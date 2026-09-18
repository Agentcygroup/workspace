class VMError(Exception):
    pass

HALTED = "halted"
RUNNING = "running"

class Machine:
    def __init__(self, memory_size=256, register_count=8):
        if memory_size <= 0 or register_count <= 0:
            raise VMError("memory and register count must be positive")
        self.mem = [0] * memory_size
        self.reg = [0] * register_count
        self.pc = 0
        self.flag_z = False
        self.flag_n = False
        self.status = RUNNING
        self.opcode_count = 0

    def load(self, program):
        for i, word in enumerate(program):
            if i >= len(self.mem):
                raise VMError("program too large")
            if not 0 <= word <= 0xFFFFFFFF:
                raise VMError("word out of range at " + str(i))
            self.mem[i] = word
        self.pc = 0
        self.status = RUNNING

    def step(self):
        if self.status == HALTED:
            raise VMError("machine halted")
        if self.pc < 0 or self.pc >= len(self.mem):
            raise VMError("pc out of range")
        op = self.mem[self.pc]
        self.opcode_count += 1
        return self._execute(op)

    def run(self, max_steps=100000):
        steps = 0
        while self.status == RUNNING:
            self.step()
            steps += 1
            if steps > max_steps:
                raise VMError("step limit exceeded")
        return steps

    def _read_operands(self, n):
        args = []
        for i in range(n):
            idx = self.pc + 1 + i
            if idx >= len(self.mem):
                raise VMError("operand out of range")
            args.append(self.mem[idx])
        return args

    def _set_flags(self, value):
        value &= 0xFFFFFFFF
        self.flag_z = (value == 0)
        self.flag_n = (value & 0x80000000) != 0

    def _execute(self, op):
        if op == 0:
            self.pc += 1
            return "NOP"
        if op == 1:
            dst, src = self._read_operands(2)
            self._check_reg(dst)
            if 0 <= src < len(self.reg):
                self.reg[dst] = self.reg[src]
            else:
                self.reg[dst] = self.mem[src] if 0 <= src < len(self.mem) else 0
            self._set_flags(self.reg[dst])
            self.pc += 3
            return "LOAD"
        if op == 2:
            dst, src = self._read_operands(2)
            self._check_reg(dst)
            if 0 <= src < len(self.mem):
                self.mem[src] = self.reg[dst] & 0xFFFFFFFF
            else:
                raise VMError("STORE target out of range")
            self.pc += 3
            return "STORE"
        if op == 3:
            dst, a, b = self._read_operands(3)
            self._check_reg(dst); self._check_reg(a); self._check_reg(b)
            self.reg[dst] = (self.reg[a] + self.reg[b]) & 0xFFFFFFFF
            self._set_flags(self.reg[dst])
            self.pc += 4
            return "ADD"
        if op == 4:
            dst, a, b = self._read_operands(3)
            self._check_reg(dst); self._check_reg(a); self._check_reg(b)
            self.reg[dst] = (self.reg[a] - self.reg[b]) & 0xFFFFFFFF
            self._set_flags(self.reg[dst])
            self.pc += 4
            return "SUB"
        if op == 5:
            a, b = self._read_operands(2)
            self._check_reg(a); self._check_reg(b)
            diff = (self.reg[a] - self.reg[b]) & 0xFFFFFFFF
            self._set_flags(diff)
            self.pc += 3
            return "CMP"
        if op == 6:
            target, = self._read_operands(1)
            if target >= len(self.mem):
                raise VMError("JMP out of range")
            self.pc = target
            return "JMP"
        if op == 7:
            target, = self._read_operands(1)
            if self.flag_z:
                if target >= len(self.mem):
                    raise VMError("JE out of range")
                self.pc = target
            else:
                self.pc += 2
            return "JE"
        if op == 8:
            target, = self._read_operands(1)
            if not self.flag_z:
                if target >= len(self.mem):
                    raise VMError("JNE out of range")
                self.pc = target
            else:
                self.pc += 2
            return "JNE"
        if op == 9:
            target, = self._read_operands(1)
            if target >= len(self.mem):
                raise VMError("CALL out of range")
            self.reg[7] = self.pc + 2
            self.pc = target
            return "CALL"
        if op == 10:
            ret = self.reg[7]
            if ret < 0 or ret >= len(self.mem):
                raise VMError("RET to invalid address")
            self.pc = ret
            return "RET"
        if op == 11:
            self.status = HALTED
            self.pc += 1
            return "HLT"
        raise VMError("unknown opcode: " + str(op))

    def _check_reg(self, r):
        if not 0 <= r < len(self.reg):
            raise VMError("register out of range: " + str(r))
