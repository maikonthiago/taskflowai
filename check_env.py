import sys
import os
import pkg_resources

print("=== DIAGNÓSTICO DE AMBIENTE ===")
print(f"Python Executable: {sys.executable}")
print(f"Current Working Directory: {os.getcwd()}")
print(f"User Home: {os.path.expanduser('~')}")
print("\n=== PATHS ===")
for p in sys.path:
    print(p)

print("\n=== PACOTES INSTALADOS (Flask related) ===")
try:
    for pkg in ['Flask', 'Werkzeug', 'Flask-Login', 'Flask-SQLAlchemy']:
        try:
            version = pkg_resources.get_distribution(pkg).version
            print(f"{pkg}: {version}")
        except pkg_resources.DistributionNotFound:
            print(f"{pkg}: NÃO INSTALADO")
except Exception as e:
    print(f"Erro ao listar pacotes: {e}")
