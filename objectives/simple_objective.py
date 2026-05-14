# objectives/simple_objective.py
import logging

def objective_function(x, y):
    print("Evaluating objective function with x = %s and y = %s" % (x, y))
    return {"objective": (x - 0.5) ** 2 + (y - 0.5) ** 2}