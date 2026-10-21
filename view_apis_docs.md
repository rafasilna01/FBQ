# Supabase — estrutura para auditoria do app

Use este arquivo para compartilhar a estrutura atual do Supabase e permitir comparar o schema com o código do projeto. Execute as consultas no SQL Editor do projeto Supabase e cole os resultados nas seções abaixo. Todas as consultas são somente de leitura.

**Não cole** chaves (`service_role`, `anon` ou outras), senhas, tokens, URLs com credenciais, dados pessoais, registros de clientes ou linhas de tabelas. Para esta auditoria, precisamos apenas de nomes de objetos, colunas, tipos, constraints, políticas e definições de views.

## Como coletar

1. Abra o SQL Editor do projeto Supabase correto.
2. Execute cada consulta abaixo separadamente.
3. Copie todos os resultados, incluindo cabeçalhos, para a seção correspondente.
4. Se um resultado for extenso, divida-o em partes e mantenha o nome da tabela em cada parte.
5. Não execute comandos `INSERT`, `UPDATE`, `DELETE`, `ALTER`, `DROP` ou `CREATE` durante esta coleta.

## 1. Tabelas, views e RLS

```sql
SELECT
    n.nspname AS schema_name,
    c.relname AS object_name,
    CASE c.relkind
        WHEN 'r' THEN 'table'
        WHEN 'p' THEN 'partitioned table'
        WHEN 'v' THEN 'view'
        WHEN 'm' THEN 'materialized view'
        WHEN 'f' THEN 'foreign table'
        ELSE c.relkind::text
    END AS object_type,
    c.relrowsecurity AS rls_enabled,
    c.relforcerowsecurity AS rls_forced
FROM pg_class AS c
JOIN pg_namespace AS n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relkind IN ('r', 'p', 'v', 'm', 'f')
ORDER BY object_type, object_name;
```

### Resultado

```text
[cole aqui]
```

## 2. Colunas e defaults

```sql
SELECT
    table_schema,
    table_name,
    ordinal_position,
    column_name,
    data_type,
    udt_name,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;
```

### Resultado

```text
[cole aqui]
```

## 3. Primary keys, unique, foreign keys e checks

```sql
SELECT
    tc.table_schema,
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name,
    ccu.table_schema AS referenced_schema,
    ccu.table_name AS referenced_table,
    ccu.column_name AS referenced_column,
    cc.check_clause
FROM information_schema.table_constraints AS tc
LEFT JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_catalog = kcu.constraint_catalog
   AND tc.constraint_schema = kcu.constraint_schema
   AND tc.constraint_name = kcu.constraint_name
   AND tc.table_schema = kcu.table_schema
   AND tc.table_name = kcu.table_name
LEFT JOIN information_schema.constraint_column_usage AS ccu
    ON tc.constraint_catalog = ccu.constraint_catalog
   AND tc.constraint_schema = ccu.constraint_schema
   AND tc.constraint_name = ccu.constraint_name
   AND tc.table_schema = ccu.table_schema
   AND tc.table_name = ccu.table_name
LEFT JOIN information_schema.check_constraints AS cc
    ON tc.constraint_catalog = cc.constraint_catalog
   AND tc.constraint_schema = cc.constraint_schema
   AND tc.constraint_name = cc.constraint_name
WHERE tc.table_schema = 'public'
ORDER BY tc.table_name, tc.constraint_name, kcu.ordinal_position;
```

### Resultado

```text
[cole aqui]
```

## 4. Políticas RLS

```sql
SELECT
    schemaname AS schema_name,
    tablename AS table_name,
    policyname AS policy_name,
    permissive,
    roles,
    cmd AS command,
    qual AS using_expression,
    with_check AS check_expression
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
```

### Resultado

```text
[cole aqui]
```

## 5. Definições de views

```sql
SELECT
    schemaname AS schema_name,
    viewname AS view_name,
    definition
FROM pg_views
WHERE schemaname = 'public'
ORDER BY viewname;
```

### Resultado

```text
[cole aqui]
```

## 6. Índices

```sql
SELECT
    schemaname AS schema_name,
    tablename AS table_name,
    indexname AS index_name,
    indexdef AS index_definition
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
```

### Resultado

```text
[cole aqui]
```

## 7. Contexto da coleta

- Projeto/ambiente (por exemplo, desenvolvimento ou produção; não informe URL nem ID se forem sensíveis):
- Data da coleta:
- Erro ou divergência que motivou a auditoria:
- Tabelas/rotas que precisam de atenção especial:

[preencha aqui]

## Objetos esperados pelo código

O guia operacional atual menciona, entre outros, `user_profiles`, `user_subscriptions_v2`, `marketing_campaigns`, `marketing_coupons`, `fbq_hybrid_orders`, `scanner_telemetry`, `scanner_test_telemetry` e `whalepulse_mempool_signals`. A consulta de objetos acima deve mostrar o que realmente existe no schema, sem presumir que essa lista esteja completa ou atualizada.
