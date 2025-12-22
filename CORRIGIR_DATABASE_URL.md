# 🔧 CORRIGIR ERRO DE CONEXÃO COM MYSQL

## ❌ Problema Identificado

A senha do MySQL (`#Wolf@1902`) contém caracteres especiais (`#` e `@`) que precisam ser **URL-encoded** na string de conexão.

O erro mostra: `Can't connect to MySQL server on '1902@lobtechsolutions.mysql.pythonanywhere-services.com'`

Isso acontece porque o `@` na senha está sendo interpretado como separador de host.

## ✅ Solução

### Opção 1: Usar o Script Automático (RECOMENDADO)

```bash
cd ~/TaskFlowAI
workon taskflowai
python fix_database_url.py
```

O script vai pedir a senha do MySQL e gerar a DATABASE_URL correta com encoding.

### Opção 2: Encoding Manual

Se a senha for `#Wolf@1902`, os caracteres devem ser encoded assim:

- `#` → `%23`
- `@` → `%40`

Resultado: `%23Wolf%401902`

### Opção 3: Editar .env Manualmente

1. **Abrir o arquivo .env:**
```bash
nano ~/TaskFlowAI/.env
```

2. **Encontrar a linha DATABASE_URL e substituir por:**

```env
DATABASE_URL=mysql+pymysql://lobtechsolutions:SUA_SENHA_ENCODED@lobtechsolutions.mysql.pythonanywhere-services.com/lobtechsolutions$lobtechsolutionstaskflowai
```

**Exemplo com a senha `#Wolf@1902` encoded:**
```env
DATABASE_URL=mysql+pymysql://lobtechsolutions:%23Wolf%401902@lobtechsolutions.mysql.pythonanywhere-services.com/lobtechsolutions$lobtechsolutionstaskflowai
```

3. **Salvar:**
   - Pressione `Ctrl+O` (salvar)
   - Pressione `Enter` (confirmar)
   - Pressione `Ctrl+X` (sair)

4. **Testar a conexão:**
```bash
python -c 'from app import db; print(db.engine.url)'
```

5. **Inicializar o banco:**
```bash
python init_db.py
```

## 📋 Tabela de URL Encoding para Caracteres Especiais

| Caractere | URL Encoded |
|-----------|-------------|
| `#`       | `%23`       |
| `@`       | `%40`       |
| `!`       | `%21`       |
| `$`       | `%24`       |
| `%`       | `%25`       |
| `&`       | `%26`       |
| `*`       | `%2A`       |
| `+`       | `%2B`       |
| `/`       | `%2F`       |
| `:`       | `%3A`       |
| `;`       | `%3B`       |
| `=`       | `%3D`       |
| `?`       | `%3F`       |
| `[`       | `%5B`       |
| `]`       | `%5D`       |

## 🧪 Verificar se Funcionou

Após corrigir a DATABASE_URL, execute:

```bash
cd ~/TaskFlowAI
workon taskflowai

# Ver a URL (deve mostrar senha encoded)
python -c 'from app import db; print(db.engine.url)'

# Testar conexão
python -c 'from app import app, db; app.app_context().push(); db.engine.connect(); print("✅ Conexão OK!")'

# Inicializar banco
python init_db.py
```

## 💡 Dica

Se você quiser evitar esse problema no futuro, pode usar uma senha sem caracteres especiais para o banco MySQL, ou sempre lembrar de fazer o URL encoding.
