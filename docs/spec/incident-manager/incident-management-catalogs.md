# Incident Management Catalogs

This document is the source of truth for the controlled incident catalogs.

The API, database, filters, and shared contracts use the `Code` column. The frontend owns presentation and must use the locale-specific label for the active user language. Labels are not persisted or sent back as API values.

## Intake channels

| Code       | English  | Portuguese | Spanish            |
| ---------- | -------- | ---------- | ------------------ |
| `phone`    | Phone    | Telefone   | Teléfono           |
| `email`    | Email    | E-mail     | Correo electrónico |
| `web_chat` | Web chat | Chat web   | Chat web           |

## Types

| Code                     | English                | Portuguese                        | Spanish                          |
| ------------------------ | ---------------------- | --------------------------------- | -------------------------------- |
| `technical_issue`        | Technical issue        | Problema técnico                  | Problema técnico                 |
| `access_account_issue`   | Access/account issue   | Problema de acesso/conta          | Problema de acceso/cuenta        |
| `billing_issue`          | Billing issue          | Problema de faturamento           | Problema de facturación          |
| `service_request`        | Service request        | Solicitação de serviço            | Solicitud de servicio            |
| `information_request`    | Information request    | Solicitação de informação         | Solicitud de información         |
| `complaint`              | Complaint              | Reclamação                        | Queja                            |
| `security_privacy_issue` | Security/privacy issue | Problema de segurança/privacidade | Problema de seguridad/privacidad |

## Severities

| Code       | English  | Portuguese | Spanish |
| ---------- | -------- | ---------- | ------- |
| `critical` | Critical | Crítica    | Crítica |
| `high`     | High     | Alta       | Alta    |
| `medium`   | Medium   | Média      | Media   |
| `low`      | Low      | Baixa      | Baja    |

## Statuses

| Code               | English          | Portuguese         | Spanish               |
| ------------------ | ---------------- | ------------------ | --------------------- |
| `open`             | Open             | Aberto             | Abierto               |
| `in_progress`      | In progress      | Em andamento       | En progreso           |
| `pending_customer` | Pending customer | Aguardando cliente | Pendiente del cliente |
| `escalated`        | Escalated        | Escalonado         | Escalado              |
| `resolved`         | Resolved         | Resolvido          | Resuelto              |
| `closed`           | Closed           | Fechado            | Cerrado               |
| `reopened`         | Reopened         | Reaberto           | Reabierto             |

## Responsible areas

| Code                             | English                                     | Portuguese                                           | Spanish                                                 |
| -------------------------------- | ------------------------------------------- | ---------------------------------------------------- | ------------------------------------------------------- |
| `marketing_and_communications`   | Marketing and Communications                | Marketing e Comunicação                              | Marketing y Comunicación                                |
| `sales_and_business_development` | Sales and Business Development              | Vendas e Desenvolvimento de Negócios                 | Ventas y Desarrollo de Negocios                         |
| `human_resources_internal`       | Human Resources (Internal)                  | Recursos Humanos (Interno)                           | Recursos Humanos (Interno)                              |
| `talent_selection_operations`    | Talent Selection Operations (core business) | Operações de Seleção de Talentos (negócio principal) | Operaciones de Selección de Talento (negocio principal) |
| `corporate_training`             | Corporate Training                          | Treinamento Corporativo                              | Capacitación Corporativa                                |
| `customer_support_outsourced`    | Customer Support (outsourced service)       | Atendimento ao Cliente (serviço terceirizado)        | Atención al Cliente (servicio tercerizado)              |
| `technology_and_infrastructure`  | Technology and Infrastructure               | Tecnologia e Infraestrutura                          | Tecnología e Infraestructura                            |
| `executive_direction`            | Executive Direction                         | Direção Executiva                                    | Dirección Ejecutiva                                     |

## Frontend rules

- Use the code as the translation key and as the value submitted to the API.
- Do not translate or persist catalog codes.
- Keep the documented order when rendering select options and summaries.
- Add a new code only after the controlled catalog is approved by Nexova.
