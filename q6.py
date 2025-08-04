#check if 97 is prime number
def is_prime(n):
    if n<2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0 :
            return False
    return True
print("97 is prime", is_prime(97))