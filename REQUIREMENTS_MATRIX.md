# Требование → артефакт → проверка

Матрица проверяет **содержание проектного решения**, а не внедрение систем клиники. Проверка 08.11.2026.

| Требование | Артефакт | Проверка |
|---|---|---|
| MVP 3 мес / годовые бизнес- и технические цели | [README](README.md), [Task4.2](Task4.2/README.md) | Есть 500/50k, −30%, 70%, чек, P99, 99.95%, этапы; допущения не выданы за измерения |
| Проблемы, признаки, влияние; надёжность/безопасность/масштаб | [Task1](Task1/README.md) | 14 строк, все INT-001…011 и SD-001…009 связаны с последствиями; гипотеза SD-007 отмечена |
| C4 L1, мобильный участник, старые и новые системы | [Task2](Task2/README.md), [схема](Task2/context.drawio) | Центральная система и соседние системы типизированы; 17 потоков; PDF визуально проверен |
| Обоснование каждого нового взаимодействия и стилей | [Task2, таблица](Task2/README.md) | REST, события, ACL, общая Saga; target/переходный путь различены |
| LIS: сравнение решений и инструментов | [Task3.1](Task3.1/README.md) | 4 альтернативы, задержка/пики/эксплуатация/доставка; выбор RabbitMQ обоснован |
| LIS: текст и полная схема до приложения | [Task3.1](Task3.1/README.md), [схема](Task3.1/data-flow.drawio) | Захват, durable storage, publish confirm, ack после commit, dedup, DLQ/replay, сверка, auth и чтение |
| UML Sequence успешной записи/ДМС/оплаты/анализов | [Task3.2](Task3.2/README.md), [Sequence](Task3.2/success-sequence.drawio) | Все 4 бизнес-шага, подтверждения, 202 и COMPLETED различены; видимые lifelines и сообщения |
| Выбор Saga в 3–4 предложениях | [Task3.2](Task3.2/README.md) | 4 предложения, оркестрация, durable журнал и цена выбора |
| Таблица компенсаций 3 шагов | [Task3.2](Task3.2/README.md) | Врач, оплата и lab, три колонки; UNKNOWN и возврат не названы мгновенным rollback |
| Входная идемпотентность | [Task3.2](Task3.2/README.md) | Scope/hash/unique insert/повтор/409; уникальность slot и ключи шагов, PSP guard |
| YAML /appointments GET, фильтр и limit/offset | [Task3.3](Task3.3/README.md), [OpenAPI 3.0](Task3.3/openapi.yaml) | Валидатор PASS; только текущий пациент, сортировка и семантика upcoming заданы |
| Auth, 200/401/500 и примеры | [контракт](Task3.3/openapi.yaml) | Bearer JWT; все response examples проверены по schema; дополнены 400/403/429/503 |
| Версионирование и противоречие 3.2/3.0 | [Task3.3](Task3.3/README.md), [3.2](Task3.3/openapi-3.2.yaml) | Обе версии валидны; автоматическое сравнение подтверждает единую бизнес-спецификацию |
| Timeout/retry/fallback для 1С и PSP | [Task4.1](Task4.1/README.md) | Секунды, полное число попыток, интервалы, deadline; mutation/status различены |
| Circuit Breaker и приоритет | [Task4.1](Task4.1/README.md) | Приоритет 1С, CLOSED/OPEN/HALF_OPEN, критерии и общие квоты |
| Разгрузка 1С с C4 L1 | [Task4.1](Task4.1/README.md), [схема](Task4.1/policy-context.drawio) | Фасад/read model, master, freshness, UNKNOWN, необходимые контракты и расчёт |
| Две критичные системы, горизонтальный план, ограничение и решение | [Task4.2](Task4.2/README.md) | Расписание и CRM; четыре колонки; writer/lag не скрыты репликами |
| Схема auth, протокол, токен | [Task4.3](Task4.3/README.md), [схема](Task4.3/authentication.drawio) | Native OIDC/PKCE, внешний браузер, Bearer, хранение/отзыв, object authorization |
| Rate limiting двух сценариев | [Task4.3](Task4.3/README.md) | Публичный поиск и авторизованный POST, лимит/429/Retry-After; общий bucket и отказ limiter |
| Защита каналов | [Task4.3](Task4.3/README.md) | TLS/mTLS, legacy boundary, минимизация, секреты, replay, SQL/XXE, аудит |
| 8 каталогов; редактируемые диаграммы и читаемость | Все Task-каталоги | README в каждом; 5 комплектов drawio/SVG/PDF/PNG; локальные ссылки и границы элементов проверены |
| Публичный Solution-Health, PR, отправка | GitHub и Practicum | Проверяются отдельно после публикации; подтверждение платформы хранится приватно и не подменяется этой матрицей |
