## Python API
Работа с устройством производится через класс `pyspectrum3.DeviceManager`.
Правильный порядок работы c библиотекой: 
```python
import pyspectrum3 as ps3
import numpy as np


def on_frame(data: np.ndarray):
    pass

def on_status(statuses: Dict[str, ps3.AssemblyStatus]):
    pass

def on_error(error: AsyncDriverException):
    pass
    

# Создание экземпляра класса устройства
dev = ps3.DeviceManager()

# Инициализация драйвера вручную.
dev.initialize(ps3.DeviceConfigFile([ps3.AssemblyConfigFile("10.116.220.2"), ps3.AssemblyConfigFile("10.116.220.3")]))

# Установка колбеков
# Колбэки должны быть установлены до вызова метода run(), иначе события могут быть пропущены
dev.set_frame_callback(on_frame)   # on_frame будет вызываться при получении кадра с устройства
dev.set_status_callback(on_status) # on_status будет вызываться при изменении состояния устройства
dev.set_error_callback(on_error)

# Запускает поток, управляющий устройством, и выполняет подключение к устройству
# НЕ БЛОКИРУЕТ текущий поток
dev.connect()

while something:
    do something

# отключается от устройства
dev.disconnect()
```
### Класс DeviceManager
#### Конструктор
Не принимает аргументы и просто создает пустые объекты
#### Служебные методы
##### `def initialize(cfg: ps3.DeviceConfigFile)`
Инициализация драйвера с помощью конфигурационной структуры в которой хранятся адреса сборок и их типы (по умолчанию МАСИ Ethernet)
##### `def set_frame_callback(on_frame)`
Устанавливает колбек, который будет вызываться пр получении кадра с устройства
##### `def set_status_callback(on_status)`
Устанавливает колбек, который будет вызываться при обновлении статуса устройства
##### `def set_error_callback(on_error)`
Устанавливает колбек, который будет вызываться при ошибке во время неблокирующей операции (чтения с устройства)
##### `def connect()`
Запускает потоки, работающие с устройством, начинает подключение к нему. Не блокирует выполнение текущего потока
##### `def disconnect()`
Отключается от устройства, останавливает потоки. Этот метод **нельзя** вызывать в колбеке on_status
#### Получение конфигурационной структуры ps3.DeviceConfigFile
##### `ps3.AutoConfig().config()`
Получение конфигурационной структуры с информацией о всех сборках в сети 
##### `ps3.ConfigFileParser(path: str).read_file()`
Получение конфигурационной структуры из xml файла вида:
```xml
<Device>
    <Assembly>
        <Addr>10.116.220.2</Addr>
        <Type>0</Type>
    </Assembly>
    <Assembly>
        <Addr>10.116.220.3</Addr>
        <Type>0</Type>
    </Assembly>
</Device>
```
Так же есть метод `write_file(cfg: DeviceConfigFile)` для создания xml файла.
#### Команды устройства
Комманды для чтения (`read` и `read_broadcast`) работают ассинхронно. Для получения результатов выполнения этих комманд используются `frame_callback` и `error_callback`. Остальные же комманды работают синхронно. Если синхронную комманду запустить во время чтения, то она заблокируется пока чтение не закончится. Все комманды работают сразу со всеми сборками которые были указаны при инициализации.
##### `def set_exposure(microseconds: int)`
Устанавливает экспозицию устройства
##### `def set_double_exposure(t1: int, r1: int, t2: int, r2: int)`
Устанавливает двойную экспозицию устройства
##### `write_cr(b0: bool, b1: bool, b2: bool)`
Записывает три бита контрольного устройства. На моём устройстве средний бит управляет шторкой
##### `read(n_frames: int)`
Запускает чтение данных с устройства (не используется broadcast пакет для синхронизации сборок и сброса таймеров)
##### `read_broadcast(n_frames: int)`
Запускает чтение данных с устройства (используется broadcast пакет для синхронизации сборок и сброса таймеров)
##### `cancel_reading()`
Отменяет запущенное ранее чтение данных с устройства до считывания всех кадров (но не посередине одного кадра)

### Статусы устройства
В колбек `on_status` приходят словари `Dict[str, ps3.AssemblyStatus]`. Ключ - это адрес сборки, а значение - это enum с её статусом.
- `AssemblyStatus.ALIVE` - подключена и ожидает комманды
- `AssemblyStatus.BYSY` - приходит после начала выполнения чтения
- `AssemblyStatus.DISCONNECTED` - сборка отключена

### Структура AsyncDriverException
В колбэк `on_error` приходит структура ps3.AsyncDriverException с методами:
##### `get_messages() -> List[str]`
Получить сообщения об ошибках (имеет вид stack трейса, т.е. сообщения могут добавляться на каждом пробросе ошибки)
##### `add_message(msg: str)`
Добавляет сообщение к ошибке
##### `get_exception_producer() -> ps3.ExceptionProducer`
Получить enum с местом откуда вылетело исключение (`ASSEMBLY` или `DEVICE`)
##### `get_exception_type() -> ps3.ExceptionType`
Получить enum с типом ошибки (NETWORK_EXCEPTION, CONFIG_EXCEPTION, INVALID_ARGUMENT, CALLBACK_EXCEPTION, UNKNOWN_EXCEPTION)

### Конфигурационный файл driver.ini
В файл `driver.ini` вынесены константы BROADCAST с broadcast адресом сети (10.116.220.255), UDP и TCP портом МАСИ. Этот файл **должен** находиться в директории в которой используется драйвер 

## C++ api
C++ API повторяет питоновское, единственное важное отличие:
В колбек `on_data` приходит структура `SpectrumFrame`, после обработки которой необходимо освободить память:
```c++
dev.setFrameCallback([&](auto f){  
    std::cout<<"Got frame #" << cntr++ << "; Value is " << f.data[0]<<std::endl;  
    delete[] f.data;  
});
```

## Сборка
```sh
git clone --recursive  https://github.com/Foxtezy/libspectrum3.git
cd libspectrum3
mkdir build
cd build
cmake .. 
cmake --build . # this will build the library and the c++ example
cd ..
python -m pip wheel . # this will build whl file
```
## Примечания
Перед использованием на линуксе необходимо выполнить команду `sudo sysctl -w "net.ipv4.tcp_window_scaling=0"`