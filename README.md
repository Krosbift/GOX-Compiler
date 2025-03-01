# GOX-Compiler 👀

## Guía para usar el aplicativo 📝

![Screenshot of a comment on a GitHub issue showing an image, added in the Markdown, of an Octocat smiling and raising a tentacle.](https://github.com/Krosbift/GOX-Compiler.git/assets/images/GOX-compiler.jpg)
### Nota: 
Las siguientes instrucciones, son para manejar un entorno de Miniconda, esto se suele hacer para tener un entorno de desarrollo aislado y no tener problemas con las dependencias de las librerías que se usan en el proyecto, sin embargo, las primeras versiones del proyecto no requieren de ninguna librería externa, por lo que si ya tiene Python instalado con todas las librerías necesarias puede usarlo sin problemas.

    
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
    Verá que el prompt de su terminal (Command Prompt) cambia para indicar que el entorno `gox-compiler` está activo.

4. **Instalar dependencias del proyecto**  
    Con el entorno virtual activado, navegue al directorio raíz del proyecto y ejecute:
    ```bash
    pip install -r requirements.txt
    ```
    Esto instalará todas las dependencias necesarias listadas en el archivo `requirements.txt`.

## Ejecución de la aplicación 🎬

Para ejecutar la aplicación, asegúrese de estar en el directorio raíz del proyecto y ejecute el siguiente comando:
```bash
python __main__.py <ruta del archivo a usar>
```
Reemplace `<ruta del archivo a usar>` con el nombre del archivo que desea procesar con el compilador GOX. Por ejemplo:
```bash
python __main__.py .\factorize.gox
```
## Documentación del proyecto 🗂️

1. **Funcionalidad del código y problemas durante el desarrollo**  
    [Documentación General](docs/DOCUMENTATION.md)  
    Archivo `DOCUMENTATION.md`

2. **Información del versionamiento**  
    [Versiones del proyecto](docs/VERSIONS.md)  
    Archivo `VERSION.md`
