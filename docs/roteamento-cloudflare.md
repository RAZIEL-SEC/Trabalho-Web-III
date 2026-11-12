# Rotas diretas do site institucional (Cloudflare Workers)

## Diagnóstico

O site usa React Router com rotas client-side (/quem-somos, /nossas-acoes, /como-ajudar e /contato). Ao clicar em um NavLink, o React Router troca a tela no navegador sem solicitar um novo documento ao servidor. Porém, ao abrir /contato diretamente, atualizar a página ou seguir um link HTML tradicional, o navegador faz uma requisição HTTP para /contato.

A versão ativa do Worker consultada em 12/11/2026 estava com html_handling: auto-trailing-slash e not_found_handling: none.

Como não existe um arquivo físico chamado contato no diretório de assets, a Cloudflare não devolve index.html para a rota e a navegação direta falha. O mesmo problema afeta as outras rotas React. Isso explica por que a página podia funcionar ao clicar na navbar, mas não ao abrir/atualizar a URL.

## Correções neste branch

1. wrangler.jsonc define assets.directory: ./dist e not_found_handling: single-page-application. A Cloudflare passa a servir index.html em requisições de navegação que não correspondam a um asset, permitindo que o React Router resolva a URL.
2. O botão Fale conosco em Como Ajudar usa Link do React Router, em vez de <a href>, evitando um reload desnecessário.
3. O CTA interno de Nossas Ações também usa Link.
4. /fale-conosco foi adicionado como alias que redireciona para /contato.
5. npm run deploy compila o Vite e publica os assets usando Wrangler v4 e a configuração que ativa o fallback SPA.

## Publicação

Na raiz deste projeto (branch com as correções):

```bash
npm install
npm run build
npx wrangler@4 deploy --config wrangler.jsonc
```

Ou use npm run deploy para executar build + deploy em sequência. O comando publica no Worker trabalho-web-iii; requer autenticação Wrangler na conta Cloudflare correta.

## Verificação após publicação

Testar em janela anônima ou com cache desabilitado:

- /
- /contato
- /fale-conosco (deve redirecionar para /contato)
- /quem-somos
- /nossas-acoes
- /como-ajudar

Para cada rota, testar abrir a URL diretamente, atualizar com F5 e navegar pelos botões internos. Não considerar resolvido até todas retornarem a aplicação e o React Router mostrar a página correta.

## Observação sobre deploy

A integração de Workers Builds do Worker trabalho-web-iii não retornou triggers vinculados a um repositório nesta conta; as versões recentes foram marcadas como uploads pelo Dashboard. Portanto, o merge do código não publica automaticamente o Worker. É necessário executar o comando de deploy acima com Wrangler ou configurar separadamente a integração de build.
