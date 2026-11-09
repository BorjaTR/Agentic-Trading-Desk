"""stub for the red run: the pipeline's names with no step bodies"""
STEPS = [(1, 'INPUT', 'own')]
class P:
    def __init__(self, f): self.f = f
    def done(self, n): return None
def init(folder, inp, settings):
    import os; os.makedirs(folder, exist_ok=True); return 0
def one_move(p): return 3, 'STOP 00 STUB NOT_BUILT: stub'
def adopt(*a): pass
def main(a): return 2
