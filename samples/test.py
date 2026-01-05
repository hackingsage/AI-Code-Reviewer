import os
import json
import pickle


def load_data(path):
    # SECURITY: pickle
    with open(path, "rb") as f:
        return pickle.loads(f.read())


def run_command(cmd):
    # SECURITY: os.system
    os.system(cmd)


def insecure_eval(expr):
    # SECURITY: eval
    return eval(expr)


def normalize(values):
    # LOGIC + PERFORMANCE
    total = sum(values)
    result = []

    for i in range(len(values)):  # len() in loop
        result.append(values[i] / total)

    return result


def compute_stats(data, scale=1.0, cache=[]):
    # LOGIC: mutable default
    scaled = []

    for i in range(len(data)):
        scaled.append(data[i] * scale)

    cache.append(scaled)

    return {
        "mean": sum(scaled) / len(scaled),
        "count": len(scaled),
    }


def bad_flag(flag):
    # LOGIC: == True / False
    if flag == True:
        return "on"
    elif flag == False:
        return "off"
    return None


def deep_nesting(n):
    # COMPLEXITY
    total = 0
    for i in range(n):
        for j in range(n):
            if i % 2 == 0:
                for k in range(3):
                    total += i + j + k
    return total


class Processor:
    def __init__(self, items=[]):
        # LOGIC: mutable default
        self.items = items

    def process(self):
        # PERFORMANCE: len in loop
        total = 0
        for i in range(len(self.items)):
            total += self.items[i]
        return total


def main():
    data = [1, 2, 3]

    run_command("echo test")
    insecure_eval("1 + 1")

    print(normalize(data))
    print(compute_stats(data))
    print(bad_flag(True))
    print(deep_nesting(2))

    p = Processor()
    p.items.extend(data)
    print(p.process())


if __name__ == "__main__":
    main()
