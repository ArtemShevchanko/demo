# Клас Alphabet описує звичайний алфавіт
class Alphabet:
    # Метод __init__() створює об'єкт алфавіту
    # lang — мова
    # letters — рядок з літерами алфавіту
    def __init__(self, lang, letters):
        self.lang = lang
        self.letters = letters

    # Метод print() виводить літери алфавіту на екран
    def print(self):
        print("Літери алфавіту:")
        print(self.letters)

    # Метод letters_num() повертає кількість літер в алфавіті
    def letters_num(self):
        return len(self.letters)


# Клас EngAlphabet описує англійський алфавіт
# Він успадковує клас Alphabet
class EngAlphabet(Alphabet):
    # Приватний статичний атрибут,
    # який зберігає кількість літер в англійському алфавіті
    __letters_num = 26

    # Метод __init__() створює об'єкт англійського алфавіту
    def __init__(self):
        # Рядок з усіма літерами англійського алфавіту
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        # Викликаємо метод __init__() батьківського класу Alphabet
        # Передаємо позначення мови та рядок з літерами
        super().__init__("En", letters)

    # Метод is_en_letter() перевіряє,
    # чи належить літера англійському алфавіту
    def is_en_letter(self, letter):
        return letter.upper() in self.letters

    # Перевизначений метод letters_num()
    # Тепер він повертає значення приватного атрибута __letters_num
    def letters_num(self):
        return EngAlphabet.__letters_num

    # Статичний метод example()
    # Повертає приклад тексту англійською мовою
    @staticmethod
    def example():
        return "The quick brown fox jumps over the lazy dog."


# Основна частина програми
def main():
    # Створюємо об'єкт класу EngAlphabet
    eng = EngAlphabet()

    # Виводимо літери алфавіту
    eng.print()

    # Виводимо кількість літер в алфавіті
    print("Кількість літер в англійському алфавіті:")
    print(eng.letters_num())

    # Перевіряємо, чи належить літера F англійському алфавіту
    print("Чи належить літера 'F' англійському алфавіту?")
    print(eng.is_en_letter("F"))

    # Перевіряємо, чи належить літера Щ англійському алфавіту
    print("Чи належить літера 'Щ' англійському алфавіту?")
    print(eng.is_en_letter("Щ"))

    # Виводимо приклад тексту англійською мовою
    print("Приклад тексту англійською мовою:")
    print(EngAlphabet.example())


# Запускаємо програму
if __name__ == "__main__":
    main()
