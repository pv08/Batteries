import torch
from torch.optim import Optimizer

class CustomLinearProgrammingOptimizer(Optimizer):
    def __init__(self, params, learning_rate=0.1):
        defaults = dict(learning_rate=learning_rate)
        super(CustomLinearProgrammingOptimizer, self).__init__(params, defaults)

    def step(self, closure=None):
        loss = None
        if closure is not None:
            loss = closure()

        for group in self.param_groups:
            for p in group['params']:
                if p.grad is None:
                    continue
                p.data -= group['learning_rate'] * p.grad.data

        return loss

if __name__ == '__main__':
    x = torch.tensor([1.0], requires_grad=True, device='cuda')
    y = torch.tensor([1.0], requires_grad=True, device='cuda')

    def objective():
        return -(3 * x + 4 * y)

    def closure():
        CustomLinearProgrammingOptimizer.zero_grad()
        obj = objective()
        loss = -obj
        loss.backward()
        return loss

    optimizer = CustomLinearProgrammingOptimizer([x, y], learning_rate=0.1)

    max_iterations = 100
    for iteration in range(max_iterations):
        optimizer.step(closure)
        if iteration % 10 == 0:
            obj_value = -objective().item()
            print(f'Iteration {iteration}: x={x.item()}, y={y.item()}, Objective={obj_value}')

    optimal_x = x.item()
    optimal_y = y.item()
    optimal_objective = -objective().item()
    print(f'Optimal Solution: x={optimal_x}, y={optimal_y}, Objective={optimal_objective}')