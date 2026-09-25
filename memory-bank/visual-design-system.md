# Visual Design System

## Escopo

Este documento registra a linguagem visual atual do backoffice de incidentes da Nexova Solutions. Os valores abaixo refletem a implementação em `uis/backoffice/styles.css` e devem ser reutilizados antes de criar novos componentes ou telas.

## Direcao visual

- Interface operacional para equipes de Customer Support.
- Aparencia clara, profissional e funcional.
- Fundo claro com acentos verdes institucionais e laranja para acoes principais.
- Layout denso, organizado para leitura de filas, filtros, SLAs e historico.
- Cards usados para resumos e itens de trabalho, com bordas discretas e cantos pequenos.
- Evitar gradientes, excesso de decoracao e superficies arredondadas grandes.

## Tipografia

As fontes sao carregadas do Google Fonts:

- **DM Sans**: fonte principal da interface, textos, titulos, botoes, formularios e tabelas.
- **Space Mono**: fonte monoespaca para labels tecnicos, eyebrows, timestamps, IDs, SLA e cabecalhos de tabela.

Pesos utilizados:

- DM Sans 400: texto regular.
- DM Sans 500: pequenos destaques e marca.
- DM Sans 600: botoes, links de incidentes e valores enfatizados.
- DM Sans 700: marca e destaques fortes.
- Space Mono 400: metadados e labels.
- Space Mono 700: disponivel para informacoes tecnicas enfatizadas.

Hierarquia aproximada:

- H1: `clamp(28px, 3vw, 42px)`, line-height 1, letter-spacing `-0.06em`.
- H2: `22px`, letter-spacing `-0.04em`.
- H3: `18px`.
- Texto de tabela: `13px`.
- Texto secundario: `12px`.
- Eyebrow e labels tecnicos: `10px`, Space Mono, uppercase, letter-spacing `0.1em`.
- IDs e timestamps: `9px`, Space Mono.

## Cores

### Tokens principais

| Token      | Valor                                | Uso                                                             |
| ---------- | ------------------------------------ | --------------------------------------------------------------- |
| `--ink`    | `#17211b`                            | Texto principal, titulos e fundo de toast.                      |
| `--muted`  | `#6e776f`                            | Texto secundario, labels e metadados.                           |
| `--line`   | `#dfe5df`                            | Bordas e divisores.                                             |
| `--paper`  | `#f5f7f3`                            | Fundo geral da aplicacao.                                       |
| `--white`  | `#ffffff`                            | Superficies de painel, cards e modais.                          |
| `--green`  | `#155d45`                            | Navegacao lateral, identidade e acoes positivas.                |
| `--mint`   | `#d9eee2`                            | Botoes secundarios e superficies de apoio.                      |
| `--orange` | `#d86d36`                            | Acao principal, marcadores de auditoria e destaque de operacao. |
| `--red`    | `#b8443f`                            | Erros, atrasos, criticidade e acoes destrutivas.                |
| `--yellow` | `#c58b24`                            | Reserva para estados de atencao.                                |
| `--shadow` | `0 18px 50px rgba(31, 49, 38, 0.08)` | Elevacao suave de cards e paineis.                              |

### Cores complementares

- Texto claro na sidebar: `#eef7f0`.
- Marca secundaria: `#a6d6b7`.
- Fundo do simbolo da marca: `#c5e7d0`.
- Eyebrow da sidebar: `#9bc6a9`.
- Navegacao clara: `#d8eddf`.
- Navegacao ativa/hover: texto `--green`, fundo `#dbf0e2`.
- Status online: `#74d295`.
- Footer da sidebar: `#b8d8c1` e `#84b295`.
- Linha de tabela: `#edf0ed`.
- Hover de tabela: `#fafcf9`.
- Fundo de inputs: `#fbfcfa`.
- Overlay de modal: `rgba(22, 35, 27, 0.45)`.

## Estados semanticos

Os pills usam cores suaves para manter boa leitura em tabelas:

- Critical e Escalated: texto `--red`, fundo `#fae9e6`.
- High: texto `#97600b`, fundo `#fff0d6`.
- Medium e Pending customer: texto `#1e6375`, fundo `#e1f0f4`.
- Low e Open: texto `#286848`, fundo `#e2f3e8`.
- In progress e Reopened: texto `#735ca5`, fundo `#eee9fa`.
- Resolved: texto `#28735c`, fundo `#dcf2e5`.
- Closed: texto `#68716a`, fundo `#edf0ed`.

SLA:

- Dentro do prazo: `--green`.
- Atrasado: `--red`.
- Texto em Space Mono, `10px`.

## Layout e espacamento

- Shell desktop: sidebar fixa visualmente de `248px` e conteudo flexivel.
- Conteudo principal: largura maxima de `1440px`, padding horizontal responsivo entre `24px` e `70px`.
- Sidebar: padding `28px 20px` no desktop.
- Topbar: margem inferior de `32px`.
- Grid de resumo: quatro colunas, gap `14px`, margem inferior `28px`.
- Paineis: padding interno geralmente entre `18px` e `24px`.
- Grid de formularios: duas colunas, gap `15px`; uma coluna em telas pequenas.
- Action rows: gap `8px` e wrap permitido.
- Bordas: 1px, usando `--line` ou tons neutros equivalentes.

## Componentes

### Sidebar

- Fundo `--green`.
- Marca Nexova no topo.
- Navegacao com estado ativo/hover em fundo `#dbf0e2`.
- Indicador de operacao online no rodape.

### Botoes

- Base: sem borda, radius `6px`, padding `11px 15px`, peso 600.
- Primary: texto branco e fundo `--orange`.
- Quiet: texto `--green` e fundo `--mint`.
- Danger: texto `--red` e fundo `#fae9e6`.
- Hover: elevacao discreta com `translateY(-1px)`.
- Disabled: opacidade `0.45`, sem movimento e cursor bloqueado.

### Cards de resumo

- Fundo branco, borda `--line`, radius `8px` e sombra `--shadow`.
- Mostram contagem de incidentes abertos por severidade.
- Possuem um arco decorativo sutil no canto inferior direito.
- Sao interativos e levam para a fila filtrada pela severidade.

### Fila de incidentes

- Painel branco com borda e sombra.
- Busca e filtros ficam acima da tabela.
- Tabela possui largura minima de `850px` e scroll horizontal quando necessario.
- Linhas usam divisores suaves e hover `#fafcf9`.
- Incidentes sao links com destaque em hover usando `--orange`.

### Modal

- Overlay escuro translucido sobre a aplicacao.
- Superficie branca, largura maxima `700px`, altura maxima de `90vh`, scroll interno.
- Radius `8px` e sombra profunda.
- Usada para criacao, edicao e detalhe de incidentes.
- Seções internas usam divisores e padding vertical de `20px`.

### Formularios

- Labels pequenos e semibold em `--muted`.
- Campos com fundo `#fbfcfa`, borda `--line`, radius `5px` e foco orientado por `--green`.
- Textareas tem altura minima de `100px`.
- Acoes ficam alinhadas à direita e podem quebrar linha em telas menores.

### Auditoria e feedback

- Eventos de auditoria usam marcador circular em `--orange`.
- Timestamps e IDs usam Space Mono.
- Toast fica fixado no canto inferior direito, com fundo `--ink`, texto branco e animacao curta de entrada.
- Estados vazio e carregando usam texto centralizado em `--muted`.

## Responsividade

- Ate `900px`: sidebar vira uma faixa horizontal, footer e eyebrow da sidebar desaparecem, e filtros passam para duas colunas.
- Ate `600px`: topbar e cabecalho de painel empilham, filtros passam para uma coluna, grids de formulario/detalhe passam para uma coluna e a modal reduz o padding para `28px 20px`.
- Componentes com formato fixo devem manter dimensoes estaveis e nunca depender de texto para redimensionar controles.

## Regras de consistencia

- Reutilizar os tokens CSS existentes antes de introduzir novas cores.
- Manter a diferenca entre texto principal (`--ink`) e metadados (`--muted`).
- Usar `--orange` para acoes principais e destaque operacional, nao como cor dominante de toda a tela.
- Usar Space Mono apenas para dados tecnicos, nao para paragrafos longos.
- Manter radius entre `4px` e `8px`; evitar cards dentro de cards.
- Toda nova acao de status deve continuar visivel, agrupada e semanticamente colorida.
- Preservar contraste, foco visivel e leitura em telas pequenas.
