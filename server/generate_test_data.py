import random
import requests

# Координаты для региона (например, Москва и область)
# Центр: 55.7558, 37.6173
BASE_LAT = 55.7558
BASE_LON = 37.6173
RADIUS = 0.5  # ~50км разброс

API_URL = "http://localhost:8000/api"

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

streets = [
    "ул. Ленина", "ул. Пушкина", "пр-т Мира", "ул. Гагарина",
    "ул. Советская", "ул. Кирова", "пр-т Победы", "ул. Молодежная",
    "ул. Центральная", "ул. Школьная", "пр-т Ленинский", "ул. Садовая",
    "ул. Новая", "ул. Зеленая", "пр-т Комсомольский", "ул. Рабочая",
    "ул. Парковая", "ул. Заречная", "пр-т Октябрьский", "ул. Лесная",
    "ул. Полевая", "ул. Строителей", "пр-т Мирный", "ул. Трудовая",
    "ул. Дружбы"
]


def generate_phone():
    return f"+7 (495) {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}"


def create_domain(name, parent_id=None):
    data = {"name": name}
    if parent_id:
        data["parent_id"] = parent_id

    try:
        response = requests.post(f"{API_URL}/domains", json=data)
        if response.status_code == 201:
            print(f"[OK] Домен: {name}")
            return response.json()
        else:
            print(f"[ERR] Домен {name}: {response.status_code}")
            return None
    except Exception as e:
        print(f"[ERR] Домен {name}: {e}")
        return None


def create_enterprise(name, street, domain_id=None):
    lat = BASE_LAT + random.uniform(-RADIUS, RADIUS)
    lon = BASE_LON + random.uniform(-RADIUS, RADIUS)
    house = random.randint(1, 150)

    data = {
        "name": name,
        "domain_id": domain_id,
        "address": {
            "address": f"{street}, д. {house}",
            "latitude": lat,
            "longitude": lon
        },
        "phones": [generate_phone(), generate_phone()]
    }

    try:
        response = requests.post(f"{API_URL}/enterprises", json=data)
        if response.status_code == 201:
            print(f"[OK] {name} ({lat:.4f}, {lon:.4f})")
            return response.json()
        else:
            print(f"[ERR] {name}: {response.status_code}")
            return None
    except Exception as e:
        print(f"[ERR] {name}: {e}")
        return None


def test_in_circle(center_lat, center_lon, radius_m):
    print(f"\n=== Тест in_circle: центр ({center_lat}, {center_lon}), радиус {radius_m}м ===")
    response = requests.get(
        f"{API_URL}/enterprises/in_circle/",
        params={"x": center_lat, "y": center_lon, "r": radius_m}
    )
    if response.status_code == 200:
        results = response.json()
        print(f"Найдено предприятий: {len(results)}")
        for ent in results[:5]:
            print(f"  - {ent['name']}: {ent['address']['address']}")
        return results
    else:
        print(f"Ошибка: {response.status_code}")
        return []


def test_in_frame(lat1, lon1, lat2, lon2):
    print(f"\n=== Тест in_frame: ({lat1}, {lon1}) -> ({lat2}, {lon2}) ===")
    response = requests.get(
        f"{API_URL}/enterprises/in_frame/",
        params={"x1": lat1, "y1": lon1, "x2": lat2, "y2": lon2}
    )
    if response.status_code == 200:
        results = response.json()
        print(f"Найдено предприятий: {len(results)}")
        for ent in results[:5]:
            print(f"  - {ent['name']}: {ent['address']['address']}")
        return results
    else:
        print(f"Ошибка: {response.status_code}")
        return []


if __name__ == "__main__":
    print("=== Создание иерархии доменов ===\n")

    domain_map = {}
    for domain_data in domains_hierarchy:
        parent_id = None
        if "parent_name" in domain_data:
            parent_id = domain_map.get(domain_data["parent_name"])
        elif "parent_id" in domain_data:
            parent_id = domain_data["parent_id"]

        result = create_domain(domain_data["name"], parent_id)
        if result:
            domain_map[domain_data["name"]] = result["id"]

    print(f"\n=== Создано доменов: {len(domain_map)} ===")

    print("\n=== Создание 25 тестовых предприятий ===\n")

    created = []
    domain_ids = list(domain_map.values())
    for i in range(25):
        domain_id = random.choice(domain_ids) if domain_ids else None
        result = create_enterprise(companies[i], streets[i], domain_id)
        if result:
            created.append(result)

    print(f"\n=== Создано предприятий: {len(created)} ===")

    test_in_circle(BASE_LAT, BASE_LON, 20000)
    test_in_circle(BASE_LAT, BASE_LON, 50000)

    test_in_frame(BASE_LAT - 0.2, BASE_LON - 0.2, BASE_LAT + 0.2, BASE_LON + 0.2)
    test_in_frame(BASE_LAT, BASE_LON, BASE_LAT + 0.3, BASE_LON + 0.3)

