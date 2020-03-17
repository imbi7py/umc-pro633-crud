from . import crud
from .cli import print_h1, print_h2, print_long, print_error, print_table
import re

# Módulo de estudiante

def main(user_id):
    """Función principal del módulo de estudiante."""
    # Lista de opciones con sus funciones asociadas
    opciones = [['Consultar información personal', show_personal_info],
                ['Consultar récord académico completo', show_record],
                ['Consultar calificaciones por materia', find_grades],
                ['Calcular índice académico acumulado (IAA)', calculate_iaa],
                ['Calcular índice académico parcial (IAP)', calculate_iap],
                ['Salir']]
    while True:
        print()
        print_h1(f'Módulo de Estudiante')
        print_h2(user_id)
        # Mostrar las opciones del menú
        for i, opcion in enumerate(opciones):
            print(f'{i+1}. {opcion[0]}')
        print()
        # Pedir al usuario que elija alguna opción entre 1 y n
        opc = int(input(f'Elegir opción (1-{len(opciones)}): '))
        print()
        if opc in range(1, len(opciones)):
            # Si la opción elegida está entre 1 y n-1,
            # ejecutar la función correspondiente
            funcion = opciones[opc-1][1]
            funcion(crud.get_student_info(user_id))
            cont = input('[Enter] para volver al menu principal... ')
        else:
            # De lo contrario, salir
            print('Saliendo.')
            break


def show_personal_info(student_data):
    """Muestra la información personal del estudiante."""
    print_h2(f'Información personal: {student_data["id_usuario"]}')
    print(f'Nombre y apellido: {student_data["nombre"]} '
          f'{student_data["apellido"]}')
    print(f'C.I.: {student_data["ci"]}')
    print(f'Teléfono: {student_data["telefono"]}')
    print(f'Dirección: {student_data["direccion"]}')
    carrera = crud.get_career_info(student_data['id_carrera'])
    print(f'Carrera: {carrera["nombre"]} ({carrera["id"]})')
    print(f'Mención {carrera["mencion"]}')
    print()


def show_record(student_data):
    """Muestra el record académico completo del estudiante."""
    print_h2(f'Récord académico: {student_data["id_usuario"]}')
    # Muestra la tabla
    print_record(crud.read_records(student_data['ci']))


def find_grades(student_data):
    """Consulta las calificaciones por materia del estudiante."""
    print_h2(f'Consulta de calificaciones: {student_data["id_usuario"]}')
    print_long('Introduzca el código de una o varias materias para '
               'consultar sus calificaciones. El código de materia '
               'consiste de letras y números solamente, por ejemplo '
               'CAL114. Para buscar varias materias escriba '
               'sus códigos separados por espacios o comas.')
    # Pide al usuario los códigos de materia y los separa en una lista
    materia_ids = re.split('[,\s]+', input('Materia(s): ').upper())
    # Muestra la tabla
    print_record(crud.read_records(student_data['ci'], materia_ids))


def calculate_iaa(student_data):
    """Calcula el índice académico acumulado (IAA) del estudiante."""
    print_h2(f'Índice Académico Acumulado: {student_data["id_usuario"]}')
    record = crud.read_records(student_data['ci'])
    iaa = calculate_ia(record)
    print(f'Su IAA es de {iaa} según su récord académico completo.')
    print()


def calculate_iap(student_data):
    """Calcula el índice académico parcial (IAP) del estudiante por período."""
    print_h2(f'Índice Académico Parcial: {student_data["id_usuario"]}')
    print_long('El IAP es el índice académico acumulado hasta un período '
               'determinado, es decir, tomando en cuenta solo las materias '
               'cursadas en ese período y períodos anteriores. Introduzca '
               'el período académico para calcular su IAP (ejemplos: 2020-01, '
               '2018-IN, 2019-02).')
    # Pide al usuario el período académico límite
    p = input('Período académico: ').upper()
    if re.match('^\d{4}-(01|IN|02)$'):
        # Si el usuario ingresó un período válido
        # Se calcula el índice académico con las materias
        # cursadas hasta el período límite
        iap = calculate_ia(
                filter_records_until_period(
                    crud.read_records(student_data['ci'])))
        print(f'Su IAP es de {iap} según su récord académico '
              f'hasta el período {p}.')
    else:
        # Si no se ingresó un período válido, mostrar un error
        print_error('Período académico inválido.')
    print()


def calculate_ia(record):
    """Calcula el índice académico acumulado a partir del récord dado."""
    suma_ponderada = sum([r['uc']*r['nota'] for r in record])
    suma_uc = sum([r['uc'] for r in record])
    return round(suma_ponderada/suma_uc, 2)


def print_record(record):
    """Muestra una tabla de récords académicos a partir de los datos dados."""
    cols = {'id': 'Código',
            'nombre': 'Materia'
            'uc': 'UC'
            'nota': 'Nota',
            'periodo': 'Período'}
    widths = dict(zip(columnas.keys(), [10, 45, 5, 5, 10]))
    print_table(record, cols, widths)


def filter_records_until_period(record, period):
    """Conserva los registros de materias cursadas hasta el período dado."""
    # Separa los componentes del período de entrada (año y lapso)
    yi, li = period.split('-')
    # Crea la lista que almacenará el récord filtrado
    result = []
    # Para cada registro en el récord
    for r in record:
        # Se separan los componentes del período
        # en que se cursó la materia
        y, l = r['periodo'].split('-')
        # Si la materia se cursó en el año anterior, o
        # en el mismo año pero en el mismo lapso o uno
        # anterior, se conserva el registro
        seq =  ['01', 'IN', '02']
        if y < yi or (y == yi and seq.index(l) <= seq.index(li)):
            result.append(r)
    return result
