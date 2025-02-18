# GOX-Compiler

## Requisitos para usar el aplicativo

1. **Instalar Miniconda**  
    Descargue e instale Miniconda desde el siguiente enlace: [Miniconda Link](https://docs.conda.io/en/latest/miniconda.html). Siga las instrucciones específicas para su sistema operativo.

2. **Crear un entorno virtual**  
    Abra una terminal y ejecute el siguiente comando para crear un entorno virtual llamado `gox-compiler` con Python 3:
    ```bash
    conda create --name gox-compiler python=3
    ```
    Esto descargará e instalará Python 3 y todas las dependencias necesarias en un entorno aislado.

3. **Activar el entorno virtual**  
    Para activar el entorno virtual, ejecute:
    ```bash
    conda activate gox-compiler
    ```
    Verá que el prompt de su terminal cambia para indicar que el entorno `gox-compiler` está activo.

4. **Instalar dependencias del proyecto**  
    Con el entorno virtual activado, navegue al directorio raíz del proyecto y ejecute:
    ```bash
    pip install -r requirements.txt
    ```
    Esto instalará todas las dependencias necesarias listadas en el archivo `requirements.txt`.

## Ejecución de la aplicación

Para ejecutar la aplicación, asegúrese de estar en el directorio raíz del proyecto y ejecute el siguiente comando:
```bash
python __main__.py <nombre del archivo a usar>
```
Reemplace `<nombre del archivo a usar>` con el nombre del archivo que desea procesar con el compilador GOX. Por ejemplo:
```bash
python __main__.py ejemplo.gox
```
