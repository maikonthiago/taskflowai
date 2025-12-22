#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para gerar DATABASE_URL correta com URL encoding de senha
"""

from urllib.parse import quote_plus

print("🔧 GERADOR DE DATABASE_URL COM URL ENCODING")
print("=" * 60)
print("")

# Dados do banco
username = "lobtechsolutions"
password = input("Digite a senha do MySQL: ").strip()
host = "lobtechsolutions.mysql.pythonanywhere-services.com"
database = "lobtechsolutions$lobtechsolutionstaskflowai"

# Fazer URL encoding da senha
password_encoded = quote_plus(password)

# Gerar DATABASE_URL
database_url = f"mysql+pymysql://{username}:{password_encoded}@{host}/{database}"

print("")
print("✅ DATABASE_URL gerada:")
print("")
print(database_url)
print("")
print("=" * 60)
print("📝 Cole esta linha no seu arquivo .env:")
print("")
print(f"DATABASE_URL={database_url}")
print("")
print("⚠️  IMPORTANTE:")
print("   1. Edite o arquivo .env: nano ~/TaskFlowAI/.env")
print("   2. Substitua a linha DATABASE_URL pela linha acima")
print("   3. Salve (Ctrl+O) e saia (Ctrl+X)")
print("   4. Execute novamente: python init_db.py")
print("")
