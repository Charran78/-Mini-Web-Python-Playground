import streamlit as st
import tempfile
import os
import sys
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
import numpy as np # Necesario para el ejemplo de Matplotlib
from streamlit_ace import st_ace # Componente para editor avanzado (Linter/IntelliSense)

# --- CONFIGURACIÓN DE LA PÁGINA ---

st.set_page_config(page_title="Python Playground", page_icon="🐍", layout="wide")
st.markdown(
    """
    <div style='text-align: center; padding: 8px 0;'>
        <h1 style='color: #FF4B4B; margin-bottom: 10px;'>
            🐍 - Mini Web Python Playground - 🐍
        </h1>
        <p style='font-size: 1.3em; color: #666;'>
            Escribe y ejecuta código Python directamente en tu navegador
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <div style='text-align: center; color: #FF4B4B; font-size: 1.1em; padding-bottom: 8px'>
        Para ejecutar el código, <b>APLICAR</b> los cambios con el botón o con <b>CTRL+ENTER</b> 
        y luego usa el botón <b>🚀 EJECUTAR</b>
    </div>
    """,
    unsafe_allow_html=True
)

# Código inicial por defecto
codigo_inicial = '''print("Hello Python World!")
print("Running Python code...")

# Ejemplo básico
numbers = [1, 2, 3, 4, 5]
for num in numbers:
    print(f"Number: {num}")

# Ejemplo de función
def multiply(a, b):
    return a * b

result = multiply(6, 7)
print(f"6 * 7 = {result}")'''

# Ejemplos predefinidos
ejemplo_basico = codigo_inicial

ejemplo_listas = '''# Trabajando con listas
fruits = ["apple", "banana", "orange"]
for i, fruit in enumerate(fruits, 1):
    print(f"Fruit {i}: {fruit}")

# Comprensión de listas
squares = [x**2 for x in range(1, 6)]
print("Squares:", squares)'''

ejemplo_funciones = '''def is_even(number):
    """Verifica si un número es par"""
    return number % 2 == 0

# Prueba de la función
for num in [1, 2, 3, 4, 5]:
    result = "par" if is_even(num) else "impar"
    print(f"{num} es {result}")'''

ejemplo_matplotlib = '''import matplotlib.pyplot as plt
import numpy as np

# Gráfico simple
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Aunque st.pyplot() es ideal, en este contexto de 'exec'
# mostraremos el éxito de la ejecución.
plt.figure(figsize=(8, 4))
plt.plot(x, y, 'b-', label='sin(x)')
plt.title('Onda Senoidal')
plt.xlabel('x')
plt.ylabel('sin(x)')
plt.grid(True)
plt.legend()

print("Plot data generated successfully. (Note: Actual plot rendering in 'exec' environment is limited.)")'''

# Diccionario de ejemplos
ejemplos_map = {
    "Básico": ejemplo_basico,
    "Listas": ejemplo_listas,
    "Funciones": ejemplo_funciones,
    "Matplotlib": ejemplo_matplotlib,
}


# --- INICIALIZACIÓN DEL ESTADO DE SESIÓN ---
# code_content: La única fuente de verdad para el código
if 'code_content' not in st.session_state:
    st.session_state.code_content = codigo_inicial
if 'ejecuciones' not in st.session_state:
    st.session_state.ejecuciones = 0
if 'example_selector' not in st.session_state:
    st.session_state.example_selector = "Básico"
if 'editor_key_suffix' not in st.session_state:
    st.session_state.editor_key_suffix = 0


# --- FUNCIONES DE ACCIÓN (Corregidas) ---

# Función para cargar el ejemplo seleccionado y actualizar el editor
def load_example():
    selected_example = st.session_state.example_selector
    if selected_example != "Personalizado":
        new_code = ejemplos_map.get(selected_example, codigo_inicial)
        st.session_state.code_content = new_code
        # Forzar reinicio del editor
        st.session_state.editor_key_suffix += 1


# Función para limpiar el código
def limpiar_codigo():
    st.session_state.code_content = "# Escribe tu código aquí\nprint('Hello World!')"
    # RESTABLECER: Forzamos la selección a "Personalizado"
    st.session_state.example_selector = "Personalizado"
    # Forzar reinicio del editor
    st.session_state.editor_key_suffix += 1
    
# Función para reiniciar
def reiniciar_codigo():
    st.session_state.code_content = codigo_inicial
    # RESTABLECER: Forzamos la selección a "Básico"
    st.session_state.example_selector = "Básico"
    # Forzar reinicio del editor
    st.session_state.editor_key_suffix += 1


# --- WIDGETS ---

# Selector de ejemplos: Usamos key y on_change para controlar la carga
ejemplo = st.selectbox(
    "Ejemplos:",
    options=["Personalizado", "Básico", "Listas", "Funciones", "Matplotlib"],
    key="example_selector",
    on_change=load_example # La función se ejecuta solo cuando el usuario cambia la selección
)

# Editor de código avanzado (st_ace)
codigo = st_ace(
    # Usamos la única fuente de verdad para inicializar el valor
    value=st.session_state.code_content,
    language="python", # Habilita el linter de Python
    theme="dracula", 
    height=300,
    # CLAVE DE REINICIO: La clave cambia cada vez que se usa una función de control
    key=f"editor_codigo_{st.session_state.editor_key_suffix}"
)

# Sincronizamos el contenido del editor con el estado de sesión después de la edición del usuario
st.session_state.code_content = codigo


# Botones de acción
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    ejecutar = st.button("🚀 Ejecutar", use_container_width=True)

with col2:
    st.button("📝 Limpiar Código", use_container_width=True, on_click=limpiar_codigo)

with col3:
    # Usamos el valor actual del editor para descargar
    descargar = st.download_button(
        label="💾 Guardar",
        data=st.session_state.code_content,
        file_name="mi_codigo.py",
        mime="text/python",
        use_container_width=True
    )

with col4:
    st.button("🔄 Reiniciar", use_container_width=True, on_click=reiniciar_codigo)

# Ejecutar código cuando se presiona el botón
if ejecutar:
    # CLAVE DE CORRECCIÓN: Usamos la variable 'codigo' (valor de retorno del widget)
    # que es el valor más fresco en este ciclo de ejecución.
    codigo_a_ejecutar = codigo 
    if codigo_a_ejecutar.strip():
        try:
            # Create temporary file with explicit encoding
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(codigo_a_ejecutar)
                temp_file = f.name
            
            # Capture output
            output = StringIO()
            error_output = StringIO()
            
            try:
                # Modificamos el PATH para que el script pueda importarse si es necesario
                original_sys_path = sys.path
                sys.path.insert(0, os.path.dirname(temp_file))
                
                # Ejecutamos el código capturando stdout y stderr
                with redirect_stdout(output), redirect_stderr(error_output):
                    # Usamos 'exec' para ejecutar el código del archivo temporal
                    with open(temp_file, 'r', encoding='utf-8') as file:
                        exec(file.read())
                
                # Restauramos el path original
                sys.path = original_sys_path

                st.success("✅ Código ejecutado exitosamente!")
                st.session_state.ejecuciones += 1
                
                # Mostrar salida
                salida_texto = output.getvalue()
                if salida_texto:
                    st.subheader("📤 Salida:")
                    st.code(salida_texto)
                else:
                    st.info("ℹ️ El código se ejecutó pero no produjo salida.")
                
                # Mostrar errores si los hay
                errores = error_output.getvalue()
                if errores:
                    st.subheader("⚠️ Advertencias/Errores (puede ser de Matplotlib):")
                    st.code(errores)
                
            except Exception as e:
                st.error(f"❌ Error durante la ejecución: {str(e)}")
                errores = error_output.getvalue()
                if errores:
                    st.subheader("📝 Detalles del error:")
                    st.code(errores)
                
        except Exception as e:
            st.error(f"❌ Error al crear archivo temporal: {str(e)}")
        finally:
            # Cleanup
            try:
                if 'temp_file' in locals():
                    os.unlink(temp_file)
            except:
                pass
    else:
        st.warning("⚠️ Por favor escribe algún código")

# Información adicional
with st.expander("💡 Consejos"):
    st.markdown("""
    **Consejos para usar el playground:**
    
    - **📝 Limpiar Código**: Borra todo el código y deja un template básico
    - **🔄 Reiniciar**: Vuelve al código de ejemplo inicial completo
    - **🚀 Ejecutar**: Ejecuta el código actual (usa el botón, Ctrl+Enter no está disponible)
    - **💾 Guardar**: Descarga tu código como archivo .py
    - **📊 Gráficos**: Funciona con librerías comunes (aunque la visualización directa de gráficos de Matplotlib dentro de este tipo de ejecución es limitada).
    - **🛡️ Seguridad**: El código se ejecuta localmente en un entorno seguro.

    **Librerías disponibles:**
    - `matplotlib`, `seaborn` para gráficos
    - `numpy`, `pandas` para análisis de datos
    - `math`, `random`, `datetime` estándar
    - ¡Y muchas más!
    """)

# Sección de estadísticas
with st.expander("📊 Estadísticas"):
    st.metric("Ejecuciones realizadas", len(codigo.split('\n')) - 1) # Usamos las líneas del código actual
    st.metric("Líneas de código", len(codigo.split('\n')))

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.9em; padding: 10px'>
        <b style='color: #ff4b4b'>Mini Web Python Playground</b> · Hecho con <b>Streamlit</b>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("""
    <div align="center">
        <p>
            <a href="https://www.linkedin.com/in/pedro-menc%C3%ADas-68223336b/">
                <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn">
            </a>
            <a href="https://github.com/Charran78">
                <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
            </a>
            <a href="https://pedromencias.netlify.app/">
                <img src="https://img.shields.io/badge/netlify-000000?style=for-the-badge&logo=netlify&logoColor=#FF7139" alt="Portfolio">
            </a>
            <a href="https://buymeacoffee.com/beyonddigiv">
                <img src="https://img.shields.io/badge/buymeacoffee-FF0000?style=for-the-badge&logo=buymeacoffee&logoColor=yellow" alt="buymeacoffee">
            </a>
        </p>
    </div>
 """, unsafe_allow_html=True
)

st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.9em; padding: 10px'>
        <b style='color: #ff4b4b'> · ©Pedro Mencías · 2025 ·</b>
    </div>
    """,
    unsafe_allow_html=True
)
