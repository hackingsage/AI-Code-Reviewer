import os
import pickle


def insecure_eval(x):
    # SECURITY: eval
    return eval(x)


def normalize(values):
    # LOGIC + PERFORMANCE
    total = sum(values)
    out = []

    for i in range(len(values)):
        out.append(values[i] / total)

    return out


class Cache:
    def __init__(self, data=[]):
        # LOGIC: mutable default
        self.data = data

    def add(self, x):
        self.data.append(x)


def main():
    run = insecure_eval("1 + 1")
    print(run)

    normalize([1, 2, 3])

    c = Cache()
    c.add(10)

    os.system("echo done")  # SECURITY


if __name__ == "__main__":
    main()
