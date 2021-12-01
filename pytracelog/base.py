"""
:mod:`base` -- Базовые методы
===================================
.. moduleauthor:: Aleksey Guzhin <a-guzhin@it-serv.ru>
"""
from os import environ
from typing import (
    Union,
    Optional,
    List,
    Callable
)
from logging import (
    getLogRecordFactory,
    setLogRecordFactory,
    WARNING,
    basicConfig,
    Handler,
    _checkLevel,
    root
)

from logstash_async.formatter import LogstashFormatter
from logstash_async.handler import AsynchronousLogstashHandler
from opentelemetry.trace import (
    set_tracer_provider,
)
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import (
    SERVICE_NAME,
    Resource
)
from opentelemetry.sdk.trace import (
    TracerProvider
)
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

from pytracelog.logging.handlers import (
    StdoutHandler,
    StderrHandler,
    TracerHandler,
)


__all__ = (
    'PyTraceLog',
    'LOGSTASH_HOST',
    'LOGSTASH_PORT',
    'OTEL_EXPORTER_JAEGER_AGENT_HOST',
)


LOGSTASH_HOST = 'LOGSTASH_HOST'
LOGSTASH_PORT = 'LOGSTASH_PORT'

OTEL_EXPORTER_JAEGER_AGENT_HOST = 'OTEL_EXPORTER_JAEGER_AGENT_HOST'


class PyTraceLog:
    """
    Класс для инициализации подсистем логирования и трассировки:
     * Инициализация базового логгера Python с отправкой записей журнала в stderr и stdout (в зависимости от
       уровня записи журнала);
     * Инициализация отправки записей журнала напрямую в Logstash;
     * Инициализация трассировки;
     * Добавление дополнительных атрибутов к записям журнала.

    """
    _old_factory: Optional[Callable] = None
    _handlers: Optional[List[Handler]] = list()

    @staticmethod
    def init_root_logger(
            level: Union[str, int] = WARNING,
    ) -> None:
        """
        Инициализация логирования: инициализирует root логгер
        LOGSTASH_HOST.

        :param level: Уровень логирования
        """
        # Выходим, т.к. все уже инициализировано
        if len(root.handlers) != 0:
            return

        if isinstance(level, str):
            level = _checkLevel(level.upper())

        # Добавление обработчика для вывода логов в stdout
        stdout_handler = StdoutHandler()
        PyTraceLog._handlers.append(stdout_handler)

        # Добавление обработчика для вывода логов в stderr
        stderr_handler = StderrHandler()
        PyTraceLog._handlers.append(stderr_handler)

        basicConfig(
            level=level,
            handlers=PyTraceLog._handlers
        )

    @staticmethod
    def extend_log_record(**_kwargs) -> None:
        """
        Расширение записи лога статическими атрибутами

        :param _kwargs: Список атрибутов со значениями
        """
        old_factory = getLogRecordFactory()
        PyTraceLog._old_factory = old_factory

        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)

            for k, v in _kwargs.items():
                record.__setattr__(k, v)

            return record

        setLogRecordFactory(record_factory)

    @staticmethod
    def init_logstash_logger(
            level: Union[str, int] = WARNING,
            message_type: str = 'python',
            index_name: str = 'python'
    ) -> None:
        """
        Инициализация Logstash логгера: добавление обработчика для отправки записей журналов в Logstash

        :param level: Уровень логирования (только если root логгер еще не инициализирован)
        :param message_type: Тип сообщения
        :param index_name: Наименование индекса в Elasticsearch
        """
        # Ничего не делаем, если обработчик уже есть в списке
        for handler in PyTraceLog._handlers:
            if isinstance(handler, AsynchronousLogstashHandler):
                return

        logstash_host = environ.get(LOGSTASH_HOST)

        # Инициализируем обработчик, только если задан хост Logstash
        if logstash_host:
            logstash_formatter = LogstashFormatter(
                message_type=message_type,
                extra_prefix=None,
                metadata={
                    'beat': index_name
                }
            )
            logstash_handler = AsynchronousLogstashHandler(
                host=logstash_host,
                port=int(environ.get(LOGSTASH_PORT, 5959)),
                database_path=None
            )
            logstash_handler.setFormatter(fmt=logstash_formatter)
            PyTraceLog._handlers.append(logstash_handler)

            # Если root логгер инициализирован, добавляем обработчик
            if len(root.handlers) != 0:
                root.addHandler(hdlr=logstash_handler)
            # Иначе выполняем его инициализацию
            else:
                basicConfig(
                    level=level,
                    handlers=PyTraceLog._handlers
                )

    @staticmethod
    def init_tracer(service: str) -> None:
        """
        Инициализация трассировки, если задана переменная окружения OTEL_EXPORTER_JAEGER_AGENT_HOST.

        :param service: Наименование сервиса
        """
        if not environ.get(OTEL_EXPORTER_JAEGER_AGENT_HOST):
            return

        jaeger_exporter = JaegerExporter()
        span_processor = BatchSpanProcessor(span_exporter=jaeger_exporter)
        tracer_provider = TracerProvider(
            resource=Resource.create({
                SERVICE_NAME: service
            })
        )
        tracer_provider.add_span_processor(span_processor=span_processor)
        set_tracer_provider(tracer_provider=tracer_provider)

        # Добавляем к атрибутам для логирования идентификаторы трассировки
        LoggingInstrumentor().instrument(tracer_provider=tracer_provider)

    @staticmethod
    def init_tracer_logger(
            level: Union[str, int] = WARNING,
    ) -> None:
        """
        Инициализация обработчика для для экспорта записей журнала в систему трассировки

        :param level: Уровень логирования (только если root логгер еще не инициализирован)
        """
        # Ничего не делаем, если обработчик уже есть в списке
        for handler in PyTraceLog._handlers:
            if isinstance(handler, TracerHandler):
                return

        tracer_handler = TracerHandler()
        PyTraceLog._handlers.append(tracer_handler)

        # Если root логгер инициализирован, добавляем обработчик
        if len(root.handlers) != 0:
            root.addHandler(hdlr=tracer_handler)
        # Иначе выполняем его инициализацию
        else:
            basicConfig(
                level=level,
                handlers=PyTraceLog._handlers
            )

    @staticmethod
    def reset() -> None:
        """
        Сброс настроек
        """
        root.level = WARNING

        if PyTraceLog._old_factory:
            setLogRecordFactory(PyTraceLog._old_factory)
            PyTraceLog._old_factory = None

        for handler in PyTraceLog._handlers:
            root.removeHandler(hdlr=handler)

        PyTraceLog._handlers = list()
