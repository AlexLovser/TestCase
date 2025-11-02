"""
Скрипт для генерации тестовых данных через прямую работу с БД
Используется при первом запуске приложения
"""
import random
from server.core.db import SessionLocal
from server.core.models import Domain, Enterprise, Address, Phone

BASE_LAT = 55.7558
BASE_LON = 37.6173
RADIUS = 0.5

domains_hierarchy = [
    {"name": "Еда", "parent_id": None},
    {"name": "Мясная продукция", "parent_name": "Еда"},
    {"name": "Молочная продукция", "parent_name": "Еда"},
    {"name": "Колбасы", "parent_name": "Мясная продукция"},
    {"name": "Сыры", "parent_name": "Молочная продукция"},

    {"name": "Услуги", "parent_id": None},
    {"name": "Строительство", "parent_name": "Услуги"},
    {"name": "IT", "parent_name": "Услуги"},
    {"name": "Ремонт", "parent_name": "Строительство"},

    {"name": "Торговля", "parent_id": None},
    {"name": "Оптовая торговля", "parent_name": "Торговля"},
    {"name": "Розничная торговля", "parent_name": "Торговля"},
]

companies = [
    "ООО Рога и Копыта", "ИП Васильев", "ООО Техносервис", "ЗАО Стройком",
    "ООО Меркурий", "ИП Иванов", "ООО Альфа", "ЗАО Бета",
    "ООО Гамма", "ИП Петров", "ООО Дельта", "ЗАО Эпсилон",
    "ООО Зета", "ИП Сидоров", "ООО Эта", "ЗАО Тета",
    "ООО Йота", "ИП Смирнов", "ООО Каппа", "ЗАО Лямбда",
    "ООО Мю", "ИП Кузнецов", "ООО Ню", "ЗАО Кси",
    "ООО Омикрон"
]

business_centers = [
    {"street": "ул. Ленина", "house": 15},
    {"street": "ул. Пушкина", "house": 77},
    {"street": "пр-т Мира", "house": 9},
    {"street": "ул. Гагарина", "house": 42},
    {"street": "ул. Советская", "house": 111},
    {"street": "ул. Кирова", "house": 25},
    {"street": "пр-т Победы", "house": 58},
    {"street": "ул. Центральная", "house": 97},
    {"street": "пр-т Ленинский", "house": 33},
    {"street": "ул. Парковая", "house": 51},
]


def generate_phone():
    return f"+7 (495) {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}"


def seed_data():
    """Генерация тестовых данных"""
    db = SessionLocal()
    try:
        print("=== Создание иерархии доменов ===\n")

        domain_map = {}
        for domain_data in domains_hierarchy:
            parent_id = None
            if "parent_name" in domain_data:
                parent_id = domain_map.get(domain_data["parent_name"])
            elif "parent_id" in domain_data:
                parent_id = domain_data["parent_id"]

            domain = Domain(name=domain_data["name"], parent_id=parent_id)
            db.add(domain)
            db.flush()
            domain_map[domain_data["name"]] = domain.id
            print(f"[OK] Домен: {domain_data['name']}")

        print(f"\n=== Создано доменов: {len(domain_map)} ===")

        print("\n=== Создание бизнес-центров (адресов) ===\n")

        addresses = []
        for i, bc in enumerate(business_centers):
            lat = BASE_LAT + random.uniform(-RADIUS, RADIUS)
            lon = BASE_LON + random.uniform(-RADIUS, RADIUS)

            address = Address(
                address=f"{bc['street']}, д. {bc['house']}",
                latitude=lat,
                longitude=lon
            )
            db.add(address)
            db.flush()
            addresses.append(address)
            print(f"[OK] Адрес: {bc['street']}, д. {bc['house']} (id={address.id})")

        print(f"\n=== Создано адресов: {len(addresses)} ===")
        print("\n=== Создание 25 тестовых предприятий ===\n")

        domain_ids = list(domain_map.values())
        created_count = 0

        for i in range(25):
            address = random.choice(addresses)

            domain_id = random.choice(domain_ids) if domain_ids else None
            enterprise = Enterprise(
                name=companies[i],
                address_id=address.id,
                domain_id=domain_id
            )
            db.add(enterprise)
            db.flush()

            for _ in range(2):
                phone = Phone(phone=generate_phone(), enterprise_id=enterprise.id)
                db.add(phone)

            created_count += 1
            print(f"[OK] {companies[i]} -> {address.address}")

        db.commit()
        print(f"\n=== Создано предприятий: {created_count} ===")

    except Exception as e:
        db.rollback()
        print(f"[ERR] Ошибка: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()

