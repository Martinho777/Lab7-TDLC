# Laboratorio 7 — Ejercicio 2

## Integrantes

- Esteban de la Peña — 24171
- Martin Villatoro — 24033

Programa en Python para leer gramáticas libres de contexto y eliminar producciones-ε.

## Requisitos

- Python 3.10 o superior.
- No requiere instalar paquetes externos.

## Formato de los archivos

Cada línea debe tener una producción con este formato:

```text
S -> 0A0 | 1B1 | BB
```

- Las letras mayúsculas individuales (`A-Z`) son no terminales.
- Las letras minúsculas y los dígitos (`a-z`, `0-9`) son terminales.
- Se acepta `->` o `→` como flecha.
- Las alternativas se separan con `|`.
- Se usa `ε` para representar una producción vacía.
- Las líneas vacías y las líneas que comienzan con `#` se ignoran.
- Si una línea es inválida, el programa se detiene y muestra el número de línea.

## Ejecución

Desde esta carpeta:

```bash
python3 grammar_simplifier.py gramatica1.txt gramatica2.txt
```

También puede ejecutarse un archivo a la vez:

```bash
python3 grammar_simplifier.py gramatica1.txt
```

El programa muestra la gramática cargada, los símbolos anulables, las combinaciones generadas para cada cuerpo con símbolos anulables y la gramática final sin producciones-ε. Cuando el símbolo inicial es anulable, crea un nuevo símbolo inicial para conservar ε correctamente.

## Prueba de validación

Para demostrar que la ejecución se detiene ante una línea inválida, copie temporalmente uno de los archivos y agregue, por ejemplo:

```text
S -> 0A0 | |
```

Luego ejecútelo. El programa debe mostrar un error indicando la línea inválida y terminar con código de error.

## Video de demostración

[Video de demostración](https://uvggt-my.sharepoint.com/:f:/g/personal/vil24033_uvg_edu_gt/IgCS9Xc87AoGSbxzTpVnGvtXAWPs2fFLtktBNxhjEwFnGME?e=wT7fJW)

## Estructura

```text
Ejercicio2/
├── grammar_simplifier.py
├── gramatica1.txt
├── gramatica2.txt
└── README.md
```
