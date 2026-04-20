import json
from datetime import datetime
import random

# Configuración 
VALOR_CITA = {"particular": 80000, "eps": 5000, "prepagada": 30000}
VALORES_ATENCION = {
    "particular": {"limpieza": 60000, "calzas": 80000, "extracción": 100000, "diagnóstico": 50000},
    "eps": {"limpieza": 0, "calzas": 40000, "extracción": 40000, "diagnóstico": 0},
    "prepagada": {"limpieza": 0, "calzas": 10000, "extracción": 10000, "diagnóstico": 0}
}

DATA_FILE = "consultorio.json"
DAILY_QUEUE = []
URGENT_STACK = []

# Persistencia 
def save_data(data_list):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data_list, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error al guardar: {e}")

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception:
        return []

# Utilidades 
def get_length(data_list):
    count = 0
    for _ in data_list:
        count += 1
    return count

def add_to_list(data_list, element):
    return data_list + [element]

def sort_customers(data_list):
    n = get_length(data_list)
    for i in range(n):
        for j in range(0, n - i - 1):
            if data_list[j]['total_value'] < data_list[j+1]['total_value']:
                data_list[j], data_list[j+1] = data_list[j+1], data_list[j]
    return data_list

def search_by_id(data_list, client_id):
    for client in data_list:
        if client['id_card'] == client_id:
            return client
    return None

# Registro 
def capture_data(db_clients):
    try:
        id_card = input("Cédula: ")
        name = input("Nombre: ")
        phone = input("Teléfono: ")

        client_type = input("Tipo (Particular, EPS, Prepagada): ").lower()
        if client_type not in VALOR_CITA:
            raise ValueError("Tipo de cliente inválido.")

        attention_type = input("Atención (Limpieza, Calzas, Extracción, Diagnóstico): ").lower()
        if attention_type == "extraccion": attention_type = "extracción"
        if attention_type == "diagnostico": attention_type = "diagnóstico"
        if attention_type not in VALORES_ATENCION[client_type]:
            raise ValueError("Atención inválida.")

        if attention_type in ["limpieza", "diagnóstico"]:
            quantity = 1
        else:
            quantity = int(input("Cantidad: "))
            if quantity <= 0:
                raise ValueError("Debe ser mayor a 0.")

        priority = input("Prioridad (Normal/Urgente): ").lower()
        appointment_date = input("Fecha (DD/MM/AAAA): ")
        appointment_time = input("Hora (HH:MM): ")

        total_value = VALOR_CITA[client_type] + (VALORES_ATENCION[client_type][attention_type] * quantity)

        client = {
            'id_card': id_card,
            'name': name,
            'phone': phone,
            'client_type': client_type.capitalize(),
            'attention_type': attention_type.capitalize(),
            'quantity': quantity,
            'priority': priority.capitalize(),
            'appointment_date': appointment_date,
            'appointment_time': appointment_time,
            'total_value': total_value,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        db_clients.append(client)
        save_data(db_clients)

        if priority == "urgente":
            URGENT_STACK.append(client)
        else:
            DAILY_QUEUE.append(client)

        print("\n¡Cliente registrado con éxito!")
        return client
    except Exception as e:
        print(f"Error: {e}")
        return None

# Estadísticas 
def show_statistics(data_list):
    total_clients = get_length(data_list)
    total_income = sum(c['total_value'] for c in data_list)
    extraction_count = sum(1 for c in data_list if c['attention_type'].lower() == "extracción")
    print(f"\nClientes: {total_clients} | Total Ingresos: ${total_income:,} | Extracciones: {extraction_count}")

# Generación de clientes aleatorios 
def generate_random_clients(db_clients, n=5):
    names = ["Ana", "Luis", "Carla", "Jorge", "Marta"]
    for _ in range(n):
        client = {
            'id_card': str(random.randint(10000000, 99999999)),
            'name': random.choice(names),
            'phone': str(random.randint(3000000000, 3999999999)),
            'client_type': random.choice(list(VALOR_CITA.keys())).capitalize(),
            'attention_type': random.choice(list(VALORES_ATENCION['particular'].keys())).capitalize(),
            'quantity': random.randint(1, 3),
            'priority': random.choice(["Normal", "Urgente"]),
            'appointment_date': f"{random.randint(1,28):02}/{random.randint(1,12):02}/2026",
            'appointment_time': f"{random.randint(8,17):02}:{random.choice([0,15,30,45]):02}",
            'total_value': random.randint(5000, 150000),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        db_clients.append(client)
        if client['priority'].lower() == "urgente":
            URGENT_STACK.append(client)
        else:
            DAILY_QUEUE.append(client)
    save_data(db_clients)
    print(f"\n{n} clientes aleatorios generados y guardados en {DATA_FILE}.")
    return db_clients

# Manejo de agenda 
def serve_next_client():
    if URGENT_STACK:
        client = URGENT_STACK.pop()
        print(f"\nAtendiendo urgencia: {client['name']} | {client['attention_type']}")
    elif DAILY_QUEUE:
        client = DAILY_QUEUE.pop(0)
        print(f"\nAtendiendo cliente normal: {client['name']} | {client['attention_type']}")
    else:
        print("\nNo hay clientes en la agenda.")

#  Menú detallado 
def main_menu():
    db_clients = load_data()
    # Inicializar colas desde JSON
    for c in db_clients:
        if c['priority'].lower() == "urgente":
            URGENT_STACK.append(c)
        else:
            DAILY_QUEUE.append(c)

    while True:
        print("\n" + "="*60)
        print(" " * 10 + "DENTAL CLINIC SYSTEM (CLI MODE)")
        print("="*60)
        print("1. Dashboard")
        print("   -> Ver estadísticas: total de clientes, ingresos y extracciones.")
        print("2. Register Client Appointment")
        print("   -> Agregar un nuevo cliente con tipo, atención, prioridad y horario.")
        print("3. Generate Random Clients (For Testing)")
        print("   -> Crear clientes aleatorios para probar el sistema.")
        print("4. View Clients List & Search")
        print("   -> Mostrar listado de clientes y buscar por cédula.")
        print("5. Manage Daily Queue (FIFO Agenda)")
        print("   -> Atender clientes normales en orden de llegada.")
        print("6. Manage Contingency Stack (Urgencies)")
        print("   -> Atender clientes urgentes en orden inverso (último ingresado primero).")
        print("7. Exit")
        print("="*60)

        option = input("Seleccione una opción: ")

        if option == "1":
            show_statistics(db_clients)
        elif option == "2":
            capture_data(db_clients)
        elif option == "3":
            try:
                n = int(input("Cantidad de clientes aleatorios a generar: "))
                db_clients = generate_random_clients(db_clients, n)
            except ValueError:
                print("Ingrese un número válido.")
        elif option == "4":
            db_clients = sort_customers(db_clients)
            for c in db_clients:
                print(f"[{c['client_type']}] {c['id_card']} - {c['name']}: ${c['total_value']:,}")
            search_term = input("Ingrese cédula para buscar (Enter para saltar): ")
            if search_term:
                result = search_by_id(db_clients, search_term)
                if result:
                    print("\nDatos encontrados:")
                    for key, value in result.items():
                        print(f"{key}: {value}")
                else:
                    print("Cliente no encontrado.")
        elif option == "5":
            serve_next_client()
        elif option == "6":
            if URGENT_STACK:
                print("\nUrgencias en espera:")
                for c in URGENT_STACK[::-1]:
                    print(f"{c['name']} | {c['attention_type']} | {c['appointment_date']} {c['appointment_time']}")
            else:
                print("\nNo hay urgencias.")
        elif option == "7":
            print("Saliendo del sistema...")
            break
        else:
            print("Opción inválida. Intente de nuevo.")

if __name__ == "__main__":
    main_menu()