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
           response = service.init_payment('mc', 10, 'Test', 'test@example.com', '71111111111')
       except AlbaException, e:
           print e
           
Проверка, требуется ли 3-D secure:

       card3ds = response.get('3ds')
       if card3ds:
           # Требуется 3-D secure
           
Если 3-D secure требуется, то необходимо сделать POST запрос на адрес card3ds['ACSUrl'] с параметрами:
       
       PaReq - с значением card3ds['PaReq']
       MD - с значением card3ds['MD']
       TermUrl - URL обработчика, на вашем сайте. На него будет возвращён пользователь после прохождения 
        3DS авторизации на сайте банка-эмитента карты. Этот URL нужно сформировать так, 
        чтобы в нём передавалась информация о транзакции: рекомендуется передавать service_id, tid и order_id 
        (если транзакция создана с ним).
       

Пример использования для обратного вызова:

       from alba_client import AlbaCallback

       class MyAlbaCallback(AlbaCallback):
           def callback_success(self, data):
               # фиксирование успешной транзакции

       service1 = AlbaService(<service1-id>, '<service1-secret>')
       service2 = AlbaService(<service2-id>, '<service2-secret>')
       callback = MyAlbaCallback([service1, service2])
       callback.handle(<словарь-c-POST-данными>)
       



