
import readchar

class BFEvaluator(object):
  def __init__(self):
    super(BFEvaluator, self).__init__()
    self.memory = bytearray([0 for i in range(1024)])
    self.pc = 0
    self.jmp_map = {}

  def _pre_evaluate(self, program):
    jmp = []
    for idx, tok in enumerate(program):
      if tok == "[":
        jmp.append(idx)
      elif tok == "]":
        if len(jmp) == 0:
          return False

        start = jmp.pop()
        self.jmp_map[start] = idx
        self.jmp_map[idx] = start        

    return len(jmp) == 0

  def evaluate(self, program):
    if not self._pre_evaluate(program):
      print "There was an interpreter error"
      return (False, '')

    output = ''
    idx = 0
    while idx < len(program):
      tok = program[idx]
      if tok == ">":
        self.pc = self.pc + 1
      elif tok == "<":
        self.pc = self.pc - 1
      elif tok == "+":
        self.memory[self.pc] += 1
      elif tok == "-":
        self.memory[self.pc] -= 1
      elif tok == ".":
        output = output + chr(self.memory[self.pc])
      elif tok == ",":
        return (False, '')
      elif tok == "[":
        if self.memory[self.pc] == 0:
          idx = self.jmp_map[idx]
      elif tok == "]":
        if self.memory[self.pc] != 0:
          idx = self.jmp_map[idx]

      idx = idx + 1

    return (True, output)
