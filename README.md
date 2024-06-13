# Задание соискателям на должность разработчика Python
Решение заданий отправлять на адрес Евгении Лушиной <e-lushina@it-serv.ru> в виде архива проекта, либо в виде ссылки на собственный репозиторий.
Делать форки и ветки от текущего проекта не рекомендуется. 

Дополнительное задание выполнять не обязательно, но будет плюсом.

# Задание
Разработать тесты с использованием стандартной библиотеки 
[unittest](https://docs.python.org/3/library/unittest.html "Unit testing framework").
При необходимости исправить ошибки.

Наличие предложений по доработке приветствуется.

# Дополнительное задание
Разработать [Docker Compose](https://docs.docker.com/compose/ "Overview of Docker Compose") для запуска стека 
[ELK](https://www.elastic.co/what-is/elk-stack "ELK Stack") и [Jaeger](https://www.jaegertracing.io/ "Jaeger"). 
Jaeger должен разворачиваться отдельными компонентами (agent, collector и query) и подключаться к Elasticsearch 
из стека ELK.

Настроить Logstash для приема логов из приложения.

Подготовить тестовый пример формирующий лог и трассировку.


# Dependencies

Don't forget to install the dependencies by running the following command from the app's root directory:
```sh
pip install -r requirements.txt
```

# Testing

To test this app, run the following command from the app's root directory:
```sh
python -m unittest discover -s tests
```