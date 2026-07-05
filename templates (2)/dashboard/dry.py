import secrets
import string

def generate_strong_password(length=12):
    if length < 8:
        raise ValueError("Password length should be at least 8 characters for security.")
    
    # Character sets
    letters = string.ascii_letters      # a-z + A-Z
    digits = string.digits             # 0-9
    punctuation = string.punctuation   # Special chars

    # Ensure the password contains at least one from each set
    all_chars = letters + digits + punctuation
    password = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(digits),
        secrets.choice(punctuation)
    ]

    # Fill the rest with random choices
    password += [secrets.choice(all_chars) for _ in range(length - 4)]

    # Shuffle the password for randomness
    secrets.SystemRandom().shuffle(password)

    return ''.join(password)
