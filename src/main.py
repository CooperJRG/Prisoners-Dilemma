# Description: This is the main file that contains the code to generate the
# Fibonacci sequence.
def fibonacci(n):
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    else:
        fib_sequence = [0, 1]
        while len(fib_sequence) < n:
            next_number = fib_sequence[-1] + fib_sequence[-2]
            fib_sequence.append(next_number)
        return fib_sequence


# Example usage
def main():
    n = 10
    fib_sequence = fibonacci(n)
    print(fib_sequence)
    
    
if __name__ == "__main__":
    main()
    
