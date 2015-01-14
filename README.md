Библиотека для работы c Alba
=============

Библиотека содержит два базовых класса AlbaService и AlbaCallback предназначенных для наследования.

AlbaService - сервис в Alba. Позволяет получить список доступных способов оплаты, инициировать транзакцию, получать информацию о ней. Необходимо создать по экземпляру на каждый существующий сервис.

AlbaCallback - обработчик для обратного вызова от Alba. Проверяет подпись и вызывает соответствующий параметру "command" метод.

В процессе работы может сработать исключение AlbaException.

Пример использования для инициации транзакции:

       from alba_client import AlbaService, AlbaException

       service = AlbaService(<service-id>, '<service-secret>')
       try:
           service.init_payment('mc', 10, 'Test', 'test@example.com', '71111111111')
       except AlbaException, e:
           print e

Пример использования для обратного вызова:

       from alba_client import AlbaCallback

       class MyAlbaCallback(AlbaCallback):
           def callback_success(self, data):
               # фиксирование успешной транзакции

       service1 = AlbaService(<service1-id>, '<service1-secret>')
       service2 = AlbaService(<service2-id>, '<service2-secret>')
       callback = MyAlbaCallback([service1, service2])
       callback.handle(<словарь-c-POST-данными>)
