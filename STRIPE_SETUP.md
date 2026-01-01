# Configuração Oficial do Stripe para TaskFlowAI

Para que o sistema de pagamentos funcione e libere as funções Premium automaticamente, siga exatamente os passos abaixo no seu Dashboard do Stripe.

## 1. Obter Chaves de API
1. Acesse: [Stripe Dashboard > Developers > API Keys](https://dashboard.stripe.com/apikeys)
2. Copie a **Publishable Key** (`pk_live_...` ou `pk_test_...`).
3. Copie a **Secret Key** (`sk_live_...` or `sk_test_...`).
4. Atualize seu arquivo `.env` na PythonAnywhere (ou local):
   ```bash
   STRIPE_PUBLIC_KEY=sua_chave_publica
   STRIPE_SECRET_KEY=sua_chave_secreta
   ```

## 2. Criar Produtos e Planos
Você precisa criar os produtos que coincidam com o sistema.

1. Acesse: [Stripe Dashboard > Products](https://dashboard.stripe.com/products)
2. Clique em **+ Add Product**.
3. **Plano PRO**:
   - Name: `TaskFlowAI Pro`
   - Pricing Model: Standard pricing
   - Price: `R$ 29,90` / Month
   - Copie o **Price ID** (começa com `price_...`) gerado.
4. **Plano BUSINESS**:
   - Name: `TaskFlowAI Business`
   - Price: `R$ 79,90` / Month
   - Copie o **Price ID**.

> **IMPORTANTE**: Após criar os preços, você deve ir no **Admin Console** do TaskFlowAI (`/taskflowai/admin_console`), editar os Planos Pro e Business e colar esses IDs nos campos "Monthly Stripe Price ID".

## 3. Configurar Webhook (Crucial para Liberação Automática)
O webhook é quem avisa o sistema que o pagamento foi aprovado.

1. Acesse: [Stripe Dashboard > Developers > Webhooks](https://dashboard.stripe.com/webhooks)
2. Clique em **+ Add Endpoint**.
3. **Endpoint URL**: 
   - Se for produção: `https://seudominio.pythonanywhere.com/taskflowai/stripe_webhook`
   - (Atenção ao `/taskflowai` no caminho se estiver usando subpasta).
4. **Events to listen for** (Selecione estes eventos):
   - `checkout.session.completed` (Quando o usuário paga o checkout)
   - `invoice.paid` (Quando a renovação mensal ocorre)
   - `customer.subscription.deleted` (Quando cancela ou expira)
5. Clique em **Add Endpoint**.
6. Copie o **Signing Secret** (`whsec_...`) que aparece no topo da tela.
7. Atualize seu `.env`:
   ```bash
   STRIPE_WEBHOOK_SECRET=whsec_seu_secret_aqui
   ```

## 4. Diferencial Competitivo (Dicas)
Para bater de frente com Notion/ClickUp:
- **Preço Local**: Cobre em Reais (BRL). O Stripe aceita Pix e Boleto, configure isso no "Payment Methods" do Stripe. Notion/ClickUp cobram em Dólar.
- **Trial Grátis**: No Stripe, ao criar o preço, você pode definir "Free Trial Days" (ex: 14 dias). O TaskFlowAI suporta isso.

---
**Status Atual do Sistema**:
O código atual já tem a *estrutura*, mas faltava a rota de recepção do webhook. Eu estou adicionando essa rota agora para garantir que, assim que você configurar acima, funcione instantaneamente.
