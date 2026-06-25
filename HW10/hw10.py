import random

def guess_number():
    # Генеруємо випадкове число від 1 до 100
    secret_number = random.randint(1, 100)
    # Встановлюємо максимальну кількість спроб
    max_attempts = 5
    # Цикл працює від 1 до 5 спроби
    for attempt in range(1, max_attempts + 1):
        # Цей цикл потрібен, щоб перевірити правильність введення
        while True:
            try:
                # Просимо користувача ввести число
                user_guess = int(input(f"Attempt {attempt}/{max_attempts}. Guess a number from 1 to 100: "))

                # Перевіряємо, чи число знаходиться в діапазоні від 1 до 100
                if user_guess < 1 or user_guess > 100:
                    print("Please enter a number from 1 to 100.")
                    continue
                # Якщо число введено правильно, виходимо з циклу перевірки
                break
            except ValueError:
                # Якщо користувач ввів не число, показуємо повідомлення про помилку
                print("Please enter a valid number.")
        # Перевіряємо, чи користувач вгадав число
        if user_guess == secret_number:
            print("Congratulations! You guessed the right number!")
            return
        # Якщо введене число більше за правильне
        elif user_guess > secret_number:
            print("Too high")
        # Якщо введене число менше за правильне
        else:
            print("Too low")
    # Якщо користувач не вгадав число за 5 спроб
    print(f"Sorry, you've run out of attempts. The correct number was {secret_number}")
# Викликаємо функцію для запуску програми
guess_number()
