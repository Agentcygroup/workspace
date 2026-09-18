import pytest
from isa_vm import Machine, VMError, HALTED

def test_nop_hlt():
    m = Machine()
    m.load([0, 11])
    m.run()
    assert m.status == HALTED
    assert m.opcode_count == 2

def test_add():
    m = Machine()
    m.load([3, 0, 1, 2, 11])
    m.reg[1] = 5
    m.reg[2] = 7
    m.run()
    assert m.reg[0] == 12

def test_sub_flags():
    m = Machine()
    m.load([4, 0, 1, 2, 11])
    m.reg[1] = 10
    m.reg[2] = 10
    m.run()
    assert m.reg[0] == 0
    assert m.flag_z is True

def test_jmp():
    m = Machine()
    m.load([6, 4, 0, 0, 11])
    m.run()
    assert m.opcode_count == 2

def test_je_taken():
    m = Machine()
    m.load([5, 1, 2, 7, 6, 0, 0, 11])
    m.reg[1] = 3
    m.reg[2] = 3
    m.run()
    assert m.status == HALTED

def test_call_ret():
    m = Machine()
    m.load([9, 5, 0, 0, 0, 11])
    m.run()
    assert m.status == HALTED
    assert m.reg[7] == 2

def test_unknown_opcode():
    m = Machine()
    m.load([999])
    with pytest.raises(VMError):
        m.step()

def test_load_store_roundtrip():
    m = Machine()
    m.reg[1] = 42
    m.mem[2] = 0
    m.load([2, 1, 2, 11])
    m.run()
    assert m.mem[2] == 42

def test_step_limit():
    m = Machine()
    m.load([6, 0])
    with pytest.raises(VMError):
        m.run(max_steps=10)

def test_memory_bounds():
    m = Machine(memory_size=16)
    with pytest.raises(VMError):
        m.load([0] * 32)
