from app import app


@app.task
def add(x, y):
    print(f"Adding {x} and {y}")
    return x + y


@app.task
def mul(x, y):
    return x * y


@app.task
def xsum(numbers):
    return sum(numbers)