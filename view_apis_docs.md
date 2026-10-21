# Supabase — estrutura para auditoria do app

Use este arquivo para compartilhar a estrutura atual do Supabase e permitir comparar o schema com o código do projeto. Execute as consultas no SQL Editor do projeto Supabase e cole os resultados nas seções abaixo. Todas as consultas são somente de leitura.

**Não cole** chaves (`service_role`, `anon` ou outras), senhas, tokens, URLs com credenciais, dados pessoais, registros de clientes ou linhas de tabelas. Para esta auditoria, precisamos apenas de nomes de objetos, colunas, tipos, constraints, políticas e definições de views.

## Status da coleta recebida em 21/10/2026

Foram coladas as colunas da documentação do Supabase para 12 objetos: `client_exchange_credentials`, `fbq_hybrid_orders`, `investor_performance_ledgers`, `marketing_campaigns`, `marketing_coupons`, `painel_realtime`, `scanner_telemetry`, `scanner_test_telemetry`, `user_profiles`, `user_subscriptions_v2`, `view_active_subscriptions` e `whalepulse_mempool_signals`. Isso permite comparar nomes/tipos, mas não prova defaults, nulabilidade, PKs, FKs, índices ou grants reais. A definição SQL das views e as políticas RLS também não foram incluídas. Para fechar esses pontos, execute e cole os resultados das seções 1 a 6.

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
    column_default,
    is_identity,
    identity_generation
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

### Privilégios efetivos nos objetos de tabela/view

```sql
SELECT
    n.nspname AS schema_name,
    c.relname AS object_name,
    CASE WHEN acl.grantee = 0 THEN 'PUBLIC' ELSE r.rolname END AS grantee,
    acl.privilege_type,
    acl.is_grantable
FROM pg_class AS c
JOIN pg_namespace AS n ON n.oid = c.relnamespace
CROSS JOIN LATERAL aclexplode(
    COALESCE(c.relacl, acldefault('r', c.relowner))
) AS acl
LEFT JOIN pg_roles AS r ON r.oid = acl.grantee
WHERE n.nspname = 'public'
  AND c.relkind IN ('r', 'p', 'v', 'm', 'f')
ORDER BY object_name, grantee, acl.privilege_type;
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

segue as tabela do supabase atualizadas em 21/10/2026 as 09:16

client_exchange_credentials
No description available


Language: Javascript
Columns

Name	Format	Type	Description
id	
bigint

number	
user_slug	
character varying

string	
binance_client_api_key	
text

string	
binance_client_api_secret	
text

string	
updated_at	
timestamp with time zone

string	
Read rows
Documentation
To read rows in this table, use the select method.

Read all rows

let { data: client_exchange_credentials, error } = await supabase
  .from('client_exchange_credentials')
  .select('*')
Read specific columns

let { data: client_exchange_credentials, error } = await supabase
  .from('client_exchange_credentials')
  .select('some_column,other_column')
Read referenced tables

let { data: client_exchange_credentials, error } = await supabase
  .from('client_exchange_credentials')
  .select(`
    some_column,
    other_table (
      foreign_key
    )
  `)
With pagination

let { data: client_exchange_credentials, error } = await supabase
  .from('client_exchange_credentials')
  .select('*')
  .range(0, 9)
Filtering
Documentation
Supabase provides a wide range of filters

With filtering

let { data: client_exchange_credentials, error } = await supabase
  .from('client_exchange_credentials')
  .select("*")

  // Filters
  .eq('column', 'Equal to')
  .gt('column', 'Greater than')
  .lt('column', 'Less than')
  .gte('column', 'Greater than or equal to')
  .lte('column', 'Less than or equal to')
  .like('column', '%CaseSensitive%')
  .ilike('column', '%CaseInsensitive%')
  .is('column', null)
  .in('column', ['Array', 'Values'])
  .neq('column', 'Not equal to')

  // Arrays
  .contains('array_column', ['array', 'contains'])
  .containedBy('array_column', ['contained', 'by'])

  // Logical operators
  .not('column', 'like', 'Negate filter')
  .or('some_column.eq.Some value, other_column.eq.Other value')
Insert rows
Documentation
insert lets you insert into your tables. You can also insert in bulk and do UPSERT.

insert will also return the replaced values for UPSERT.

Insert a row

const { data, error } = await supabase
  .from('client_exchange_credentials')
  .insert([
    { some_column: 'someValue', other_column: 'otherValue' },
  ])
  .select()
Insert many rows

const { data, error } = await supabase
  .from('client_exchange_credentials')
  .insert([
    { some_column: 'someValue' },
    { some_column: 'otherValue' },
  ])
  .select()
Upsert matching rows

const { data, error } = await supabase
  .from('client_exchange_credentials')
  .upsert({ some_column: 'someValue' })
  .select()
Update rows
Documentation
update lets you update rows. update will match all rows by default. You can update specific rows using horizontal filters, e.g. eq, lt, and is.

update will also return the replaced values for UPDATE.

Update matching rows

const { data, error } = await supabase
  .from('client_exchange_credentials')
  .update({ other_column: 'otherValue' })
  .eq('some_column', 'someValue')
  .select()
Delete rows
Documentation
delete lets you delete rows. delete will match all rows by default, so remember to specify your filters!

Delete matching rows

const { error } = await supabase
  .from('client_exchange_credentials')
  .delete()
  .eq('some_column', 'someValue')
Subscribe to changes
Documentation
Supabase provides realtime functionality and broadcasts database changes to authorized users depending on Row Level Security (RLS) policies.

Subscribe to all events

const channels = supabase.channel('custom-all-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'client_exchange_credentials' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to inserts

const channels = supabase.channel('custom-insert-channel')
  .on(
    'postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'client_exchange_credentials' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to updates

const channels = supabase.channel('custom-update-channel')
  .on(
    'postgres_changes',
    { event: 'UPDATE', schema: 'public', table: 'client_exchange_credentials' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to deletes

const channels = supabase.channel('custom-delete-channel')
  .on(
    'postgres_changes',
    { event: 'DELETE', schema: 'public', table: 'client_exchange_credentials' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to specific rows

const channels = supabase.channel('custom-filter-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'client_exchange_credentials', filter: 'some_column=eq.some_value' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()

  fbq_hybrid_orders
No description available


Language: Javascript
Columns

Name	Format	Type	Description
ticker	
character varying

string	
current_price	
numeric

number	
price_change_percent	
numeric

number	
regime_detectado	
character varying

string	
volume_mempool	
numeric

number	
kelly_leverage	
integer

number	
target_price_34	
numeric

number	
target_price_60	
numeric

number	
break_even_price	
numeric

number	
risk_slider_pos	
numeric

number	
updated_at	
timestamp with time zone

string	
market_updated_at	
timestamp with time zone

string	
Read rows
Documentation
To read rows in this table, use the select method.

Read all rows

let { data: fbq_hybrid_orders, error } = await supabase
  .from('fbq_hybrid_orders')
  .select('*')
Read specific columns

let { data: fbq_hybrid_orders, error } = await supabase
  .from('fbq_hybrid_orders')
  .select('some_column,other_column')
Read referenced tables

let { data: fbq_hybrid_orders, error } = await supabase
  .from('fbq_hybrid_orders')
  .select(`
    some_column,
    other_table (
      foreign_key
    )
  `)
With pagination

let { data: fbq_hybrid_orders, error } = await supabase
  .from('fbq_hybrid_orders')
  .select('*')
  .range(0, 9)
Filtering
Documentation
Supabase provides a wide range of filters

With filtering

let { data: fbq_hybrid_orders, error } = await supabase
  .from('fbq_hybrid_orders')
  .select("*")

  // Filters
  .eq('column', 'Equal to')
  .gt('column', 'Greater than')
  .lt('column', 'Less than')
  .gte('column', 'Greater than or equal to')
  .lte('column', 'Less than or equal to')
  .like('column', '%CaseSensitive%')
  .ilike('column', '%CaseInsensitive%')
  .is('column', null)
  .in('column', ['Array', 'Values'])
  .neq('column', 'Not equal to')

  // Arrays
  .contains('array_column', ['array', 'contains'])
  .containedBy('array_column', ['contained', 'by'])

  // Logical operators
  .not('column', 'like', 'Negate filter')
  .or('some_column.eq.Some value, other_column.eq.Other value')
Insert rows
Documentation
insert lets you insert into your tables. You can also insert in bulk and do UPSERT.

insert will also return the replaced values for UPSERT.

Insert a row

const { data, error } = await supabase
  .from('fbq_hybrid_orders')
  .insert([
    { some_column: 'someValue', other_column: 'otherValue' },
  ])
  .select()
Insert many rows

const { data, error } = await supabase
  .from('fbq_hybrid_orders')
  .insert([
    { some_column: 'someValue' },
    { some_column: 'otherValue' },
  ])
  .select()
Upsert matching rows

const { data, error } = await supabase
  .from('fbq_hybrid_orders')
  .upsert({ some_column: 'someValue' })
  .select()
Update rows
Documentation
update lets you update rows. update will match all rows by default. You can update specific rows using horizontal filters, e.g. eq, lt, and is.

update will also return the replaced values for UPDATE.

Update matching rows

const { data, error } = await supabase
  .from('fbq_hybrid_orders')
  .update({ other_column: 'otherValue' })
  .eq('some_column', 'someValue')
  .select()
Delete rows
Documentation
delete lets you delete rows. delete will match all rows by default, so remember to specify your filters!

Delete matching rows

const { error } = await supabase
  .from('fbq_hybrid_orders')
  .delete()
  .eq('some_column', 'someValue')
Subscribe to changes
Documentation
Supabase provides realtime functionality and broadcasts database changes to authorized users depending on Row Level Security (RLS) policies.

Subscribe to all events

const channels = supabase.channel('custom-all-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'fbq_hybrid_orders' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to inserts

const channels = supabase.channel('custom-insert-channel')
  .on(
    'postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'fbq_hybrid_orders' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to updates

const channels = supabase.channel('custom-update-channel')
  .on(
    'postgres_changes',
    { event: 'UPDATE', schema: 'public', table: 'fbq_hybrid_orders' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to deletes

const channels = supabase.channel('custom-delete-channel')
  .on(
    'postgres_changes',
    { event: 'DELETE', schema: 'public', table: 'fbq_hybrid_orders' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to specific rows

const channels = supabase.channel('custom-filter-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'fbq_hybrid_orders', filter: 'some_column=eq.some_value' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()

  investor_performance_ledgers
No description available


Language: Javascript
Columns

Name	Format	Type	Description
id	
bigint

number	
user_slug	
character varying

string	
current_balance_usd	
numeric

number	
high_water_mark_usd	
numeric

number	
performance_fee_owed_usd	
numeric

number	
hard_cap_breached	
boolean

boolean	
updated_at	
timestamp with time zone

string	
Read rows
Documentation
To read rows in this table, use the select method.

Read all rows

let { data: investor_performance_ledgers, error } = await supabase
  .from('investor_performance_ledgers')
  .select('*')
Read specific columns

let { data: investor_performance_ledgers, error } = await supabase
  .from('investor_performance_ledgers')
  .select('some_column,other_column')
Read referenced tables

let { data: investor_performance_ledgers, error } = await supabase
  .from('investor_performance_ledgers')
  .select(`
    some_column,
    other_table (
      foreign_key
    )
  `)
With pagination

let { data: investor_performance_ledgers, error } = await supabase
  .from('investor_performance_ledgers')
  .select('*')
  .range(0, 9)
Filtering
Documentation
Supabase provides a wide range of filters

With filtering

let { data: investor_performance_ledgers, error } = await supabase
  .from('investor_performance_ledgers')
  .select("*")

  // Filters
  .eq('column', 'Equal to')
  .gt('column', 'Greater than')
  .lt('column', 'Less than')
  .gte('column', 'Greater than or equal to')
  .lte('column', 'Less than or equal to')
  .like('column', '%CaseSensitive%')
  .ilike('column', '%CaseInsensitive%')
  .is('column', null)
  .in('column', ['Array', 'Values'])
  .neq('column', 'Not equal to')

  // Arrays
  .contains('array_column', ['array', 'contains'])
  .containedBy('array_column', ['contained', 'by'])

  // Logical operators
  .not('column', 'like', 'Negate filter')
  .or('some_column.eq.Some value, other_column.eq.Other value')
Insert rows
Documentation
insert lets you insert into your tables. You can also insert in bulk and do UPSERT.

insert will also return the replaced values for UPSERT.

Insert a row

const { data, error } = await supabase
  .from('investor_performance_ledgers')
  .insert([
    { some_column: 'someValue', other_column: 'otherValue' },
  ])
  .select()
Insert many rows

const { data, error } = await supabase
  .from('investor_performance_ledgers')
  .insert([
    { some_column: 'someValue' },
    { some_column: 'otherValue' },
  ])
  .select()
Upsert matching rows

const { data, error } = await supabase
  .from('investor_performance_ledgers')
  .upsert({ some_column: 'someValue' })
  .select()
Update rows
Documentation
update lets you update rows. update will match all rows by default. You can update specific rows using horizontal filters, e.g. eq, lt, and is.

update will also return the replaced values for UPDATE.

Update matching rows

const { data, error } = await supabase
  .from('investor_performance_ledgers')
  .update({ other_column: 'otherValue' })
  .eq('some_column', 'someValue')
  .select()
Delete rows
Documentation
delete lets you delete rows. delete will match all rows by default, so remember to specify your filters!

Delete matching rows

const { error } = await supabase
  .from('investor_performance_ledgers')
  .delete()
  .eq('some_column', 'someValue')
Subscribe to changes
Documentation
Supabase provides realtime functionality and broadcasts database changes to authorized users depending on Row Level Security (RLS) policies.

Subscribe to all events

const channels = supabase.channel('custom-all-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'investor_performance_ledgers' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to inserts

const channels = supabase.channel('custom-insert-channel')
  .on(
    'postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'investor_performance_ledgers' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to updates

const channels = supabase.channel('custom-update-channel')
  .on(
    'postgres_changes',
    { event: 'UPDATE', schema: 'public', table: 'investor_performance_ledgers' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to deletes

const channels = supabase.channel('custom-delete-channel')
  .on(
    'postgres_changes',
    { event: 'DELETE', schema: 'public', table: 'investor_performance_ledgers' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to specific rows

const channels = supabase.channel('custom-filter-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'investor_performance_ledgers', filter: 'some_column=eq.some_value' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()

  marketing_campaigns
No description available


Language: Javascript
Columns

Name	Format	Type	Description
campaign_slug	
character varying

string	
campaign_name	
character varying

string	
monthly_fee	
numeric

number	
renewal_fee_text	
character varying

string	
duration_days	
integer

number	
allowed_crypto_count	
integer

number	
authorized_cryptocurrencies	
text[]

array	
hidden_plan	
boolean

boolean	
created_at	
timestamp with time zone

string	
Read rows
Documentation
To read rows in this table, use the select method.

Read all rows

let { data: marketing_campaigns, error } = await supabase
  .from('marketing_campaigns')
  .select('*')
Read specific columns

let { data: marketing_campaigns, error } = await supabase
  .from('marketing_campaigns')
  .select('some_column,other_column')
Read referenced tables

let { data: marketing_campaigns, error } = await supabase
  .from('marketing_campaigns')
  .select(`
    some_column,
    other_table (
      foreign_key
    )
  `)
With pagination

let { data: marketing_campaigns, error } = await supabase
  .from('marketing_campaigns')
  .select('*')
  .range(0, 9)
Filtering
Documentation
Supabase provides a wide range of filters

With filtering

let { data: marketing_campaigns, error } = await supabase
  .from('marketing_campaigns')
  .select("*")

  // Filters
  .eq('column', 'Equal to')
  .gt('column', 'Greater than')
  .lt('column', 'Less than')
  .gte('column', 'Greater than or equal to')
  .lte('column', 'Less than or equal to')
  .like('column', '%CaseSensitive%')
  .ilike('column', '%CaseInsensitive%')
  .is('column', null)
  .in('column', ['Array', 'Values'])
  .neq('column', 'Not equal to')

  // Arrays
  .contains('array_column', ['array', 'contains'])
  .containedBy('array_column', ['contained', 'by'])

  // Logical operators
  .not('column', 'like', 'Negate filter')
  .or('some_column.eq.Some value, other_column.eq.Other value')
Insert rows
Documentation
insert lets you insert into your tables. You can also insert in bulk and do UPSERT.

insert will also return the replaced values for UPSERT.

Insert a row

const { data, error } = await supabase
  .from('marketing_campaigns')
  .insert([
    { some_column: 'someValue', other_column: 'otherValue' },
  ])
  .select()
Insert many rows

const { data, error } = await supabase
  .from('marketing_campaigns')
  .insert([
    { some_column: 'someValue' },
    { some_column: 'otherValue' },
  ])
  .select()
Upsert matching rows

const { data, error } = await supabase
  .from('marketing_campaigns')
  .upsert({ some_column: 'someValue' })
  .select()
Update rows
Documentation
update lets you update rows. update will match all rows by default. You can update specific rows using horizontal filters, e.g. eq, lt, and is.

update will also return the replaced values for UPDATE.

Update matching rows

const { data, error } = await supabase
  .from('marketing_campaigns')
  .update({ other_column: 'otherValue' })
  .eq('some_column', 'someValue')
  .select()
Delete rows
Documentation
delete lets you delete rows. delete will match all rows by default, so remember to specify your filters!

Delete matching rows

const { error } = await supabase
  .from('marketing_campaigns')
  .delete()
  .eq('some_column', 'someValue')
Subscribe to changes
Documentation
Supabase provides realtime functionality and broadcasts database changes to authorized users depending on Row Level Security (RLS) policies.

Subscribe to all events

const channels = supabase.channel('custom-all-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'marketing_campaigns' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to inserts

const channels = supabase.channel('custom-insert-channel')
  .on(
    'postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'marketing_campaigns' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to updates

const channels = supabase.channel('custom-update-channel')
  .on(
    'postgres_changes',
    { event: 'UPDATE', schema: 'public', table: 'marketing_campaigns' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to deletes

const channels = supabase.channel('custom-delete-channel')
  .on(
    'postgres_changes',
    { event: 'DELETE', schema: 'public', table: 'marketing_campaigns' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to specific rows

const channels = supabase.channel('custom-filter-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'marketing_campaigns', filter: 'some_column=eq.some_value' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()

  marketing_coupons
No description available


Language: Javascript
Columns

Name	Format	Type	Description
id	
bigint

number	
coupon_code	
character varying

string	
discount_percent	
numeric

number	
discount_fixed	
numeric

number	
is_active	
boolean

boolean	
created_at	
timestamp with time zone

string	
Read rows
Documentation
To read rows in this table, use the select method.

Read all rows

let { data: marketing_coupons, error } = await supabase
  .from('marketing_coupons')
  .select('*')
Read specific columns

let { data: marketing_coupons, error } = await supabase
  .from('marketing_coupons')
  .select('some_column,other_column')
Read referenced tables

let { data: marketing_coupons, error } = await supabase
  .from('marketing_coupons')
  .select(`
    some_column,
    other_table (
      foreign_key
    )
  `)
With pagination

let { data: marketing_coupons, error } = await supabase
  .from('marketing_coupons')
  .select('*')
  .range(0, 9)
Filtering
Documentation
Supabase provides a wide range of filters

With filtering

let { data: marketing_coupons, error } = await supabase
  .from('marketing_coupons')
  .select("*")

  // Filters
  .eq('column', 'Equal to')
  .gt('column', 'Greater than')
  .lt('column', 'Less than')
  .gte('column', 'Greater than or equal to')
  .lte('column', 'Less than or equal to')
  .like('column', '%CaseSensitive%')
  .ilike('column', '%CaseInsensitive%')
  .is('column', null)
  .in('column', ['Array', 'Values'])
  .neq('column', 'Not equal to')

  // Arrays
  .contains('array_column', ['array', 'contains'])
  .containedBy('array_column', ['contained', 'by'])

  // Logical operators
  .not('column', 'like', 'Negate filter')
  .or('some_column.eq.Some value, other_column.eq.Other value')
Insert rows
Documentation
insert lets you insert into your tables. You can also insert in bulk and do UPSERT.

insert will also return the replaced values for UPSERT.

Insert a row

const { data, error } = await supabase
  .from('marketing_coupons')
  .insert([
    { some_column: 'someValue', other_column: 'otherValue' },
  ])
  .select()
Insert many rows

const { data, error } = await supabase
  .from('marketing_coupons')
  .insert([
    { some_column: 'someValue' },
    { some_column: 'otherValue' },
  ])
  .select()
Upsert matching rows

const { data, error } = await supabase
  .from('marketing_coupons')
  .upsert({ some_column: 'someValue' })
  .select()
Update rows
Documentation
update lets you update rows. update will match all rows by default. You can update specific rows using horizontal filters, e.g. eq, lt, and is.

update will also return the replaced values for UPDATE.

Update matching rows

const { data, error } = await supabase
  .from('marketing_coupons')
  .update({ other_column: 'otherValue' })
  .eq('some_column', 'someValue')
  .select()
Delete rows
Documentation
delete lets you delete rows. delete will match all rows by default, so remember to specify your filters!

Delete matching rows

const { error } = await supabase
  .from('marketing_coupons')
  .delete()
  .eq('some_column', 'someValue')
Subscribe to changes
Documentation
Supabase provides realtime functionality and broadcasts database changes to authorized users depending on Row Level Security (RLS) policies.

Subscribe to all events

const channels = supabase.channel('custom-all-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'marketing_coupons' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to inserts

const channels = supabase.channel('custom-insert-channel')
  .on(
    'postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'marketing_coupons' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to updates

const channels = supabase.channel('custom-update-channel')
  .on(
    'postgres_changes',
    { event: 'UPDATE', schema: 'public', table: 'marketing_coupons' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to deletes

const channels = supabase.channel('custom-delete-channel')
  .on(
    'postgres_changes',
    { event: 'DELETE', schema: 'public', table: 'marketing_coupons' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to specific rows

const channels = supabase.channel('custom-filter-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'marketing_coupons', filter: 'some_column=eq.some_value' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()

  painel_realtime
No description available


Language: Javascript
Columns

Name	Format	Type	Description
ticker	
character varying

string	
current_price	
numeric

number	
price_change_percent	
numeric

number	
regime_detectado	
character varying

string	
volume_mempool	
numeric

number	
kelly_leverage	
integer

number	
target_price_34	
numeric

number	
target_price_60	
numeric

number	
break_even_price	
numeric

number	
risk_slider_pos	
numeric

number	
updated_at	
timestamp with time zone

string	
market_updated_at	
timestamp with time zone

string	
Read rows
Documentation
To read rows in this table, use the select method.

Read all rows

let { data: painel_realtime, error } = await supabase
  .from('painel_realtime')
  .select('*')
Read specific columns

let { data: painel_realtime, error } = await supabase
  .from('painel_realtime')
  .select('some_column,other_column')
Read referenced tables

let { data: painel_realtime, error } = await supabase
  .from('painel_realtime')
  .select(`
    some_column,
    other_table (
      foreign_key
    )
  `)
With pagination

let { data: painel_realtime, error } = await supabase
  .from('painel_realtime')
  .select('*')
  .range(0, 9)
Filtering
Documentation
Supabase provides a wide range of filters

With filtering

let { data: painel_realtime, error } = await supabase
  .from('painel_realtime')
  .select("*")

  // Filters
  .eq('column', 'Equal to')
  .gt('column', 'Greater than')
  .lt('column', 'Less than')
  .gte('column', 'Greater than or equal to')
  .lte('column', 'Less than or equal to')
  .like('column', '%CaseSensitive%')
  .ilike('column', '%CaseInsensitive%')
  .is('column', null)
  .in('column', ['Array', 'Values'])
  .neq('column', 'Not equal to')

  // Arrays
  .contains('array_column', ['array', 'contains'])
  .containedBy('array_column', ['contained', 'by'])

  // Logical operators
  .not('column', 'like', 'Negate filter')
  .or('some_column.eq.Some value, other_column.eq.Other value')
Insert rows
Documentation
insert lets you insert into your tables. You can also insert in bulk and do UPSERT.

insert will also return the replaced values for UPSERT.

Insert a row

const { data, error } = await supabase
  .from('painel_realtime')
  .insert([
    { some_column: 'someValue', other_column: 'otherValue' },
  ])
  .select()
Insert many rows

const { data, error } = await supabase
  .from('painel_realtime')
  .insert([
    { some_column: 'someValue' },
    { some_column: 'otherValue' },
  ])
  .select()
Upsert matching rows

const { data, error } = await supabase
  .from('painel_realtime')
  .upsert({ some_column: 'someValue' })
  .select()
Update rows
Documentation
update lets you update rows. update will match all rows by default. You can update specific rows using horizontal filters, e.g. eq, lt, and is.

update will also return the replaced values for UPDATE.

Update matching rows

const { data, error } = await supabase
  .from('painel_realtime')
  .update({ other_column: 'otherValue' })
  .eq('some_column', 'someValue')
  .select()
Delete rows
Documentation
delete lets you delete rows. delete will match all rows by default, so remember to specify your filters!

Delete matching rows

const { error } = await supabase
  .from('painel_realtime')
  .delete()
  .eq('some_column', 'someValue')
Subscribe to changes
Documentation
Supabase provides realtime functionality and broadcasts database changes to authorized users depending on Row Level Security (RLS) policies.

Subscribe to all events

const channels = supabase.channel('custom-all-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'painel_realtime' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to inserts

const channels = supabase.channel('custom-insert-channel')
  .on(
    'postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'painel_realtime' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to updates

const channels = supabase.channel('custom-update-channel')
  .on(
    'postgres_changes',
    { event: 'UPDATE', schema: 'public', table: 'painel_realtime' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to deletes

const channels = supabase.channel('custom-delete-channel')
  .on(
    'postgres_changes',
    { event: 'DELETE', schema: 'public', table: 'painel_realtime' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to specific rows

const channels = supabase.channel('custom-filter-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'painel_realtime', filter: 'some_column=eq.some_value' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()

  scanner_telemetry
No description available


Language: Javascript
Columns

Name	Format	Type	Description
ticker	
text

string	
payload	
jsonb

json	
updated_at	
timestamp with time zone

string	
Read rows
Documentation
To read rows in this table, use the select method.

Read all rows

let { data: scanner_telemetry, error } = await supabase
  .from('scanner_telemetry')
  .select('*')
Read specific columns

let { data: scanner_telemetry, error } = await supabase
  .from('scanner_telemetry')
  .select('some_column,other_column')
Read referenced tables

let { data: scanner_telemetry, error } = await supabase
  .from('scanner_telemetry')
  .select(`
    some_column,
    other_table (
      foreign_key
    )
  `)
With pagination

let { data: scanner_telemetry, error } = await supabase
  .from('scanner_telemetry')
  .select('*')
  .range(0, 9)
Filtering
Documentation
Supabase provides a wide range of filters

With filtering

let { data: scanner_telemetry, error } = await supabase
  .from('scanner_telemetry')
  .select("*")

  // Filters
  .eq('column', 'Equal to')
  .gt('column', 'Greater than')
  .lt('column', 'Less than')
  .gte('column', 'Greater than or equal to')
  .lte('column', 'Less than or equal to')
  .like('column', '%CaseSensitive%')
  .ilike('column', '%CaseInsensitive%')
  .is('column', null)
  .in('column', ['Array', 'Values'])
  .neq('column', 'Not equal to')

  // Arrays
  .contains('array_column', ['array', 'contains'])
  .containedBy('array_column', ['contained', 'by'])

  // Logical operators
  .not('column', 'like', 'Negate filter')
  .or('some_column.eq.Some value, other_column.eq.Other value')
Insert rows
Documentation
insert lets you insert into your tables. You can also insert in bulk and do UPSERT.

insert will also return the replaced values for UPSERT.

Insert a row

const { data, error } = await supabase
  .from('scanner_telemetry')
  .insert([
    { some_column: 'someValue', other_column: 'otherValue' },
  ])
  .select()
Insert many rows

const { data, error } = await supabase
  .from('scanner_telemetry')
  .insert([
    { some_column: 'someValue' },
    { some_column: 'otherValue' },
  ])
  .select()
Upsert matching rows

const { data, error } = await supabase
  .from('scanner_telemetry')
  .upsert({ some_column: 'someValue' })
  .select()
Update rows
Documentation
update lets you update rows. update will match all rows by default. You can update specific rows using horizontal filters, e.g. eq, lt, and is.

update will also return the replaced values for UPDATE.

Update matching rows

const { data, error } = await supabase
  .from('scanner_telemetry')
  .update({ other_column: 'otherValue' })
  .eq('some_column', 'someValue')
  .select()
Delete rows
Documentation
delete lets you delete rows. delete will match all rows by default, so remember to specify your filters!

Delete matching rows

const { error } = await supabase
  .from('scanner_telemetry')
  .delete()
  .eq('some_column', 'someValue')
Subscribe to changes
Documentation
Supabase provides realtime functionality and broadcasts database changes to authorized users depending on Row Level Security (RLS) policies.

Subscribe to all events

const channels = supabase.channel('custom-all-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'scanner_telemetry' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to inserts

const channels = supabase.channel('custom-insert-channel')
  .on(
    'postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'scanner_telemetry' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to updates

const channels = supabase.channel('custom-update-channel')
  .on(
    'postgres_changes',
    { event: 'UPDATE', schema: 'public', table: 'scanner_telemetry' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to deletes

const channels = supabase.channel('custom-delete-channel')
  .on(
    'postgres_changes',
    { event: 'DELETE', schema: 'public', table: 'scanner_telemetry' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to specific rows

const channels = supabase.channel('custom-filter-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'scanner_telemetry', filter: 'some_column=eq.some_value' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()

  scanner_test_telemetry
No description available


Language: Javascript
Columns

Name	Format	Type	Description
ticker	
text

string	
payload	
jsonb

json	
updated_at	
timestamp with time zone

string	
Read rows
Documentation
To read rows in this table, use the select method.

Read all rows

let { data: scanner_test_telemetry, error } = await supabase
  .from('scanner_test_telemetry')
  .select('*')
Read specific columns

let { data: scanner_test_telemetry, error } = await supabase
  .from('scanner_test_telemetry')
  .select('some_column,other_column')
Read referenced tables

let { data: scanner_test_telemetry, error } = await supabase
  .from('scanner_test_telemetry')
  .select(`
    some_column,
    other_table (
      foreign_key
    )
  `)
With pagination

let { data: scanner_test_telemetry, error } = await supabase
  .from('scanner_test_telemetry')
  .select('*')
  .range(0, 9)
Filtering
Documentation
Supabase provides a wide range of filters

With filtering

let { data: scanner_test_telemetry, error } = await supabase
  .from('scanner_test_telemetry')
  .select("*")

  // Filters
  .eq('column', 'Equal to')
  .gt('column', 'Greater than')
  .lt('column', 'Less than')
  .gte('column', 'Greater than or equal to')
  .lte('column', 'Less than or equal to')
  .like('column', '%CaseSensitive%')
  .ilike('column', '%CaseInsensitive%')
  .is('column', null)
  .in('column', ['Array', 'Values'])
  .neq('column', 'Not equal to')

  // Arrays
  .contains('array_column', ['array', 'contains'])
  .containedBy('array_column', ['contained', 'by'])

  // Logical operators
  .not('column', 'like', 'Negate filter')
  .or('some_column.eq.Some value, other_column.eq.Other value')
Insert rows
Documentation
insert lets you insert into your tables. You can also insert in bulk and do UPSERT.

insert will also return the replaced values for UPSERT.

Insert a row

const { data, error } = await supabase
  .from('scanner_test_telemetry')
  .insert([
    { some_column: 'someValue', other_column: 'otherValue' },
  ])
  .select()
Insert many rows

const { data, error } = await supabase
  .from('scanner_test_telemetry')
  .insert([
    { some_column: 'someValue' },
    { some_column: 'otherValue' },
  ])
  .select()
Upsert matching rows

const { data, error } = await supabase
  .from('scanner_test_telemetry')
  .upsert({ some_column: 'someValue' })
  .select()
Update rows
Documentation
update lets you update rows. update will match all rows by default. You can update specific rows using horizontal filters, e.g. eq, lt, and is.

update will also return the replaced values for UPDATE.

Update matching rows

const { data, error } = await supabase
  .from('scanner_test_telemetry')
  .update({ other_column: 'otherValue' })
  .eq('some_column', 'someValue')
  .select()
Delete rows
Documentation
delete lets you delete rows. delete will match all rows by default, so remember to specify your filters!

Delete matching rows

const { error } = await supabase
  .from('scanner_test_telemetry')
  .delete()
  .eq('some_column', 'someValue')
Subscribe to changes
Documentation
Supabase provides realtime functionality and broadcasts database changes to authorized users depending on Row Level Security (RLS) policies.

Subscribe to all events

const channels = supabase.channel('custom-all-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'scanner_test_telemetry' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to inserts

const channels = supabase.channel('custom-insert-channel')
  .on(
    'postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'scanner_test_telemetry' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to updates

const channels = supabase.channel('custom-update-channel')
  .on(
    'postgres_changes',
    { event: 'UPDATE', schema: 'public', table: 'scanner_test_telemetry' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to deletes

const channels = supabase.channel('custom-delete-channel')
  .on(
    'postgres_changes',
    { event: 'DELETE', schema: 'public', table: 'scanner_test_telemetry' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to specific rows

const channels = supabase.channel('custom-filter-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'scanner_test_telemetry', filter: 'some_column=eq.some_value' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()

  user_profiles
No description available


Language: Javascript
Columns

Name	Format	Type	Description
id	
bigint

number	
user_slug	
character varying

string	
full_name	
character varying

string	
whatsapp_phone	
character varying

string	
email	
character varying

string	
password_hash	
character varying

string	
recovery_token_code	
character varying

string	
recovery_token_expires	
character varying

string	
created_at	
timestamp with time zone

string	
Read rows
Documentation
To read rows in this table, use the select method.

Read all rows

let { data: user_profiles, error } = await supabase
  .from('user_profiles')
  .select('*')
Read specific columns

let { data: user_profiles, error } = await supabase
  .from('user_profiles')
  .select('some_column,other_column')
Read referenced tables

let { data: user_profiles, error } = await supabase
  .from('user_profiles')
  .select(`
    some_column,
    other_table (
      foreign_key
    )
  `)
With pagination

let { data: user_profiles, error } = await supabase
  .from('user_profiles')
  .select('*')
  .range(0, 9)
Filtering
Documentation
Supabase provides a wide range of filters

With filtering

let { data: user_profiles, error } = await supabase
  .from('user_profiles')
  .select("*")

  // Filters
  .eq('column', 'Equal to')
  .gt('column', 'Greater than')
  .lt('column', 'Less than')
  .gte('column', 'Greater than or equal to')
  .lte('column', 'Less than or equal to')
  .like('column', '%CaseSensitive%')
  .ilike('column', '%CaseInsensitive%')
  .is('column', null)
  .in('column', ['Array', 'Values'])
  .neq('column', 'Not equal to')

  // Arrays
  .contains('array_column', ['array', 'contains'])
  .containedBy('array_column', ['contained', 'by'])

  // Logical operators
  .not('column', 'like', 'Negate filter')
  .or('some_column.eq.Some value, other_column.eq.Other value')
Insert rows
Documentation
insert lets you insert into your tables. You can also insert in bulk and do UPSERT.

insert will also return the replaced values for UPSERT.

Insert a row

const { data, error } = await supabase
  .from('user_profiles')
  .insert([
    { some_column: 'someValue', other_column: 'otherValue' },
  ])
  .select()
Insert many rows

const { data, error } = await supabase
  .from('user_profiles')
  .insert([
    { some_column: 'someValue' },
    { some_column: 'otherValue' },
  ])
  .select()
Upsert matching rows

const { data, error } = await supabase
  .from('user_profiles')
  .upsert({ some_column: 'someValue' })
  .select()
Update rows
Documentation
update lets you update rows. update will match all rows by default. You can update specific rows using horizontal filters, e.g. eq, lt, and is.

update will also return the replaced values for UPDATE.

Update matching rows

const { data, error } = await supabase
  .from('user_profiles')
  .update({ other_column: 'otherValue' })
  .eq('some_column', 'someValue')
  .select()
Delete rows
Documentation
delete lets you delete rows. delete will match all rows by default, so remember to specify your filters!

Delete matching rows

const { error } = await supabase
  .from('user_profiles')
  .delete()
  .eq('some_column', 'someValue')
Subscribe to changes
Documentation
Supabase provides realtime functionality and broadcasts database changes to authorized users depending on Row Level Security (RLS) policies.

Subscribe to all events

const channels = supabase.channel('custom-all-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'user_profiles' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to inserts

const channels = supabase.channel('custom-insert-channel')
  .on(
    'postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'user_profiles' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to updates

const channels = supabase.channel('custom-update-channel')
  .on(
    'postgres_changes',
    { event: 'UPDATE', schema: 'public', table: 'user_profiles' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to deletes

const channels = supabase.channel('custom-delete-channel')
  .on(
    'postgres_changes',
    { event: 'DELETE', schema: 'public', table: 'user_profiles' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to specific rows

const channels = supabase.channel('custom-filter-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'user_profiles', filter: 'some_column=eq.some_value' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()

  user_subscriptions_v2
No description available


Language: Javascript
Columns

Name	Format	Type	Description
id	
bigint

number	
user_slug	
character varying

string	
campaign_slug	
character varying

string	
status_licenca	
boolean

boolean	
selected_cryptos	
text

string	
start_date	
date

string	
end_date	
date

string	
updated_at	
timestamp with time zone

string	
Read rows
Documentation
To read rows in this table, use the select method.

Read all rows

let { data: user_subscriptions_v2, error } = await supabase
  .from('user_subscriptions_v2')
  .select('*')
Read specific columns

let { data: user_subscriptions_v2, error } = await supabase
  .from('user_subscriptions_v2')
  .select('some_column,other_column')
Read referenced tables

let { data: user_subscriptions_v2, error } = await supabase
  .from('user_subscriptions_v2')
  .select(`
    some_column,
    other_table (
      foreign_key
    )
  `)
With pagination

let { data: user_subscriptions_v2, error } = await supabase
  .from('user_subscriptions_v2')
  .select('*')
  .range(0, 9)
Filtering
Documentation
Supabase provides a wide range of filters

With filtering

let { data: user_subscriptions_v2, error } = await supabase
  .from('user_subscriptions_v2')
  .select("*")

  // Filters
  .eq('column', 'Equal to')
  .gt('column', 'Greater than')
  .lt('column', 'Less than')
  .gte('column', 'Greater than or equal to')
  .lte('column', 'Less than or equal to')
  .like('column', '%CaseSensitive%')
  .ilike('column', '%CaseInsensitive%')
  .is('column', null)
  .in('column', ['Array', 'Values'])
  .neq('column', 'Not equal to')

  // Arrays
  .contains('array_column', ['array', 'contains'])
  .containedBy('array_column', ['contained', 'by'])

  // Logical operators
  .not('column', 'like', 'Negate filter')
  .or('some_column.eq.Some value, other_column.eq.Other value')
Insert rows
Documentation
insert lets you insert into your tables. You can also insert in bulk and do UPSERT.

insert will also return the replaced values for UPSERT.

Insert a row

const { data, error } = await supabase
  .from('user_subscriptions_v2')
  .insert([
    { some_column: 'someValue', other_column: 'otherValue' },
  ])
  .select()
Insert many rows

const { data, error } = await supabase
  .from('user_subscriptions_v2')
  .insert([
    { some_column: 'someValue' },
    { some_column: 'otherValue' },
  ])
  .select()
Upsert matching rows

const { data, error } = await supabase
  .from('user_subscriptions_v2')
  .upsert({ some_column: 'someValue' })
  .select()
Update rows
Documentation
update lets you update rows. update will match all rows by default. You can update specific rows using horizontal filters, e.g. eq, lt, and is.

update will also return the replaced values for UPDATE.

Update matching rows

const { data, error } = await supabase
  .from('user_subscriptions_v2')
  .update({ other_column: 'otherValue' })
  .eq('some_column', 'someValue')
  .select()
Delete rows
Documentation
delete lets you delete rows. delete will match all rows by default, so remember to specify your filters!

Delete matching rows

const { error } = await supabase
  .from('user_subscriptions_v2')
  .delete()
  .eq('some_column', 'someValue')
Subscribe to changes
Documentation
Supabase provides realtime functionality and broadcasts database changes to authorized users depending on Row Level Security (RLS) policies.

Subscribe to all events

const channels = supabase.channel('custom-all-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'user_subscriptions_v2' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to inserts

const channels = supabase.channel('custom-insert-channel')
  .on(
    'postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'user_subscriptions_v2' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to updates

const channels = supabase.channel('custom-update-channel')
  .on(
    'postgres_changes',
    { event: 'UPDATE', schema: 'public', table: 'user_subscriptions_v2' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to deletes

const channels = supabase.channel('custom-delete-channel')
  .on(
    'postgres_changes',
    { event: 'DELETE', schema: 'public', table: 'user_subscriptions_v2' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to specific rows

const channels = supabase.channel('custom-filter-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'user_subscriptions_v2', filter: 'some_column=eq.some_value' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()

  view_active_subscriptions
No description available


Language: Javascript
Columns

Name	Format	Type	Description
id	
bigint

number	
user_slug	
character varying

string	
full_name	
character varying

string	
email	
character varying

string	
whatsapp_phone	
character varying

string	
campaign_slug	
character varying

string	
campaign_name	
character varying

string	
monthly_fee	
numeric

number	
allowed_crypto_count	
integer

number	
selected_cryptos	
text

string	
start_date	
date

string	
end_date	
date

string	
status_licenca	
boolean

boolean	
Read rows
Documentation
To read rows in this table, use the select method.

Read all rows

let { data: view_active_subscriptions, error } = await supabase
  .from('view_active_subscriptions')
  .select('*')
Read specific columns

let { data: view_active_subscriptions, error } = await supabase
  .from('view_active_subscriptions')
  .select('some_column,other_column')
Read referenced tables

let { data: view_active_subscriptions, error } = await supabase
  .from('view_active_subscriptions')
  .select(`
    some_column,
    other_table (
      foreign_key
    )
  `)
With pagination

let { data: view_active_subscriptions, error } = await supabase
  .from('view_active_subscriptions')
  .select('*')
  .range(0, 9)
Filtering
Documentation
Supabase provides a wide range of filters

With filtering

let { data: view_active_subscriptions, error } = await supabase
  .from('view_active_subscriptions')
  .select("*")

  // Filters
  .eq('column', 'Equal to')
  .gt('column', 'Greater than')
  .lt('column', 'Less than')
  .gte('column', 'Greater than or equal to')
  .lte('column', 'Less than or equal to')
  .like('column', '%CaseSensitive%')
  .ilike('column', '%CaseInsensitive%')
  .is('column', null)
  .in('column', ['Array', 'Values'])
  .neq('column', 'Not equal to')

  // Arrays
  .contains('array_column', ['array', 'contains'])
  .containedBy('array_column', ['contained', 'by'])

  // Logical operators
  .not('column', 'like', 'Negate filter')
  .or('some_column.eq.Some value, other_column.eq.Other value')
Insert rows
Documentation
insert lets you insert into your tables. You can also insert in bulk and do UPSERT.

insert will also return the replaced values for UPSERT.

Insert a row

const { data, error } = await supabase
  .from('view_active_subscriptions')
  .insert([
    { some_column: 'someValue', other_column: 'otherValue' },
  ])
  .select()
Insert many rows

const { data, error } = await supabase
  .from('view_active_subscriptions')
  .insert([
    { some_column: 'someValue' },
    { some_column: 'otherValue' },
  ])
  .select()
Upsert matching rows

const { data, error } = await supabase
  .from('view_active_subscriptions')
  .upsert({ some_column: 'someValue' })
  .select()
Update rows
Documentation
update lets you update rows. update will match all rows by default. You can update specific rows using horizontal filters, e.g. eq, lt, and is.

update will also return the replaced values for UPDATE.

Update matching rows

const { data, error } = await supabase
  .from('view_active_subscriptions')
  .update({ other_column: 'otherValue' })
  .eq('some_column', 'someValue')
  .select()
Delete rows
Documentation
delete lets you delete rows. delete will match all rows by default, so remember to specify your filters!

Delete matching rows

const { error } = await supabase
  .from('view_active_subscriptions')
  .delete()
  .eq('some_column', 'someValue')
Subscribe to changes
Documentation
Supabase provides realtime functionality and broadcasts database changes to authorized users depending on Row Level Security (RLS) policies.

Subscribe to all events

const channels = supabase.channel('custom-all-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'view_active_subscriptions' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to inserts

const channels = supabase.channel('custom-insert-channel')
  .on(
    'postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'view_active_subscriptions' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to updates

const channels = supabase.channel('custom-update-channel')
  .on(
    'postgres_changes',
    { event: 'UPDATE', schema: 'public', table: 'view_active_subscriptions' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to deletes

const channels = supabase.channel('custom-delete-channel')
  .on(
    'postgres_changes',
    { event: 'DELETE', schema: 'public', table: 'view_active_subscriptions' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to specific rows

const channels = supabase.channel('custom-filter-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'view_active_subscriptions', filter: 'some_column=eq.some_value' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()

  whalepulse_mempool_signals
No description available


Language: Javascript
Columns

Name	Format	Type	Description
id	
bigint

number	
ticker	
character varying

string	
tx_hash	
character varying

string	
volume_usd	
numeric

number	
direction	
character varying

string	
mempool_latency_ms	
integer

number	
created_at	
timestamp with time zone

string	
Read rows
Documentation
To read rows in this table, use the select method.

Read all rows

let { data: whalepulse_mempool_signals, error } = await supabase
  .from('whalepulse_mempool_signals')
  .select('*')
Read specific columns

let { data: whalepulse_mempool_signals, error } = await supabase
  .from('whalepulse_mempool_signals')
  .select('some_column,other_column')
Read referenced tables

let { data: whalepulse_mempool_signals, error } = await supabase
  .from('whalepulse_mempool_signals')
  .select(`
    some_column,
    other_table (
      foreign_key
    )
  `)
With pagination

let { data: whalepulse_mempool_signals, error } = await supabase
  .from('whalepulse_mempool_signals')
  .select('*')
  .range(0, 9)
Filtering
Documentation
Supabase provides a wide range of filters

With filtering

let { data: whalepulse_mempool_signals, error } = await supabase
  .from('whalepulse_mempool_signals')
  .select("*")

  // Filters
  .eq('column', 'Equal to')
  .gt('column', 'Greater than')
  .lt('column', 'Less than')
  .gte('column', 'Greater than or equal to')
  .lte('column', 'Less than or equal to')
  .like('column', '%CaseSensitive%')
  .ilike('column', '%CaseInsensitive%')
  .is('column', null)
  .in('column', ['Array', 'Values'])
  .neq('column', 'Not equal to')

  // Arrays
  .contains('array_column', ['array', 'contains'])
  .containedBy('array_column', ['contained', 'by'])

  // Logical operators
  .not('column', 'like', 'Negate filter')
  .or('some_column.eq.Some value, other_column.eq.Other value')
Insert rows
Documentation
insert lets you insert into your tables. You can also insert in bulk and do UPSERT.

insert will also return the replaced values for UPSERT.

Insert a row

const { data, error } = await supabase
  .from('whalepulse_mempool_signals')
  .insert([
    { some_column: 'someValue', other_column: 'otherValue' },
  ])
  .select()
Insert many rows

const { data, error } = await supabase
  .from('whalepulse_mempool_signals')
  .insert([
    { some_column: 'someValue' },
    { some_column: 'otherValue' },
  ])
  .select()
Upsert matching rows

const { data, error } = await supabase
  .from('whalepulse_mempool_signals')
  .upsert({ some_column: 'someValue' })
  .select()
Update rows
Documentation
update lets you update rows. update will match all rows by default. You can update specific rows using horizontal filters, e.g. eq, lt, and is.

update will also return the replaced values for UPDATE.

Update matching rows

const { data, error } = await supabase
  .from('whalepulse_mempool_signals')
  .update({ other_column: 'otherValue' })
  .eq('some_column', 'someValue')
  .select()
Delete rows
Documentation
delete lets you delete rows. delete will match all rows by default, so remember to specify your filters!

Delete matching rows

const { error } = await supabase
  .from('whalepulse_mempool_signals')
  .delete()
  .eq('some_column', 'someValue')
Subscribe to changes
Documentation
Supabase provides realtime functionality and broadcasts database changes to authorized users depending on Row Level Security (RLS) policies.

Subscribe to all events

const channels = supabase.channel('custom-all-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'whalepulse_mempool_signals' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to inserts

const channels = supabase.channel('custom-insert-channel')
  .on(
    'postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'whalepulse_mempool_signals' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to updates

const channels = supabase.channel('custom-update-channel')
  .on(
    'postgres_changes',
    { event: 'UPDATE', schema: 'public', table: 'whalepulse_mempool_signals' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to deletes

const channels = supabase.channel('custom-delete-channel')
  .on(
    'postgres_changes',
    { event: 'DELETE', schema: 'public', table: 'whalepulse_mempool_signals' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to specific rows

const channels = supabase.channel('custom-filter-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'whalepulse_mempool_signals', filter: 'some_column=eq.some_value' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()