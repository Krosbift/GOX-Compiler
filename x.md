# ¿Qué se hace en un Análisis Semántico?

El **análisis semántico** es la etapa de un compilador que **verifica que el significado del programa sea correcto**.

Aunque el análisis léxico y sintáctico aseguran que el programa *está escrito correctamente* (es decir, es *gramaticalmente válido*), eso **no significa** que tenga sentido.

El análisis semántico asegura que:

| **Error** | **¿Quién lo detecta?** | **¿Qué etapa?** |
|-------------------------------------|---------------------------|------------------------|
| Olvidé un punto y coma | Analizador léxico/sintáctico | Parsing |
| Sumo un `int` y un `bool` | Análisis semántico | Semantic checking |
| Uso una variable no declarada | Análisis semántico | Semantic checking |
| Retorno un tipo incorrecto en `func` | Análisis semántico | Semantic checking |

---

## En concreto, el análisis semántico hace:

| **Tarea** | **Ejemplo** |
|--------------------------------------|-----------------------------------------------------|
| **Verificar tipos** | `int` + `float` puede ser permitido; `int` + `bool` no. |
| **Verificar declaraciones** | No puedes usar `x` si no hiciste `var x int;` antes. |
| **Verificar alcance (scope)** | Si declaras `x` dentro de una función, no es visible afuera. |
| **Constantes inmutables** | No puedes modificar una `const`. |
| **Chequeo de llamadas a funciones** | ¿La función existe? ¿Le pasaste el número correcto de argumentos? |
| **Chequeo de retornos** | Una función `int` debe devolver un `int`. |
| **Coerciones y conversiones** | A veces `int` se convierte automáticamente a `float`, pero no siempre. |
| **Otros aspectos semánticos** | Como la asignación de valores correctos a tipos, operaciones legales, etc. |

---

## ¿Cómo lo hace?

1. **Visita** el programa **nodo por nodo** (el AST).
2. **Mantiene una tabla de símbolos** (variables, funciones, constantes) para saber qué nombres están disponibles.
3. **Consulta el tipo de cada operación** usando reglas de tipos (`typesys.py`).
4. **Lanza errores** cuando algo no tiene sentido semánticamente.

---

## Metáfora
Si el **parsing** (análisis sintáctico) es como revisar que tu ensayo tenga la gramática correcta,
el **análisis semántico** es como revisar que tus ideas tengan sentido lógico.
Parsing: Tu ensayo tiene comas, verbos, y puntos bien puestos.
Semántico: ¿Pero realmente tiene sentido lo que dices?
---

## Ejemplos Rápidos

| Código | ¿Error semántico? | ¿Por qué? |
|-----------------------------------|-------------------|------------------------------------------|
| `var x int; x = 5;` | No error | Variable declarada y tipo correcto. |
| `var x int; x = true;` | Error | No puedes asignar un `bool` a un `int`. |
| `y = 10;` | Error | `y` no ha sido declarada. |
| `print(x + 5);` | No error | Suponiendo `x` es un `int`. |
| `func f(x int) float { return x; }` | Error | Devuelve un `int` y debería devolver `float`. |

---

## Resumen Corto

> **El análisis semántico revisa el significado de tu programa: tipos, scopes, declaraciones y reglas del lenguaje.**