# steam_parser

Запуск: 

manage.py - Запуск парсера и сервера одновременно

analyze.py - Запуск парсера

server.py  - Запуск сервера

      
analyze.py: 

PAUSES - Включает/отключает паузы между переходами по ссылкам, предназначенно для имитаций действий человека,сервера стим меньше реагируют на такие запросы и шанс бана заметно уменьшается ,можно отключить при использовании нескольких прокси или впн.

USER_AGENTS - Юзер агенты, отправляются в качестве заголовка, имитируется использование реального браузера, при использовании стандартного юзер агента библиотеки requests запросы блокируютя уже на первых итерациях.

ID_CONTAINER - Свойство HTML содержащие id приложения стим

manage.py: 

ANALYZE_DELAY- Задержка между циклами парсинга, при двух - трех циклах парсинга в сутки количество необработанных страниц уменьшается до минимума, страницы заблокированные в основном цикле востанавлюваются дополнительными циклами (запускается автоматически)


Launch: 

manage.py - Start parser and server

analyze.py - Start parser

server.py - Start server
        
analyze.py: 

PAUSES - Enables / disables the pause between clicks on the links, designed to simulate human actions,steam server less responsive to such requests and the chance of a ban is significantly reduced ,can be disabled when using multiple proxies or VPN.

USER_AGENTS - User agents are sent as a header, simulated use of a real browser, when using the standard user agent library requests requests are blocked already in the first iterations.

ID_CONTAINER - HTML Property containing steam application id

manage.py:

ANALYZE_DELAY - Delay between cycles parsing, when two or three cycles of parsing a number of unprocessed pages is reduced to a minimum, the page is blocked in the main loop vosstanavlivayutsya additional cycles (starts automatically)        
