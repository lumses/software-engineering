workspace {
    name "Социальная сеть"
    description "Платформа для общения пользователей через публикации на стене и личные сообщения"

    !identifiers hierarchical

    model {
        user = person "Пользователь" "Пользователь социальной сети"

        social_network = softwareSystem "Социальная сеть" 

        user_system = softwareSystem "Система пользователей" {
            description "Управление пользователями социальной сети"

            auth_service = container "Сервис авторизации пользователей" {
                description "Авторизация пользователей"
                technology "Python/FastAPI"
            }
            // Временно используется общая БД, на лекции обсуждали, что заменим на Redis хранение одной из сущности
            user_db = container "База данных пользователей и записей на стене" {
                description "Хранит данные пользователей и записей на стене"
                technology "PostgreSQL"
                tags "Database"
            }

            user_service = container "Сервис обработки пользователей" {
                description "Обрабатывает запросы, связанные с пользователями" 
                technology "Python/FastAPI"
                -> user_db "сохранение и получение информации о пользователе" "JDBC"
            }
        }

        posts_system = softwareSystem "Система записей стен пользователя" {
            description "Управление записями на стенах пользователей"

            posts_service = container "Сервис обработки записей на стене" {
                description "Добавление записей на стену, загрузка стены пользователя"
                technology "Python/FastAPI"
                -> user_system.user_db "сохранение и получение записей стен пользователей" "JDBC"
            }
        }

        ptp_system = softwareSystem "Система сообщений" {
            description "Управление сообщениями пользователей"

            ptp_chat = container "PtP Чат" {
                description "Личный чат между двумя пользователями"
                technology "Python/FastAPI"
            }

            message_db = container "База данных сообщений" {
                description "Управляет сохранением и получением сообщений"
                technology "PostgreSQL"
            }

            message_service = container "Сервис обработки сообщений" {
                description "Управляет обработкой сообщений"
                technology "Python/FastAPI"
                -> message_db "сохранение и получение сообщений пользователей" "JDBC"
            }
        }

        user -> user_system "Использует для авторизации, создания и поиска пользователей"
        user -> user_system.user_service "Создает пользователя и производит поиск пользователей"
        user -> user_system.auth_service "Запрос на авторизацию"

        
        user -> posts_system "Использует для добавления записи на стену и загрузки стены пользователя"
        user -> posts_system.posts_service "Создает запись на стене"


        user -> ptp_system "Ипользует для обмена сообщениями с пользователями"
        user -> ptp_system.ptp_chat "Посылает сообщение пользователю"
        ptp_system.ptp_chat -> ptp_system.message_service "Обрабатывает сообщение"
        ptp_system.message_service -> ptp_system.ptp_chat "Возвращает список сообщений пользователя"
    
        user_system.auth_service -> user_system.user_service "Предоставляет доступ к сервису обработки пользователей"
        user_system.auth_service -> posts_system.posts_service "Предоставляет доступ к системе записей на стене"
        user_system.auth_service -> ptp_system.ptp_chat "Предоставляет доступ к системе сообщений"

        prod = deploymentEnvironment "PROD" {
            deploymentNode "Auth Server" {
                containerInstance user_system.auth_service
                instances 1
            }

            deploymentNode "User Server" {
                containerInstance user_system.user_service
                instances 1
            }

            deploymentNode "Posts Server" {
                containerInstance posts_system.posts_service
                instances 1
            }

            deploymentNode "Ptp Chat Server" {
                containerInstance ptp_system.ptp_chat
                instances 1
            }

            deploymentNode "Message Server" {
                containerInstance ptp_system.message_service
                instances 1
            }
 
            deploymentNode "Databases" {
                // Временно используется общая БД, на лекции обсуждали, что заменим на Redis хранение одной из сущности
                deploymentNode "User+Post database Server" {
                    containerInstance user_system.user_db
                    instances 2
                }

                deploymentNode "Message Server" {
                    containerInstance ptp_system.message_db
                    instances 2
                }
            }
        }
    }

    views {
        themes default

        properties { 
            structurizr.tooltips true
        }

        systemContext user_system "SystemContext" "Диаграмма контекста системы" {
            autoLayout lr
            include user user_system posts_system ptp_system
        }

        container user_system {
            include user user_system user_system.auth_service user_system.user_service user_system.user_db
            autoLayout
            title "Контекст пользователей"
        }

        container posts_system {
            include user posts_system.posts_service user_system.user_db user_system.auth_service
            autoLayout
            title "Контекст записей на стене пользователей"
        }
        container ptp_system {
            include user ptp_system.ptp_chat ptp_system.message_service ptp_system.message_db user_system.user_service
            autoLayout
            title "Контекст сообщений пользователей"
        }

        deployment user_system "PROD" "user_system_prod_deployment" {
            autoLayout
            include *
        }

        deployment posts_system "PROD" "posts_system_prod_deployment" {
            autoLayout
            include *
        }

        deployment ptp_system "PROD" "ptp_system_prod_deployment" {
            autoLayout
            include *
        }

        dynamic social_network "Case1" {
            description "Создание нового пользователя"
            autoLayout
            user -> user_system.auth_service "Отправляет запрос на авторизацию"
            user_system.auth_service -> user "Возвращается токен"
            user -> user_system.user_service "Создает нового пользователя"
            user_system.user_service -> user_system.user_db "Проверка существование пользователя"
            user_system.user_service -> user_system.user_db "Сохранение пользователя в базу данных"
        }

        dynamic social_network "Case2" {
            description "Поиск пользователя по логину"
            autoLayout
            user -> user_system.auth_service "Отправляет запрос на авторизацию"
            user_system.auth_service -> user "Возвращается токен"
            user -> user_system.user_service "Вводит логин пользователя"
            user_system.user_service -> user_system.user_db "Поиск по логину в базе данных"
        }

        dynamic social_network "Case3" {
            description "Поиск пользователя по маске имя и фамилии"
            autoLayout
            user -> user_system.auth_service "Отправляет запрос на авторизацию"
            user_system.auth_service -> user "Возвращается токен"
            user -> user_system.user_service "Вводит маску имени и фамилии пользователя"
            user_system.user_service -> user_system.user_db "Поиск по маске и фамилии в базе данных"
        }

        dynamic social_network "Case4" {
            description "Добавление записи на стену"
            autoLayout
            user -> user_system.auth_service "Отправляет запрос на авторизацию"
            user_system.auth_service -> user "Возвращается токен"
            user -> posts_system.posts_service "Создает новую запись на стене"
            posts_system.posts_service -> user_system.user_db "Сохранение нового поста в базу данных"
        }

        dynamic social_network "Case5" {
            description "Загрузка стены пользователя"
            autoLayout
            user -> user_system.auth_service "Отправляет запрос на авторизацию"
            user_system.auth_service -> user "Возвращается токен"
            user -> posts_system.posts_service "Запрашивает записи на стене пользователя"
            posts_system.posts_service -> user_system.user_db "Получает данные о записях на стене пользователя"
        }

        dynamic social_network "Case6" {
            description "Отправка сообщения пользователю"
            autoLayout
            user -> user_system.auth_service "Отправляет запрос на авторизацию"
            user_system.auth_service -> user "Возвращается токен"
            user -> ptp_system.ptp_chat "Отправляет сообщение"
            ptp_system.ptp_chat -> ptp_system.message_service "Создает сообщение"
            ptp_system.message_service -> ptp_system.message_db "Сохраняет сообщение"
        }

        dynamic social_network "Case7" {
            description "Получение списка сообщения для пользователя"
            autoLayout
            user -> user_system.auth_service "Отправляет запрос на авторизацию"
            user_system.auth_service -> user "Возвращается токен"
            user -> ptp_system.ptp_chat "Запрашивает сообщения из чата"
            ptp_system.ptp_chat -> ptp_system.message_service "Получает список собщений для пользователя"
            ptp_system.message_service -> ptp_system.message_db "Предоставляет из базы данных список собщений для пользователя"
        }

        styles {
            element "SoftwareSystem" {
                background #788B9F
                color #ffffff
            }

            element "Container" {
                background #85F09C
                color #000000
            }

            element "Person" {
                shape Person
                background #B7600E
                color #ffffff
            }

            element "Dynamic" {
                background #EA8DF5
                color #000000
            }
        }
    }
}