
import heapq
import json
from datetime import datetime

class SistemaDeTareas:
    def __init__(self, archivo_persistencia="tareas.json", archivo_historial="historial.json"):
        self.cola_prioridad = []
        self.archivo_persistencia = archivo_persistencia
        self.archivo_historial = archivo_historial
        self.historial = []
        self.cargar_tareas()
        self.cargar_historial()

    def agregar_tarea(self, nombre, prioridad, fecha_vencimiento, dependencias=[]):
        if not isinstance(prioridad, int):
            raise ValueError("La prioridad debe ser un número entero.")
        if any(tarea[2] == nombre for tarea in self.cola_prioridad):
            raise ValueError("Ya existe una tarea con ese nombre.")
        fecha_vencimiento = datetime.strptime(fecha_vencimiento, "%Y-%m-%d")
        heapq.heappush(self.cola_prioridad, (prioridad, fecha_vencimiento, nombre, dependencias))
        self.guardar_tareas()

    def mostrar_tareas(self, criterio="prioridad"):
        if not self.cola_prioridad:
            print("No hay tareas pendientes.")
            return

        if criterio == "prioridad":
            tareas_ordenadas = sorted(self.cola_prioridad, key=lambda x: (x[0], x[1]))
        elif criterio == "fecha":
            tareas_ordenadas = sorted(self.cola_prioridad, key=lambda x: (x[1], x[0]))
        else:
            print("Criterio no válido. Usa 'prioridad' o 'fecha'.")
            return

        print("\nTareas pendientes ordenadas por", criterio + ":")
        for prioridad, fecha, nombre, dependencias in tareas_ordenadas:
            print(f"- Tarea: {nombre}, Prioridad: {prioridad}, Vencimiento: {fecha.date()}, Dependencias: {dependencias}")

    def editar_tarea(self, nombre):
        for tarea in self.cola_prioridad:
            if tarea[2] == nombre:
                self.cola_prioridad.remove(tarea)
                heapq.heapify(self.cola_prioridad)
                nueva_prioridad = int(input(f"Nueva prioridad (actual: {tarea[0]}): "))
                nueva_fecha = input(f"Nueva fecha de vencimiento (AAAA-MM-DD, actual: {tarea[1].date()}): ")
                nuevas_dependencias = input(f"Nuevas dependencias (separadas por comas, actual: {tarea[3]}): ").split(",") if input("¿Modificar dependencias? (s/n): ").lower() == "s" else tarea[3]
                self.agregar_tarea(nombre, nueva_prioridad, nueva_fecha, nuevas_dependencias)
                print(f"Tarea '{nombre}' actualizada con éxito.")
                return
        print(f"No se encontró la tarea '{nombre}'.")

    def verificar_dependencias(self, dependencias):
        completadas = {tarea['nombre'] for tarea in self.historial}
        return all(dependencia in completadas for dependencia in dependencias)

    def completar_tarea(self, nombre):
        for tarea in self.cola_prioridad:
            if tarea[2] == nombre:
                # Verificar dependencias
                if not self.verificar_dependencias(tarea[3]):
                    print(f"No se puede completar la tarea '{nombre}' porque sus dependencias no están completas: {tarea[3]}")
                    return
                # Completar tarea
                self.cola_prioridad.remove(tarea)
                heapq.heapify(self.cola_prioridad)
                self.historial.append({"prioridad": tarea[0], "fecha_vencimiento": tarea[1].strftime("%Y-%m-%d"), "nombre": tarea[2], "dependencias": tarea[3]})
                self.guardar_tareas()
                self.guardar_historial()
                print(f"Tarea '{nombre}' completada y movida al historial.")
                return
        print(f"No se encontró la tarea '{nombre}'.")

    def mostrar_historial(self):
        if not self.historial:
            print("El historial está vacío.")
        else:
            print("\nHistorial de tareas completadas:")
            for tarea in self.historial:
                print(f"- Tarea: {tarea['nombre']}, Prioridad: {tarea['prioridad']}, Vencimiento: {tarea['fecha_vencimiento']}, Dependencias: {tarea['dependencias']}")

    def obtener_tarea_prioritaria(self):
        if not self.cola_prioridad:
            print("No hay tareas pendientes.")
            return
        prioridad, fecha, nombre, dependencias = self.cola_prioridad[0]
        print(f"Tarea de mayor prioridad: {nombre}, Prioridad: {prioridad}, Vencimiento: {fecha.date()}, Dependencias: {dependencias}")

    def guardar_tareas(self):
        with open(self.archivo_persistencia, "w") as archivo:
            tareas = [
                {"prioridad": tarea[0], "fecha_vencimiento": tarea[1].strftime("%Y-%m-%d"), "nombre": tarea[2], "dependencias": tarea[3]}
                for tarea in self.cola_prioridad
            ]
            json.dump(tareas, archivo)

    def cargar_tareas(self):
        try:
            with open(self.archivo_persistencia, "r") as archivo:
                tareas = json.load(archivo)
                self.cola_prioridad = [
                    (tarea["prioridad"], datetime.strptime(tarea["fecha_vencimiento"], "%Y-%m-%d"), tarea["nombre"], tarea["dependencias"])
                    for tarea in tareas
                ]
                heapq.heapify(self.cola_prioridad)
        except (FileNotFoundError, json.JSONDecodeError):
            self.cola_prioridad = []

    def guardar_historial(self):
        with open(self.archivo_historial, "w") as archivo:
            json.dump(self.historial, archivo)

    def cargar_historial(self):
        try:
            with open(self.archivo_historial, "r") as archivo:
                self.historial = json.load(archivo)
        except (FileNotFoundError, json.JSONDecodeError):
            self.historial = []

def mostrar_menu():
    print("\n--- Sistema de Gestión de Tareas ---")
    print("1. Añadir una nueva tarea")
    print("2. Mostrar tareas pendientes ordenadas por prioridad o fecha")
    print("3. Editar una tarea")
    print("4. Filtrar tareas")
    print("5. Marcar una tarea como completada")
    print("6. Mostrar historial de tareas completadas")
    print("7. Obtener la tarea de mayor prioridad")
    print("8. Salir")

def ejecutar_sistema():
    sistema = SistemaDeTareas()

    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción (1-8): ")

        if opcion == "1":
            nombre = input("Nombre de la tarea: ")
            try:
                prioridad = int(input("Prioridad (número entero, menor número = mayor prioridad): "))
            except ValueError:
                print("La prioridad debe ser un número entero.")
                continue
            fecha_vencimiento = input("Fecha de vencimiento (AAAA-MM-DD): ")
            dependencias = input("Dependencias (separadas por comas, si las hay): ").split(",") if input("¿Tiene dependencias? (s/n): ").lower() == "s" else []
            try:
                sistema.agregar_tarea(nombre, prioridad, fecha_vencimiento, dependencias)
                print(f"Tarea '{nombre}' añadida con éxito.")
            except ValueError as e:
                print(e)

        elif opcion == "2":
            criterio = input("¿Cómo deseas ordenar las tareas? ('prioridad' o 'fecha'): ").lower()
            sistema.mostrar_tareas(criterio)

        elif opcion == "3":
            nombre = input("Nombre de la tarea a editar: ")
            sistema.editar_tarea(nombre)

        elif opcion == "4":
            criterio = input("Criterio de filtrado ('prioridad', 'fecha' o 'dependencias'): ").lower()
            valor = input("Valor para el criterio seleccionado: ")
            sistema.filtrar_tareas(criterio, valor)

        elif opcion == "5":
            nombre = input("Nombre de la tarea a completar: ")
            sistema.completar_tarea(nombre)

        elif opcion == "6":
            sistema.mostrar_historial()

        elif opcion == "7":
            sistema.obtener_tarea_prioritaria()

        elif opcion == "8":
            print("Saliendo del sistema. ¡Hasta pronto!")
            break

        else:
            print("Opción no válida. Inténtalo de nuevo.")

# Ejecutar el sistema
ejecutar_sistema()
