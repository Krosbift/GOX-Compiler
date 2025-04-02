# DOCUMENTACIÓN DEL PROYECTO

## Integrantes del equipo

1. Santiago Torifa Manso
2. Mariana Tellez Gutierrez
3. Katherin Tatiana Ocampo

## Estructura del proyecto

```plaintext
GOX-Compiler/
├── src/
│   ├── lexical_analysis/
│   │   ├── exceptions/
│   │   │   └── lexical_exception.py
│   │   ├── grammar/
│   │   │   └── grammar.py
│   │   ├── scanner/
│   │   │   └── file_scanner.py
│   │   └── lexical_analysis.py
│   ├── compiler.py
│   └── main.py
├── test/
│   └── PROXIMAMENTE
├── __main__.py
├── .gitignore
├── DOCUMENTATION.md
├── README.md
├── requirements.txt
└── VERSIONS.md
```

## Explicación de archivos

### 1. **lexical_exception.py**

#### Descripción
La clase `LexicalException` representa una excepción léxica durante la compilación. Tiene un atributo `errors` que almacena los errores de compilación formateados.

#### Métodos
- **`__init__`**: Inicializa la instancia con una lista de errores, los convierte en una cadena separada por saltos de línea y llama a `format_errors`.
- **`format_errors`**: Imprime "Errores de compilación:" seguido de la lista de errores en `self.errors`.

#### Problemas y soluciones

| Problema | Solución |
|----------|----------|
| Las excepciones de Python mostraban errores de seguimiento en el código. | Se dejó de usar las excepciones originales de Python y se optó por imprimir los errores en pantalla. |

### 2. **grammar.py**

#### Descripción
La clase `Grammar` define la gramática para el análisis léxico usando expresiones regulares. Tiene un atributo `REGULAR_EXPRESSIONS` que almacena patrones de expresiones regulares para diferentes tipos de tokens.

#### Atributos y métodos
- **`REGULAR_EXPRESSIONS`**: Patrones de expresiones regulares para comentarios, espacios en blanco, saltos de línea, palabras reservadas, operadores, símbolos, literales y errores.
- **`get_regular_expression`**: Compila las expresiones regulares en un solo patrón con grupos nombrados para cada tipo de token.

#### Problemas y soluciones

| Problema | Solución |
|----------|----------|
| Prioridad de las expresiones regulares causaba conflictos con literales y palabras reservadas. | Se priorizaron las palabras reservadas sobre los literales. |

### 3. **file_scanner.py**

#### Descripción
La clase `FileScanner` lee el contenido de un archivo y lo devuelve como un string. Usa un bloque `try-except` para manejar errores.

#### Método
- **`read_file`**: Abre y lee el contenido del archivo; maneja `FileNotFoundError` y otras excepciones devolviendo mensajes de error.

#### Problemas y soluciones
No se presentaron problemas.

### 4. **lexical_analysis.py**

#### Descripción
La clase `LexicalAnalysis` realiza el análisis léxico de un archivo fuente, identificando tokens y manejando errores léxicos.

#### Atributos y métodos
- **Atributos**:
    - `file_content`: Contenido del archivo fuente.
    - `regular_expressions`: Expresiones regulares compiladas para la coincidencia de tokens.
- **Métodos**:
    - `__init__(file_path)`: Inicializa leyendo el contenido del archivo y obteniendo las expresiones regulares.
    - `analyze()`: Analiza el contenido del archivo, tokeniza la entrada e identifica errores.
    - `_extract_match_info(match)`: Extrae y devuelve información del token.
    - `_update_line_info(start_pos, line_start, line_number)`: Actualiza y devuelve el número de línea y la posición de inicio de la línea.

#### Problemas y soluciones
No se presentaron problemas.

### 5. **compiler.py**
PRÓXIMAMENTE

### 6. **main.py**
PRÓXIMAMENTE

### 7. **__main__.py**
PRÓXIMAMENTE
