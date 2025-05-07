## Лабораторная работа №5
### Вариант №1 ("Социальная сеть")

1. Для данных, хранящихся в реляционной базе PotgreSQL реализуйте шаблон
сквозное чтение и сквозная запись (Пользователь/Клиент …);
2. В качестве кеша – используйте Redis
3. Замерьте производительность запросов на чтение данных с и без кеша с
использованием утилиты wrk https://github.com/wg/wrk изменяя количество
потоков из которых производятся запросы (1, 5, 10)
4. Актуализируйте модель архитектуры в Structurizr DSL
5. Ваши сервисы должны запускаться через docker-compose командой docker-
compose up (создайте Docker файлы для каждого сервиса)

Тест без кэша:
Тест [NO_CACHE] с 1 потоками:
Running 10s test @ http://localhost:8000/users/search
  1 threads and 10 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    10.83ms    4.86ms  49.82ms   85.04%
    Req/Sec     0.95k   200.51     1.37k    66.00%
  9460 requests in 10.02s, 2.07MB read
Requests/sec:    943.71
Transfer/sec:    211.05KB

Тест [NO_CACHE] с 5 потоками:
Running 10s test @ http://localhost:8000/users/search
  5 threads and 10 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     9.85ms    4.24ms  56.56ms   86.95%
    Req/Sec   208.37     35.08   272.00     71.60%
  10412 requests in 10.04s, 2.27MB read
Requests/sec:   1036.88
Transfer/sec:    231.88KB

Тест [NO_CACHE] с 10 потоками:
Running 10s test @ http://localhost:8000/users/search
  10 threads and 10 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    10.83ms    4.39ms  44.28ms   85.96%
    Req/Sec    94.38     17.45   140.00     78.80%
  9448 requests in 10.05s, 2.06MB read
Requests/sec:    940.04
Transfer/sec:    210.22KB

Тест с кэшем:
Тест [CACHE] с 1 потоками:
Running 10s test @ http://localhost:8000/users-redis/cached-search
  1 threads and 10 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     6.33ms    2.89ms  51.45ms   91.71%
    Req/Sec     1.62k   215.34     1.97k    73.00%
  16186 requests in 10.01s, 3.53MB read
Requests/sec:   1616.89
Transfer/sec:    361.59KB

Тест [CACHE] с 5 потоками:
Running 10s test @ http://localhost:8000/users-redis/cached-search
  5 threads and 10 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     6.09ms    2.38ms  35.47ms   90.01%
    Req/Sec   337.30     42.39   410.00     66.80%
  16832 requests in 10.03s, 3.68MB read
Requests/sec:   1677.98
Transfer/sec:    375.25KB

Тест [CACHE] с 10 потоками:
Running 10s test @ http://localhost:8000/users-redis/cached-search
  10 threads and 10 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     6.09ms    2.69ms  46.72ms   91.82%
    Req/Sec   169.76     22.05   232.00     74.40%
  16965 requests in 10.03s, 3.71MB read
Requests/sec:   1691.15
Transfer/sec:    378.20KB
