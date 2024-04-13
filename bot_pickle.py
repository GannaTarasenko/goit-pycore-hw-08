from collections import UserDict
from datetime import datetime, timedelta
import pickle


class Field: 
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return str(self.value)
    

class Name(Field): 
    def __init__(self, name=None):
        if name is None:
            raise ValueError  # Перевірка на наявність імені
        super().__init__(name)


class Phone(Field): 
    def __init__(self, phone): 
        if len(phone) != 10:
            raise ValueError  # Перевірка на правильний формат телефонного номеру
        super().__init__(phone)
        self.__phone = None
        self.phone = phone

class Birthday(Field):
    def __init__(self, value):
        try:
            super().__init__(value)
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
            
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")  # Перевірка на правильний формат дати
    
   
class Record: 
    def __init__(self, name): 
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone): 
        for p in self.phones:
            if p.value == phone:
                return
        self.phones.append(Phone(phone))

    def remove_phone(self, phone): 
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return
        raise ValueError
    
    def edit_phone(self, old_phone, new_phone): 
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                return
        raise ValueError

    def find_phone(self, phone): 
        for p in self.phones:
            if p.value == phone:
                return p
        raise ValueError
    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
    
    def __str__(self):
        return f'Record(Name: {self.name} Phones: {self.phones})'
    
    def __repr__(self):
        return f'Record(Name: {self.name} Phones: {self.phones})'


class AddressBook(UserDict): 
    def add_record(self, record: Record): 
        name = record.name.value
        self.data.update({name: record}) 

    def find(self, name): 
        return self.get(name) 
    
    def delete(self, name): 
        del self[name]

    def find_next_weekday(d, weekday: int):
        """Функція для знаходження наступного дня народження"""
        days_ahead = weekday - d.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return d + timedelta(days=days_ahead)

    def get_upcoming_birthdays(self):
        """Функція для знаходження наступного дня народження за виключенням суботи та неділі"""
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.values():
            if record.birthday:
                birthday_date = record.birthday.value.strftime("%d.%m.%Y")  # Виправлення тут
                birthday_date = datetime.strptime(birthday_date, "%d.%m.%Y").date().replace(year=today.year)
                if birthday_date < today:
                    birthday_date = birthday_date.replace(year=today.year + 1)
                days_until_birthday = (birthday_date - today).days

                if 0 <= days_until_birthday <= 7:
                    if birthday_date.weekday() >= 5:
                        birthday_date += timedelta(days=(7 - birthday_date.weekday()))
                    upcoming_birthdays.append({
                        'name': record.name.value,
                        'congratulation_date': birthday_date.strftime("%Y.%m.%d")
                    })

        return upcoming_birthdays

def input_error_phone(func):
    """Декоратор для обробки помилок з телефонним номером"""
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:  # Обробка помилки з неправильним форматом телефонного номеру
            return "Неправильний формат введення! Будь ласка, введіть Ім'я та 10-значний номер телефону"
        except KeyError:  # Обробка помилки з відсутністю запису
            return "Запис відсутній."
        except IndexError:  # Обробка помилки з неправильною кількістю аргументів
            return "Будь ласка, введіть Ім'я"
    return inner

def input_error_birthday(func):
    """Декоратор для обробки помилок з датою народження"""
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:  # Обробка помилки з неправильним форматом дати народження
            return "Неправильний формат введення! Будь ласка, використовуйте формат дати: ДД.ММ.РРРР."
    return inner

def input_error_change_contact(func):
    """Декоратор для обробки помилок за зміною телефонного номера"""
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Неправильний формат введення! Будь ласка, введіть Ім'я, старий номер телефону та новий номер телефону."
        except KeyError:
            return "Запис відсутній."
        except IndexError:
            return "Будь ласка, введіть Ім'я, старий номер телефону та новий номер телефону."
    return inner
    
@input_error_phone
def parse_input(user_input):
    """Функція для розбору команд та аргументів"""
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error_phone
def add_contact(args, book: AddressBook):
    """Функція для додавання контакту у словник"""
    name, phone, *_ = args
    record = book.find(name)
    message = "Контакт оновлено."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Контакт додано."
    if phone:
        record.add_phone(phone)
    return message

@input_error_change_contact
def change_contact(args, book: AddressBook):
    """Функція для зміни існуючого контакту"""
    name, old_phone, new_phone, *_ = args
    if len(new_phone) != 10:  # Перевірка на правильний формат нового номера телефону
        raise ValueError("Новий номер телефону має містити 10 цифр.")
    record = book.find(name)
    if record:
        phone = record.find_phone(old_phone)
        if phone:
            record.edit_phone(old_phone, new_phone)
            message = "Номер телефону було змінено."
        else:
            message = "Телефон не знайдено."
    else:
        message = "Контакт відсутній."
    return message

@input_error_phone       
def show_phone(args, book: AddressBook):
    """Функція для відображення існуючого контакту за ім'ям користувача"""
    name, *_ = args
    record = book.find(name)
    if record:
        return record.phones
    else:
        return "Контакт відсутній."

@input_error_birthday
def add_birthday(args, book: AddressBook):
    """Функція для додавання дати народження для контакту""" 
    name, birthday, *_ = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "День народження додано."
    else:
        return "Контакт відсутній."
    
@input_error_phone
def show_birthday(args, book: AddressBook):
    """Функція для відображення дня народження контакту"""
    name, *_ = args
    record = book.find(name)
    if record:
        return record.birthday
    else:
        return "Контакт відсутній"
    
def birthdays(book: AddressBook):
    """Функція для відображення майбутніх днів народження"""
    return book.get_upcoming_birthdays()

def save_data(book, filename="addressbook.pkl"):
    """Функція для серіалізації об'єкта book та запису його у файл"""
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    """Функція для десеріалізації об'єкта з файлу та повернення його значення"""
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

def main():  # Основна функція для виводу результату
    book = load_data()
    print("Ласкаво просимо до асистента!")
    while True:
        user_input = input("Введіть команду: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("До побачення!")
            break
        elif command == "hello":
            print("Як я можу вам допомогти?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(book)
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Невірна команда.")
          
    save_data(book)


if __name__ == "__main__":
    main()
