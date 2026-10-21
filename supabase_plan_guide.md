# Guia operacional do Supabase – fonte de verdade para integração e sincronização

## Atualização técnica coordenada — 20/10/2026 às 21:01 (UTC−03:00)

Esta atualização acompanha a revisão do stream e dos cards de telemetria:

- No modo de teste, o SSE agora envia somente linhas de `scanner_test_telemetry`; se essa tabela estiver ausente ou vazia, não completa dados sintéticos com preços ou indicadores da view real `painel_realtime`.
- Erros HTTP/schema nas leituras de `scanner_telemetry`, `scanner_test_telemetry`, `fbq_hybrid_orders` e `whalepulse_mempool_signals` agora são registrados no log do backend, com no máximo uma mensagem por fonte a cada 30 segundos.
- O stream WhalePulse solicita `ticker`, `tx_hash`, `volume_usd`, `direction`, `mempool_latency_ms` e `created_at`. O listener grava `ticker` como símbolo-base (`BTC`, `ETH` etc.); o navegador o converte para par (`BTCUSDT`, `ETHUSDT`) para localizar o card.
- O campo booleano `whale_pulse_triggered` agora interpreta corretamente respostas textuais como `"false"`.
- O cálculo do termômetro compara o candle atual com os 20 candles anteriores e as confluências não substituem indicadores ausentes por valores artificiais; o motor exige pelo menos 50 candles válidos.
- O listener WhalePulse agora usa uma URL HTTP JSON-RPC para consultar o hash recebido no WebSocket, estima USD com ticker público quando disponível fora do `ram_mock`, aplica o limite configurado e registra falhas em log sem bloquear o loop de análise.
- No modo `ram_mock`, o motor calcula os indicadores dos pares sintéticos sem depender da licença global `ACTIVE_USER_SLUG`; a interface continua aplicando a autorização por usuário e a execução de ordens simuladas permanece limitada a ativos licenciados. O slug padrão da engine usa a primeira conta de teste autorizada quando `ACTIVE_USER_SLUG` não foi definido; se definido, precisa estar em `SIMULATION_TEST_USER_SLUGS` para permitir a persistência sintética.
- O cálculo do regime agora usa a mesma base dos 20 candles anteriores do termômetro de volume.
- O status do WhalePulse agora reflete configuração/estado do listener; eventos JSON-RPC fora do formato esperado não derrubam o processo.
- Em `ram_mock`, o motor analisa todos os pares para telemetria do scanner, sem desbloquear cards nem permitir disparos de ordem para ativos sem entitlement. A UI continua a validar a licença da conta autenticada.
- O endpoint `eth_subscribe newPendingTransactions` observa transações nativas EVM pendentes; não decodifica transferências ERC-20. Para esses tokens será necessário especificar contratos, casas decimais e fonte de preço, em vez de classificar silenciosamente `value=0` como evento.
- A solicitação de SQL permanece pendente: não houve confirmação de execução no Supabase. A alteração de código não cria tabelas remotamente.
- **Ação pendente no Supabase:** a usuária confirmou que ainda não executou nenhuma alteração hoje. Portanto, nada abaixo está marcado como aplicado ou validado.
- **Solicitação clara — 20/10/2026 às 21:01 (UTC−03:00): “cole esse codigo sql no supabase:”** Cole e execute o bloco único da seção 6.5.2 no SQL Editor do projeto Supabase. Ele prepara as tabelas de telemetria, o feed WhalePulse, os índices e as permissões que este código espera.
- Depois de executar, retorne aqui com a confirmação ou com a mensagem de erro do SQL Editor. Só então conferir o stream/runtime e atualizar o status deste guia para aplicado.
- Nunca exponha a chave `service_role` no navegador, em logs ou em mensagens. O bloco SQL não contém nem solicita essa chave.

ATENÇÃO OBRIGATÓRIA: Este arquivo é a referência oficial de configuração do Supabase para o projeto. Sempre que qualquer alteração for feita no código, no fluxo de login, no painel, em campanhas, em licenças, em tokens, em filtros ou em qualquer integração do app, este guia deve ser revisado e atualizado antes de avançar. O objetivo é manter 100% de conformidade entre o banco de dados do Supabase e a lógica do sistema.

## Determinação permanente — backup do código no GitHub

- A cada solicitação que resultar em alteração de código ou documentação do projeto, após validar a mudança, criar um commit e enviá-lo ao repositório GitHub configurado (`origin`), para manter um backup auditável e disponível ao Gemini.
- Incluir somente os arquivos relacionados à solicitação concluída; não incorporar alterações locais preexistentes ou não relacionadas sem autorização.
- Nunca versionar nem enviar `.env`, `.env.*`, chaves privadas, tokens, senhas ou outros segredos. Manter esses arquivos cobertos pelo `.gitignore`; revisar o diff e o status antes de cada envio.
- Se houver credencial no código, dúvida sobre exposição, conflito com o remoto ou falha na validação, não enviar. Informar o bloqueio e pedir orientação antes de publicar.
- Usar push normal para a branch configurada. Nunca sobrescrever o histórico remoto com `--force` como parte do backup automático.
- O repositório atual é público: qualquer conteúdo enviado pode ser visto por qualquer pessoa, não apenas pelo Gemini.

Estado de segurança verificado em 2026-10-21: `.env` existe localmente, é ignorado e não é rastreado pelo Git. `dashboard.py` lê `ADMIN_GATE_PASSWORD` do ambiente e falha fechado se a variável não estiver configurada. O `.env` atual não define essa variável; configure-a localmente antes de usar o desbloqueio administrativo. Nunca publique o valor.

Este documento deve ser tratado como a documentação técnica viva do ambiente. Qualquer mudança em tabela, coluna, nome de campo, tipo, slug de campanha ou regra de negócios exige atualização imediata aqui para evitar inconsistências em produção.

## Checklist de execução imediata do projeto – registro do passo atual

Data e hora do registro da sequência atual: 11/10/2026 (horário local do ambiente do projeto).

Atualização operacional de correção do ambiente Supabase (2026-10-11):

- O host do Supabase configurado no `.env` precisa resolver em DNS; se não resolver, o login e as consultas de sessão falham com `NameResolutionError`.
- O fallback local de autenticação foi removido. Se o Supabase estiver indisponível, o login falha fechado e não cria uma sessão de demonstração.
- A arquitetura correta do projeto exige que o banco remoto reflita os campos e os slugs usados pelo Flask e pelo painel.
- A solução final precisa ser: Supabase real funcionando e validado, sem depender do mock local para produção.

Estado da sequência após a atualização informada:

- O usuário informa que a migração SQL, a reconstrução da view e o login remoto foram validados no Supabase.
- O runtime local permanece em `ram_mock`; essa configuração simula a execução e não habilita ordens financeiras reais.
- O login local de demonstração foi removido; falha de conexão com Supabase agora impede autenticação.
- O deploy/validação do scanner em RAM deve ser confirmado pelo processo `engine.py` e pelo stream `/api/stream`.
- Operação financeira real continua fora do escopo desta ativação.

Nota: a confirmação do schema acima foi fornecida pelo usuário; este ambiente não tem acesso administrativo ao projeto Supabase para auditar o SQL diretamente.

## 1) Escopo de sincronização obrigatória

O código do projeto consulta e persiste dados em tabelas específicas do Supabase. A compatibilidade real do sistema depende do seguinte:

- nomes e tipos de colunas devem coincidir com o que o app espera
- slugs e valores de campanha devem ser exatamente os permitidos pelo código
- campos booleanos e strings devem seguir o formato correto
- registros por usuário não devem duplicar nem conflitar com os filtros de update
- todo payload do app precisa ser alimentado por colunas existentes e legíveis por REST do Supabase

## 2) Tabelas e colunas obrigatórias do projeto

### 2.0) Ajuste de arquitetura atual do Supabase (obrigatório)

A partir da validação do ciclo de login, ficou comprovado que o banco remoto deve ser tratado como a fonte de verdade do sistema e não como um detalhe secundário. O app usa o Supabase para autenticação, assinatura/licença, campanhas, cupons e telemetria. Por isso, a adequação do banco precisa seguir exatamente a arquitetura abaixo:

- `public.user_profiles`: cadastro do usuário, hash de senha, email, `user_slug`, expiração de recuperação.
- `public.user_subscriptions_v2`: vínculo do usuário com campanha, vigência, licenciamento e ativos selecionados.
- `public.marketing_campaigns`: catálogo de planos e ativos autorizados.
- `public.marketing_coupons`: cupons promocionais aplicados.
- `public.fbq_hybrid_orders`: ordens e auditoria do painel de mercado.
- `public.client_exchange_credentials`: credenciais do cliente em sessão, apenas se o ambiente permitir esse fluxo com proteção adequada.

Regra geral:

- os slugs de campanha devem ser idênticos aos aceitos pelo código
- os booleanos devem ser `true/false` reais, não texto
- `selected_cryptos` é armazenado como texto CSV plano; o backend normaliza a string para uso interno
- `password_hash` deve continuar em SHA-256
- `market_updated_at` precisa existir em `fbq_hybrid_orders` para separar o timestamp do preço público do timestamp técnico

### 2.1) user_profiles

Tabela principal de cadastro do cliente.

Colunas esperadas:

- user_slug
- full_name
- email
- whatsapp_phone
- password_hash
- recovery_token_expires

Observações:

- o app usa user_slug como identificador principal do usuário
- o login compara password_hash em digest SHA-256
- o fluxo de recuperação usa email e recovery_token_expires
- o endpoint /api/auth/forgot-password grava a expiração do token no perfil do usuário

Exemplo de estrutura recomendada:

```sql
CREATE TABLE IF NOT EXISTS public.user_profiles (
  user_slug text PRIMARY KEY,
  full_name text,
  email text,
  whatsapp_phone text,
  password_hash text,
  recovery_token_expires text
);
```

### 2.2) user_subscriptions_v2

Ajuste operacional recomendado para o banco real:

```sql
CREATE TABLE IF NOT EXISTS public.user_subscriptions_v2 (
  id bigint GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  user_slug text NOT NULL UNIQUE,
  campaign_slug text,
  status_licenca boolean default false,
  selected_cryptos text DEFAULT '',
  start_date timestamptz,
  end_date timestamptz,
  monthly_fee numeric(12,2) default 0,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  UNIQUE (user_slug)
);
```

Se houver registro antigo em formato textual, use o backend para normalizar; no banco, a estrutura ideal é manter `text[]` para ativos e `timestamptz` para datas.
Tabela de vínculo do cliente com o plano e ativos liberados.

Colunas esperadas:

- user_slug
- campaign_slug
- status_licenca
- selected_cryptos
- start_date
- end_date
- monthly_fee

Observações:

- o app atualiza e consulta esta tabela diretamente em vários endpoints
- `selected_cryptos` é CSV plano (ex.: `BTCUSDT,ETHUSDT,SOLUSDT`); o backend também aceita arrays ao normalizar respostas antigas
- a licença só concede acesso quando `status_licenca` está ativo e a data atual está entre `start_date` e `end_date`
- se `selected_cryptos` estiver vazio, o painel e o motor usam `authorized_cryptocurrencies` da campanha, limitados por `allowed_crypto_count`
- se a campanha não tiver lista explícita, o limite é aplicado à lista fixa de 10 ativos suportados pelo motor
- seleções explícitas são intersectadas com os ativos e o limite da campanha; o cliente não pode ampliar o limite enviando um valor próprio

Slugs de campanha vigentes e obrigatórios:

- 1 Promoção
- 2 Premium
- 3 Premium
- 4 Premium

Exemplo de estrutura correta:

```sql
CREATE TABLE IF NOT EXISTS public.user_subscriptions_v2 (
  user_slug text PRIMARY KEY,
  campaign_slug text,
  status_licenca boolean default false,
  selected_cryptos text DEFAULT '',
  start_date date,
  end_date date,
  monthly_fee numeric(12,2) default 0
);
```

Se a aplicação estiver enviando texto em vez de array, este valor também deve ser aceitável em leitura, por exemplo:

```sql
UPDATE public.user_subscriptions_v2
SET selected_cryptos = 'BTC,ETH,SOL,XRP,BNB,LINK,AVAX,ADA,NEAR,RENDER'
WHERE user_slug = 'usuario_teste';
```

### 2.3) marketing_campaigns

Adotar os slugs exatos abaixo e manter os `authorized_cryptocurrencies` em array de strings em maiúsculas:

```sql
CREATE TABLE IF NOT EXISTS public.marketing_campaigns (
  campaign_slug text PRIMARY KEY,
  campaign_name text,
  allowed_crypto_count integer default 10,
  duration_days integer default 30,
  monthly_fee numeric(12,2) default 0,
  renewal_fee_text text,
  authorized_cryptocurrencies text[] DEFAULT ARRAY[]::text[],
  hidden_plan boolean default false,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
```

Inserir os planos válidos:

```sql
INSERT INTO public.marketing_campaigns (campaign_slug, campaign_name, allowed_crypto_count, duration_days, monthly_fee, renewal_fee_text, authorized_cryptocurrencies, hidden_plan)
VALUES
  ('1 Promoção','1 Promoção',10,30,49.90,'R$ 49,90 mensais',ARRAY['BTC','ETH','SOL','XRP','BNB','LINK','AVAX','ADA','NEAR','RENDER'],false),
  ('2 Premium','2 Premium',10,30,149.00,'R$ 149,00 mensais',ARRAY['BTC','ETH','SOL','XRP','BNB','LINK','AVAX','ADA','NEAR','RENDER'],false),
  ('3 Premium','3 Premium',10,30,249.00,'R$ 249,00 mensais',ARRAY['BTC','ETH','SOL','XRP','BNB','LINK','AVAX','ADA','NEAR','RENDER'],false),
  ('4 Premium','4 Premium',10,30,399.00,'R$ 399,00 mensais',ARRAY['BTC','ETH','SOL','XRP','BNB','LINK','AVAX','ADA','NEAR','RENDER'],false)
ON CONFLICT (campaign_slug) DO UPDATE SET
  campaign_name = EXCLUDED.campaign_name,
  allowed_crypto_count = EXCLUDED.allowed_crypto_count,
  duration_days = EXCLUDED.duration_days,
  monthly_fee = EXCLUDED.monthly_fee,
  renewal_fee_text = EXCLUDED.renewal_fee_text,
  authorized_cryptocurrencies = EXCLUDED.authorized_cryptocurrencies,
  hidden_plan = EXCLUDED.hidden_plan;
```

### 2.4) marketing_coupons

Tabela de catálogo dos planos disponíveis no cadastro e no painel.

Colunas esperadas:

- campaign_slug
- campaign_name
- allowed_crypto_count
- duration_days
- monthly_fee
- renewal_fee_text
- authorized_cryptocurrencies
- hidden_plan

Observações:

- os slugs válidos para o app são fixos e devem se manter exatamente como o código exige
- o app valida o valor de campaign_slug antes de inserir ou atualizar registros
- o cadastro e o override de licença exigem que o valor exista nesta tabela

Exemplo de estrutura recomendada:

```sql
CREATE TABLE IF NOT EXISTS public.marketing_campaigns (
  campaign_slug text PRIMARY KEY,
  campaign_name text,
  allowed_crypto_count integer,
  duration_days integer,
  monthly_fee numeric(12,2),
  renewal_fee_text text,
  authorized_cryptocurrencies text[] DEFAULT ARRAY[]::text[],
  hidden_plan boolean default false
);
```

Exemplo de insert conforme o código:

```sql
INSERT INTO public.marketing_campaigns (
  campaign_slug,
  campaign_name,
  allowed_crypto_count,
  duration_days,
  monthly_fee,
  renewal_fee_text,
  authorized_cryptocurrencies,
  hidden_plan
)
VALUES
  (
    '1 Promoção',
    '1 Promoção',
    10,
    30,
    49.90,
    'R$ 49,90 mensais',
    ARRAY['BTC','ETH','SOL','XRP','BNB','LINK','AVAX','ADA','NEAR','RENDER'],
    false
  ),
  (
    '2 Premium',
    '2 Premium',
    10,
    30,
    149.00,
    'R$ 149,00 mensais',
    ARRAY['BTC','ETH','SOL','XRP','BNB','LINK','AVAX','ADA','NEAR','RENDER'],
    false
  ),
  (
    '3 Premium',
    '3 Premium',
    10,
    30,
    249.00,
    'R$ 249,00 mensais',
    ARRAY['BTC','ETH','SOL','XRP','BNB','LINK','AVAX','ADA','NEAR','RENDER'],
    false
  ),
  (
    '4 Premium',
    '4 Premium',
    10,
    30,
    399.00,
    'R$ 399,00 mensais',
    ARRAY['BTC','ETH','SOL','XRP','BNB','LINK','AVAX','ADA','NEAR','RENDER'],
    false
  )
ON CONFLICT (campaign_slug) DO UPDATE SET
  campaign_name = EXCLUDED.campaign_name,
  allowed_crypto_count = EXCLUDED.allowed_crypto_count,
  duration_days = EXCLUDED.duration_days,
  monthly_fee = EXCLUDED.monthly_fee,
  renewal_fee_text = EXCLUDED.renewal_fee_text,
  authorized_cryptocurrencies = EXCLUDED.authorized_cryptocurrencies,
  hidden_plan = EXCLUDED.hidden_plan;
```

### 2.4) marketing_coupons

Tabela de cupons promocionais aplicados na assinatura e no cálculo de desconto.

Colunas esperadas:

- coupon_code
- discount_percent
- discount_fixed
- is_active

Exemplo:

```sql
CREATE TABLE IF NOT EXISTS public.marketing_coupons (
  coupon_code text PRIMARY KEY,
  discount_percent numeric(5,2) default 0,
  discount_fixed numeric(12,2) default 0,
  is_active boolean default true
);
```

### 2.5) client_exchange_credentials

Tabela usada pela API para armazenar chaves da exchange do cliente.

Colunas esperadas:

- user_slug
- binance_client_api_key
- binance_client_api_secret

Exemplo:

```sql
CREATE TABLE IF NOT EXISTS public.client_exchange_credentials (
  user_slug text PRIMARY KEY,
  binance_client_api_key text,
  binance_client_api_secret text
);
```

### 2.6) fbq_hybrid_orders

Tabela para ordens híbridas e auditoria.

Campos esperados no uso do app:

- created_at
- ticker / ativo / symbol / asset
- current_price / preco_atual / price
- price_change_percent / percentual
- regime_detectado / regime_mercado
- volume_mempool / mempool_transactions / mempool
- kelly_leverage / leverage_dinamico
- target_price_34 / tp / alvo_turbo
- break_even_price / break_even
- risk_slider_pos
- market_updated_at (timestamp da última cotação pública; distinto do updated_at do sinal técnico)

`ticker`, `current_price`, `price_change_percent` e `market_updated_at` são atualizados pelo feed público. `updated_at` continua reservado ao snapshot técnico autorizado. Em `ram_mock`, o app só pode atualizar esses quatro campos de mercado; ROI simulado, alvos, posição, histórico financeiro e ledger não são persistidos.

### 2.7) historico_trades

Tabela antiga de histórico de trades usada como fallback.

Campos esperados no uso do app:

- assinante_id
- id
- created_at
- ativo / ticker
- operação / side
- percentual
- resultado / profit_loss

### 2.8) investor_performance_ledgers

Tabela de auditoria financeira por usuário.

Campos esperados no uso do app:

- assinante_id
- created_at
- lucro_real
- garantia_alocada
- taxa_assertividade
- percentual_lucro

### 2.9) whalepulse_mempool_signals

Tabela de sinais de mempool para feed em tempo real.

Colunas efetivamente gravadas pelo listener e usadas pelo stream:

- `id`: chave gerada pelo banco, se a tabela usar esta coluna.
- `ticker`: símbolo-base sem `USDT` (por exemplo, `ETH`).
- `tx_hash`: hash da transação pendente.
- `volume_usd`: valor estimado em USD; o listener persiste apenas sinais acima de USD 100.000.
- `direction`: direção reportada pelo provider, ou `UNKNOWN`.
- `mempool_latency_ms`: latência medida pelo listener.
- `created_at`: timestamp com `DEFAULT now()`, usado para ordenar e expirar eventos na interface.

`ativo`, `symbol`, `valor`, `amount` e `signal_type` não são campos lidos pelo fluxo atual. Não use nomes alternativos sem mapeá-los explicitamente no backend.

### 2.10) view_active_subscriptions

View de leitura consolidada usada para obter vínculo ativo em tempo real.

Colunas esperadas no app:

- user_slug
- campaign_slug
- start_date
- end_date
- status_licenca
- selected_cryptos
- monthly_fee

### 2.11) painel_realtime e assinantes

Tabelas e views referenciadas em helpers de compatibilidade do código. A aplicação espera que existam campos compatíveis com esse ambiente real-time e com consultas de assinatura, mas as críticas de funcionamento do app estão concentradas em user_profiles, user_subscriptions_v2, marketing_campaigns e marketing_coupons.

`painel_realtime` é a view de leitura de mercado/ordens e deve manter `ticker`, preços e `market_updated_at`. Não enviar o payload técnico da engine para essa view: ela não expõe `ativo`/`adx_val` e não é o destino gravável dos indicadores. A engine grava checkpoints e métricas técnicas em `scanner_telemetry`; o SSE mescla as duas fontes por `ticker`, mantendo separados `updated_at` técnico e `market_updated_at` de mercado.

## 3) Regras operacionais obrigatórias para produção

### 3.1) Slugs válidos de campanha

O código não aceita qualquer valor arbitrário para campaign_slug. Os valores válidos são apenas estes:

- 1 Promoção
- 2 Premium
- 3 Premium
- 4 Premium

Qualquer outra string deve ser rejeitada pelo backend e pode quebrar o fluxo de criação, atualização e acesso ao painel.

### 3.2) Booleans

Campos do tipo boolean devem ser gravados como true/false reais e não como texto.

Exemplo correto:

```sql
UPDATE public.user_subscriptions_v2
SET status_licenca = true
WHERE user_slug = 'usuario_teste';
```

### 3.3) Ativos autorizados

A app normaliza os ativos e exige que sejam strings curtas em maiúsculas, sem USDT.

Valores aceitos:

- BTC
- XRP
- ETH
- SOL
- BNB
- LINK
- AVAX
- ADA
- NEAR
- RENDER

### 3.4) Ninguém deve ter mais de um vínculo ativo por usuário

O app usa filtros por user_slug e pode quebrar se houver duplicidade. A regra correta é manter somente um vínculo ativo por usuário em user_subscriptions_v2.

```sql
DELETE FROM public.user_subscriptions_v2
WHERE id NOT IN (
  SELECT MAX(id)
  FROM public.user_subscriptions_v2
  GROUP BY user_slug
);
```

## 4) SQL de verificação rápida

Use estas consultas para validar o ambiente antes de embarque ou de qualquer alteração de código:

### 4.1) Validar usuários e assinatura

```sql
SELECT
  u.user_slug,
  u.email,
  s.campaign_slug,
  s.status_licenca,
  s.selected_cryptos,
  s.start_date,
  s.end_date,
  s.monthly_fee
FROM public.user_profiles u
LEFT JOIN public.user_subscriptions_v2 s ON s.user_slug = u.user_slug
ORDER BY u.user_slug;
```

### 4.2) Validar campanhas

```sql
SELECT *
FROM public.marketing_campaigns
ORDER BY campaign_slug;
```

### 4.3) Validar cupons

```sql
SELECT *
FROM public.marketing_coupons
ORDER BY coupon_code;
```

### 4.4) Validar investimento e ordens

```sql
SELECT *
FROM public.fbq_hybrid_orders
ORDER BY created_at DESC
LIMIT 20;
```

## 5) Checklist de conformidade para auditoria do código

Antes de prosseguir com qualquer funcionalidade nova, todas as condições abaixo devem ser confirmadas:

- [ ] Slugs de campanha estão exatamente iguais aos permitidos pelo código
- [ ] Tabelas e colunas referenciadas pelo app existem no Supabase
- [ ] status_licenca é booleano
- [ ] selected_cryptos está em formato legível para o app
- [ ] user_slug é único e consistente em user_profiles e user_subscriptions_v2
- [ ] email e password_hash estão sendo persistidos corretamente
- [ ] recovery_token_expires existe quando necessário
- [ ] marketing_campaigns e marketing_coupons contêm os registros esperados
- [ ] nenhum update usa filtro incompatível com a PK real da tabela
- [ ] todos os registros relevantes foram auditados após qualquer mudança na lógica do sistema

## 6) Registro de implantação e verificações do Supabase

### 6.0) Atualização de correção do ambiente (2026-10-11)

A aplicação deve seguir esta sequência real de adequação ao banco:

1. A migração e a view foram reportadas como aplicadas e o login remoto como validado.
2. O app não possui mais autenticação local de demonstração.
3. O backend grava `selected_cryptos` como CSV plano, conforme o tipo `text` confirmado.
4. O parser do stream recalcula a autorização por ativo em cada evento SSE.
5. Manter `.runtime_mode` em `ram_mock` para scanner e telemetria sem ordens reais.
6. Confirmar a disponibilidade do stream e dos dados de mercado antes de considerar a ativação RAM concluída.

Se DNS ou REST do Supabase falhar neste ambiente, o login permanece bloqueado. O painel não deve tratar dados demonstrativos como sessão autenticada.

### 6.1) SQL recomendado para validação de DNS e schema

```sql
SELECT current_setting('server_version');

SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name IN ('user_profiles','user_subscriptions_v2','marketing_campaigns','marketing_coupons','fbq_hybrid_orders')
ORDER BY table_name, ordinal_position;
```

Verifique no editor também que o host público do Supabase esteja resolvendo corretamente no ambiente em que o app roda.

### 6.2) Migração aplicada no Supabase

O usuário confirmou a aplicação manual da alteração abaixo. O SQL fica aqui como histórico/referência; não precisa ser reaplicado se a coluna já existe.

### MIGRAÇÃO SUPABASE - `market_updated_at` (referência histórica)

Esta coluna separa a idade do preço público da idade do sinal técnico. A coluna foi reportada como aplicada e validada pelo usuário:

```sql
ALTER TABLE public.fbq_hybrid_orders
ADD COLUMN IF NOT EXISTS market_updated_at timestamptz;
```

Depois de aplicar, confirme no editor SQL:

```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'fbq_hybrid_orders'
  AND column_name IN ('ticker', 'current_price', 'price_change_percent', 'updated_at', 'market_updated_at')
ORDER BY column_name;
```

Confirme também que `ticker` tem unicidade, pois os upserts do app usam `on_conflict=ticker`; não crie uma constraint duplicada se já houver índice/constraint equivalente. Após você confirmar a coluna, reinicie a engine e confira se `market_updated_at` avança para os 10 tickers. Se a API responder erro de coluna ou permissão, envie o status/erro sem compartilhar chaves.

### 6.1) Estrutura mínima recomendada para user_profiles

```sql
CREATE TABLE IF NOT EXISTS public.user_profiles (
  user_slug text PRIMARY KEY,
  full_name text,
  email text,
  whatsapp_phone text,
  password_hash text,
  recovery_token_expires text
);
```

### 6.2) Estrutura mínima recomendada para user_subscriptions_v2

```sql
CREATE TABLE IF NOT EXISTS public.user_subscriptions_v2 (
  user_slug text PRIMARY KEY,
  campaign_slug text,
  status_licenca boolean default false,
  selected_cryptos text default '',
  start_date date,
  end_date date,
  monthly_fee numeric(12,2) default 0
);
```

Se houver dados antigos ou duplicados, manter apenas um vínculo por usuário:

```sql
DELETE FROM public.user_subscriptions_v2
WHERE id NOT IN (
  SELECT MAX(id)
  FROM public.user_subscriptions_v2
  GROUP BY user_slug
);
```

### 6.3) Estrutura mínima recomendada para marketing_campaigns

```sql
CREATE TABLE IF NOT EXISTS public.marketing_campaigns (
  campaign_slug text PRIMARY KEY,
  campaign_name text,
  allowed_crypto_count integer,
  duration_days integer,
  monthly_fee numeric(12,2),
  renewal_fee_text text,
  authorized_cryptocurrencies text[] DEFAULT ARRAY[]::text[],
  hidden_plan boolean default false
);
```

Inserir/atualizar os slugs válidos exigidos pelo código:

```sql
INSERT INTO public.marketing_campaigns (
  campaign_slug,
  campaign_name,
  allowed_crypto_count,
  duration_days,
  monthly_fee,
  renewal_fee_text,
  authorized_cryptocurrencies,
  hidden_plan
)
VALUES
  ('1 Promoção', '1 Promoção', 10, 30, 49.90, 'R$ 49,90 mensais', ARRAY['BTC','ETH','SOL','XRP','BNB','LINK','AVAX','ADA','NEAR','RENDER'], false),
  ('2 Premium', '2 Premium', 10, 30, 149.00, 'R$ 149,00 mensais', ARRAY['BTC','ETH','SOL','XRP','BNB','LINK','AVAX','ADA','NEAR','RENDER'], false),
  ('3 Premium', '3 Premium', 10, 30, 249.00, 'R$ 249,00 mensais', ARRAY['BTC','ETH','SOL','XRP','BNB','LINK','AVAX','ADA','NEAR','RENDER'], false),
  ('4 Premium', '4 Premium', 10, 30, 399.00, 'R$ 399,00 mensais', ARRAY['BTC','ETH','SOL','XRP','BNB','LINK','AVAX','ADA','NEAR','RENDER'], false)
ON CONFLICT (campaign_slug) DO UPDATE SET
  campaign_name = EXCLUDED.campaign_name,
  allowed_crypto_count = EXCLUDED.allowed_crypto_count,
  duration_days = EXCLUDED.duration_days,
  monthly_fee = EXCLUDED.monthly_fee,
  renewal_fee_text = EXCLUDED.renewal_fee_text,
  authorized_cryptocurrencies = EXCLUDED.authorized_cryptocurrencies,
  hidden_plan = EXCLUDED.hidden_plan;
```

### 6.4) Estrutura mínima recomendada para marketing_coupons

```sql
CREATE TABLE IF NOT EXISTS public.marketing_coupons (
  coupon_code text PRIMARY KEY,
  discount_percent numeric(5,2) default 0,
  discount_fixed numeric(12,2) default 0,
  is_active boolean default true
);
```

### 6.5) Contrato da telemetria técnica do scanner

O usuário informa que as condições de schema abaixo foram aplicadas/validadas no Supabase. A confirmação local da conectividade e do stream ainda deve ser feita no runtime:

- [x] `status_licenca` é booleano real
- [x] `selected_cryptos` é CSV plano em coluna `text`
- [x] `market_updated_at` existe em `fbq_hybrid_orders`
- [x] view de assinaturas foi reconstruída após a alteração de tipos
- [x] login remoto foi validado pelo usuário
- [x] `painel_realtime` responde 200 como view de mercado/ordens; `market_updated_at` avança
- [ ] tabela `scanner_telemetry` existe com chave única `ticker`, payload `jsonb` e `updated_at` recente
- [ ] tabela isolada `scanner_test_telemetry` existe com chave única `ticker`, payload `jsonb` e `updated_at` recente
- [x] processo `engine.py` ativo em `ram_mock`; scanner reportou 10 pares atualizados em RAM
- [x] `/api/stream` respondeu `200 text/event-stream` com 10 linhas de mercado, flag booleana e tokens CSV

Os itens marcados como concluídos refletem a confirmação do usuário e não uma consulta administrativa executada pelo agente.

O endpoint `GET /rest/v1/painel_realtime` respondeu 200, mas essa view não contém o payload técnico gravado pela engine e seu `updated_at` histórico não é o timestamp do mercado. Crie a tabela independente abaixo; não altere nem tente gravar na view `painel_realtime`.

```sql
CREATE TABLE IF NOT EXISTS public.scanner_telemetry (
  ticker text PRIMARY KEY,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.scanner_test_telemetry (
  ticker text PRIMARY KEY,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  updated_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE public.scanner_telemetry ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scanner_test_telemetry ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE public.scanner_telemetry FROM anon, authenticated;
REVOKE ALL ON TABLE public.scanner_test_telemetry FROM anon, authenticated;
GRANT SELECT, INSERT, UPDATE ON TABLE public.scanner_telemetry TO service_role;
GRANT SELECT, INSERT, UPDATE ON TABLE public.scanner_test_telemetry TO service_role;
NOTIFY pgrst, 'reload schema';
```

Se uma tabela já existir, confirme que `ticker` tem chave primária ou constraint/índice `UNIQUE`, pois a engine faz upsert com `on_conflict=ticker`; não crie uma segunda constraint equivalente. O backend precisa usar credencial Supabase `service_role` exclusivamente no servidor; nunca exponha essa chave no HTML ou JavaScript. Após executar o SQL, valide pelo SQL Editor:

```sql
SELECT ticker, updated_at, payload
FROM public.scanner_telemetry
ORDER BY updated_at DESC
LIMIT 10;

SELECT ticker, updated_at, payload
FROM public.scanner_test_telemetry
ORDER BY updated_at DESC
LIMIT 10;
```

E valide a view de mercado sem pedir colunas técnicas que ela não fornece:

```sql
SELECT ticker, current_price, market_updated_at, updated_at
FROM public.painel_realtime
ORDER BY market_updated_at DESC
LIMIT 10;
```

O engine e o SSE mesclam os resultados por ticker; a interface só aceita indicadores quando `scanner_telemetry.updated_at` estiver recente.

### 6.5.1) Contrato e migração de whalepulse_mempool_signals

O listener insere registros em `public.whalepulse_mempool_signals`; o SSE lê as colunas indicadas explicitamente. Execute no SQL Editor. As instruções `ADD COLUMN IF NOT EXISTS` alinham tabelas antigas sem apagar colunas ou registros:

```sql
CREATE TABLE IF NOT EXISTS public.whalepulse_mempool_signals (
  id bigint GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  ticker text NOT NULL,
  tx_hash text NOT NULL,
  volume_usd numeric(20,2) NOT NULL,
  direction text NOT NULL DEFAULT 'UNKNOWN',
  mempool_latency_ms numeric(12,2) NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE public.whalepulse_mempool_signals
  ADD COLUMN IF NOT EXISTS ticker text,
  ADD COLUMN IF NOT EXISTS tx_hash text,
  ADD COLUMN IF NOT EXISTS volume_usd numeric(20,2),
  ADD COLUMN IF NOT EXISTS direction text DEFAULT 'UNKNOWN',
  ADD COLUMN IF NOT EXISTS mempool_latency_ms numeric(12,2) DEFAULT 0,
  ADD COLUMN IF NOT EXISTS created_at timestamptz DEFAULT now();

CREATE INDEX IF NOT EXISTS whalepulse_mempool_signals_created_at_idx
  ON public.whalepulse_mempool_signals (created_at DESC);

ALTER TABLE public.whalepulse_mempool_signals ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE public.whalepulse_mempool_signals FROM anon, authenticated;
GRANT SELECT, INSERT ON TABLE public.whalepulse_mempool_signals TO service_role;
NOTIFY pgrst, 'reload schema';
```

O listener não envia `id` nem `created_at`: confirme que `id` é gerado pelo banco (quando presente) e que `created_at` tem `DEFAULT now()`. Valide estrutura e registros:

```sql
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'whalepulse_mempool_signals'
ORDER BY ordinal_position;

SELECT ticker, tx_hash, volume_usd, direction, mempool_latency_ms, created_at
FROM public.whalepulse_mempool_signals
ORDER BY created_at DESC
LIMIT 20;
```

O RPC de mempool é independente do scanner de candles. Configure no `.env` do processo da engine:

```dotenv
WHALE_PULSE_RPC_URL=wss://SEU-PROVEDOR/SEU-ENDPOINT
WHALE_PULSE_RPC_HTTP_URL=https://SEU-PROVEDOR/SEU-ENDPOINT
WHALE_PULSE_TICKER=ETH
WHALE_PULSE_NATIVE_USD_PRICE=0
WHALE_PULSE_MEMPOOL_THRESHOLD=100000
```

`WHALE_PULSE_RPC_URL` precisa ser um endpoint WebSocket JSON-RPC (`ws://` ou `wss://`). `WHALE_PULSE_RPC_HTTP_URL` é opcional se o mesmo endpoint aceitar a conversão de esquema para HTTP/HTTPS; configure-o explicitamente quando o provedor fornecer URLs distintas. Sem preço USD configurado, o motor usa o ticker público do ativo nativo somente fora de `ram_mock`; no modo simulado não usa preço sintético para classificar transações on-chain. `WHALE_PULSE_MEMPOOL_THRESHOLD` tem padrão de USD 100.000 e pode ser ajustado para teste controlado; isso não fabrica eventos. Sem endpoint acessível ou transações compatíveis acima do limite, o estado correto é “aguardando”, sem evento falso.

### 6.5.2) Ação solicitada: preparar as tabelas no Supabase

**Data e hora da solicitação: 20/10/2026 às 21:01 (UTC−03:00).**

> **Cole esse codigo sql no supabase:** abra o SQL Editor do projeto Supabase, cole o bloco completo abaixo e execute-o. Você informou que ainda não fez as alterações no Supabase; portanto, a execução continua pendente.

Este SQL é repetível, não apaga registros e prepara as três tabelas consumidas pelos fluxos de telemetria. Em tabelas de scanner preexistentes, `ticker` deve estar sem duplicatas para a criação do índice único; se a execução parar no índice, envie o erro antes de remover qualquer dado.

```sql
CREATE TABLE IF NOT EXISTS public.scanner_telemetry (
  ticker text PRIMARY KEY,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.scanner_test_telemetry (
  ticker text PRIMARY KEY,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.whalepulse_mempool_signals (
  id bigint GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  ticker text NOT NULL,
  tx_hash text NOT NULL,
  volume_usd numeric(20,2) NOT NULL,
  direction text NOT NULL DEFAULT 'UNKNOWN',
  mempool_latency_ms numeric(12,2) NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE public.scanner_telemetry
  ADD COLUMN IF NOT EXISTS ticker text,
  ADD COLUMN IF NOT EXISTS payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  ADD COLUMN IF NOT EXISTS updated_at timestamptz NOT NULL DEFAULT now();

ALTER TABLE public.scanner_test_telemetry
  ADD COLUMN IF NOT EXISTS ticker text,
  ADD COLUMN IF NOT EXISTS payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  ADD COLUMN IF NOT EXISTS updated_at timestamptz NOT NULL DEFAULT now();

ALTER TABLE public.whalepulse_mempool_signals
  ADD COLUMN IF NOT EXISTS ticker text,
  ADD COLUMN IF NOT EXISTS tx_hash text,
  ADD COLUMN IF NOT EXISTS volume_usd numeric(20,2),
  ADD COLUMN IF NOT EXISTS direction text DEFAULT 'UNKNOWN',
  ADD COLUMN IF NOT EXISTS mempool_latency_ms numeric(12,2) DEFAULT 0,
  ADD COLUMN IF NOT EXISTS created_at timestamptz DEFAULT now();

ALTER TABLE public.whalepulse_mempool_signals
  ALTER COLUMN created_at SET DEFAULT now();

UPDATE public.whalepulse_mempool_signals
SET created_at = now()
WHERE created_at IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS scanner_telemetry_ticker_uidx
  ON public.scanner_telemetry (ticker);
CREATE UNIQUE INDEX IF NOT EXISTS scanner_test_telemetry_ticker_uidx
  ON public.scanner_test_telemetry (ticker);
CREATE INDEX IF NOT EXISTS whalepulse_mempool_signals_created_at_idx
  ON public.whalepulse_mempool_signals (created_at DESC);

ALTER TABLE public.scanner_telemetry ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scanner_test_telemetry ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.whalepulse_mempool_signals ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.scanner_telemetry FROM PUBLIC, anon, authenticated;
REVOKE ALL ON TABLE public.scanner_test_telemetry FROM PUBLIC, anon, authenticated;
REVOKE ALL ON TABLE public.whalepulse_mempool_signals FROM PUBLIC, anon, authenticated;

GRANT SELECT, INSERT, UPDATE ON TABLE public.scanner_telemetry TO service_role;
GRANT SELECT, INSERT, UPDATE ON TABLE public.scanner_test_telemetry TO service_role;
GRANT SELECT, INSERT ON TABLE public.whalepulse_mempool_signals TO service_role;

DO $$
DECLARE
  id_sequence text;
BEGIN
  id_sequence := pg_get_serial_sequence('public.whalepulse_mempool_signals', 'id');
  IF id_sequence IS NOT NULL THEN
    EXECUTE format('GRANT USAGE, SELECT ON SEQUENCE %s TO service_role', id_sequence);
  END IF;
END
$$;

NOTIFY pgrst, 'reload schema';q   q
```

Se o SQL Editor indicar erro em alguma linha, não apague tabelas ou registros: copie a mensagem exata e envie para correção orientada. Após execução bem-sucedida, informe “SQL executado” para eu conferir o stream e registrar a confirmação; ainda será necessário verificar que o listener WhalePulse tem `WHALE_PULSE_RPC_URL` válido para que apareçam eventos reais.

### 6.6) Varredura sintética isolada para testes

O modo `ram_mock` gera candles e preços sintéticos em memória quando o feed público da Binance não está disponível. Esses dados são apenas para validação funcional; não representam o mercado, não criam ordens em corretoras e não devem ser apresentados como dados reais a investidores.

Para testar o painel, configure no `.env`:

```dotenv
RUNTIME_MODE=ram_mock
SIMULATION_TEST_USER_SLUGS=investidor-teste-1,investidor-teste-2
SIMULATION_TEST_EMAIL=caixa-de-teste@example.com
ACTIVE_USER_SLUG=investidor-teste-1
```

- Ative `RAM MOCK` no console de manutenção (ou defina `.runtime_mode` como `ram_mock`). Esse arquivo tem prioridade sobre `RUNTIME_MODE` do `.env`.
- Use somente slugs de contas de teste dedicadas em `SIMULATION_TEST_USER_SLUGS`; não inclua contas de investidores reais.
- No modo `ram_mock`, o motor calcula as confluências para todos os pares sintéticos para que o ambiente de teste alimente os cards; a UI continua bloqueando ativos não autorizados. Alertas/ordens simuladas só podem ser gerados para ativos com assinatura vigente e autorização.
- Em `ram_mock`, somente as contas nessa lista recebem a telemetria sintética pelo SSE. O painel dessas contas exibe um aviso persistente de simulação.
- A engine grava os indicadores e preços sintéticos apenas em `public.scanner_test_telemetry`, sem substituir `scanner_telemetry`, `fbq_hybrid_orders` ou os preços públicos.
- E-mails enviados em `ram_mock` são redirecionados para `SIMULATION_TEST_EMAIL`, marcados como simulação e bloqueados se esse destino não estiver configurado. A recuperação/reemissão de código também é limitada aos slugs de teste.
- Faça estes testes em um projeto Supabase de staging sempre que possível. A tabela de teste precisa de uma chave única por `ticker`, acesso de leitura/escrita somente pelo `service_role` e RLS habilitado:

```sql
CREATE TABLE IF NOT EXISTS public.scanner_test_telemetry (
  ticker text PRIMARY KEY,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  updated_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE public.scanner_test_telemetry ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE public.scanner_test_telemetry FROM anon, authenticated;
GRANT SELECT, INSERT, UPDATE ON TABLE public.scanner_test_telemetry TO service_role;
NOTIFY pgrst, 'reload schema';
```

Com essas proteções, o modo de teste não depende de DNS/Binance para continuar a varredura e não mistura sua telemetria nem seus e-mails com os fluxos reais.

## 7) Resumo final

Este guide deve ser usado como a referência de sincronização do banco com o sistema. Se o app funciona de forma estável, o Supabase está alinhado; se o app falha, a primeira auditoria deve ser feita aqui, confirmando tabelas, nomes de colunas, tipos, slugs e regras de integridade.

Tudo que impacta a sessão, licenças, campanhas, autenticação, filtros de ativos e rescisão do stream precisa estar refletido no banco e neste guia. Sem essa sincronização, o funcionamento real do código fica inconsistente e suscetível a falhas em produção.

## 8) Auditoria de compatibilidade histórica e impacto real no fluxograma de métricas

Durante a auditoria do código atual, ficou confirmado que existem referências legadas e compatibilidade antiga para históricos de ordem, mas a trajetória principal do sistema não depende de uma tabela material separada chamada `public.historico_trades` como fonte principal de truth para o painel.

### 7.1) Diagnóstico do caminho atual

No arquivo [engine.py](engine.py), a função `buscar_assinantes_ativos()` ainda tenta consultar `SUPABASE_URL_CLEAN/rest/v1/assinantes?status=eq.ativo`. Esse endpoint é uma rota legada/compatibilidade e não é o caminho primário de licenciamento do app atual.

A leitura ativa mais relevante do backend usa diretamente:

- `public.fbq_hybrid_orders` para ordens e telemetria híbrida
- `public.investor_performance_ledgers` para ledger financeiro e ganhos reais
- `public.user_subscriptions_v2` para licença, ativos liberados e status de uso

A função `contar_posicoes_abertas_supabase()` em [engine.py](engine.py) ainda consulta `rest/v1/historico_trades`, mas isso é um fallback de compatibilidade, não o eixo principal de execução atual do fluxo de monitoramento e resultado.

O mesmo vale para o bloco de leitura em [dashboard.py](dashboard.py), que tenta `fbq_hybrid_orders` primeiro e só depois recorre a `historico_trades` se o feed híbrido estiver vazio. Esse comportamento foi implementado para evitar quebra total, mas também transforma a ausência de tabela em um estado silencioso: a resposta cai para lista vazia, os dados não são exibidos e o painel pode parecer funcional sem preencher corretamente os indicadores financeiros.

### 7.2) Impacto real no “Controle de Resultado”

O bloco visual do “Controle de Resultado” em [templates/monitoramento.html](templates/monitoramento.html) é alimentado principalmente por renderização estática do HTML e por um recalculo local do navegador via `recalcularAuditoriaFinanceira()`. Ou seja:

- o painel não depende exclusivamente de uma API de histórico do Supabase para mostrar os cards base
- o conteúdo dos cards pode aparecer com valores zerados ou sem dados reais quando não há feed híbrido ou ledger disponível
- a ausência de uma tabela histórica robusta pode impedir a população plena dos valores de relatório, embora não necessariamente provoque crash visível da página

Em termos práticos: a ausência de `public.historico_trades` ou de `public.assinantes` não bloqueia imediatamente o app em toda a estrutura, mas pode causar `404`, lista vazia e dados sem preenchimento para o extrato e para as métricas de resultado, especialmente em cenários legados ou sem feed híbrido ativo.

### 7.3) Conclusão de compatibilidade

A arquitetura atual está sincronizada com a seguinte realidade:

- `public.fbq_hybrid_orders` = eixo principal do feed híbrido e telemetria
- `public.investor_performance_ledgers` = eixo principal do resultado financeiro real
- `public.user_subscriptions_v2` = eixo principal da licença e desbloqueio de ativos
- `historico_trades` e `assinantes` = compatibilidade legacy/fallback, não a linha de produção principal

Portanto, a documentação precisa refletir que a fiação atual do sistema é híbrida: produção em `fbq_hybrid_orders` + `investor_performance_ledgers`, com queda para históricos legados apenas como contingência.

## Observações e solicitações concluídas

- Validação do ciclo de conformidade da tabela `public.marketing_campaigns` concluída com status 100% compatível ao backend em produção.
- Slugs numéricos validados e integrados ao fluxo do código: `1 Promoção`, `2 Premium`, `3 Premium`, `4 Premium`.
- A camada de licenciamento e desbloqueio de ativos permanece consistente com a fiação atual do painel e da telemetria.
- A recuperação de senha com fallback SMTP dual port foi mantida conforme o fluxo já validado, sem alteração nas rotas ativas.
- O microcard de `Controle de Resultado` e os filtros de dados permanecem intactos, preservando a experiência de produção.

## Instruções complementares de código e Supabase

- Sempre que qualquer mudança for feita em slugs, campanhas, licenças, filtros, autenticação ou stream, revisar este guia antes de publicar.
- Manter `user_subscriptions_v2` com um único vínculo ativo por usuário para evitar conflitos de autorização.
- Armazenar `selected_cryptos` como CSV plano `text`; normalizar os tokens para pares canônicos apenas em memória.
- Manter `marketing_campaigns` como fonte de verdade para o catálogo de planos e campanhas publicadas no cadastro.
- Monitorar o fluxo de `fbq_hybrid_orders` e `investor_performance_ledgers` para garantir que os indicadores financeiros do painel não fiquem vazios ou sem sincronização.

## Sugestões de melhoria para o negócio

- Criar rotina mensal de auditoria automatizada de slugs e campanhas para prevenir drift de dados no banco.
- Separar logs de compensação para `historico_trades` e `fbq_hybrid_orders` para facilitar análise de regressão e correção de inconsistência.
- Adotar uma view materializada ou consulta consolidada para o resumo financeiro, reduzindo risco de timeout e melhorando velocidade de carregamento do painel.
- Implementar alerta quando `status_licenca` estiver falso, a campanha estiver fora da whitelist ou o entitlement efetivo não resolver nenhum ativo autorizado.
- Manter um checklist de publicação para cada release, cobrindo código, banco e documentação do Supabase.

---
### 📋 LEGENDA PADRÃO DE SINCRONISMO E AUDITORIA FBQ
* **Última Atualização:** 20/10/2026 às 21:01 (UTC−03:00)
* **Status da Migração SQL:** Aplicada segundo confirmação do usuário; `status_licenca` boolean, `selected_cryptos` CSV `text`, `market_updated_at` adicionado e view reconstruída.
* **painel_realtime:** [VERIFICADA - RECONCILIADA NA VIEW DO SUPABASE] GET respondeu 200 e mostrou a projeção de mercado/ordens; `market_updated_at` avança. A view não expõe `ativo`/`adx_val` do scanner e não é destino de escrita técnica.
* **scanner_telemetry:** A última consulta remota documentada retornou `404 / PGRST205` em 14/10/2026. Confirmar a situação atual e aplicar o SQL da seção 6.5 se a tabela ainda não existir.
* **Status do Login Remoto:** Validado pelo usuário; fallback local removido do backend.
* **Status Local do Runtime:** `.runtime_mode` permanece `ram_mock`; não mudar para `producao_binance` sem alterar sua semântica atual, pois esse modo bloqueia a varredura com estado `LOCKED`.
* **Fiação de Desbloqueio (Blur):** A cada evento SSE exige `m.license_active_flag === true` e o ativo normalizado presente em `m.allowed_string_tokens`.
* **Pipeline de Telemetria:** em modo normal, a engine grava indicadores em `scanner_telemetry`; em `ram_mock`, grava apenas em `scanner_test_telemetry`. A fonte de mercado real segue sendo `painel_realtime`; para o usuário de teste, o SSE não usa essa view como fallback para os dados sintéticos.
* **Solicitação pendente ao usuário — 20/10/2026 às 21:01 (UTC−03:00):** “Cole esse codigo sql no supabase:” — executar o bloco da seção 6.5.2 no SQL Editor e retornar o resultado. Ainda não recebemos confirmação de execução; a migração está pendente, não validada.
* **Próximos bloqueios de conformidade:** após confirmação do SQL, validar tabelas e permissões, reiniciar/acompanhar o stream, configurar e testar separadamente `WHALE_PULSE_RPC_URL`/`WHALE_PULSE_RPC_HTTP_URL` e conferir a conta de teste em `SIMULATION_TEST_USER_SLUGS`, com login dessa mesma conta de teste no dashboard. A execução de ordens simuladas ainda requer licença e ativos autorizados; nenhum evento on-chain sintético é criado. O listener atual é de transferências nativas EVM, não de tokens ERC-20. Não declarar os elementos 100% operacionais antes dessas validações.
---
