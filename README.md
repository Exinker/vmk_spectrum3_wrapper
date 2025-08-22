# `vmk_spectrum3` wrapper


Обвертка драйвера `vmk_spectrum3`, используемого для регистрации спектров на малогабаритном спектрометре [Колибри-2](https://www.vmk.ru/product/spektrometry/kolibri-2_-_malogabaritnyy_mnogokanalnyy_spektrome.html) с несколькими сборками линеек (БЛПП-2000 или БЛПП-4000).


## Author Information:
Павел Ващенко (vaschenko@vmk.ru)
[ВМК-Оптоэлектроника](https://www.vmk.ru/), г. Новосибирск 2025 г.

## Installation
### Установка Python
Для работы требуется установить Python версии 3.12. *Ссылку на последнюю версию можно скачать [здесь](https://www.python.org/downloads/).*

### Установка виртуального окружения
Зависимости, необходимые для работы приложения, необходимо установить в виртуальное окружение `.venv`. Для этого в командной строке необходимо:
1. Установить пакетный менеджер `uv`: `pip install uv`;
2. Клонировать проект с удаленного репозитория: `git clone https://github.com/Exinker/vmk_spectrum3_wrapper.git $HOME/code/vmk_spectrum3`;
3. Зайти в директорию с проектом: `cd $HOME/code/vmk_spectrum3`;
4. Запустить jupyter notebook: `uv run jupyter notebook`;

## Usage

### ENV
Преременные окружения проекта:
- `LOGGING_LEVEL: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' = 'INFO'` - уровень логгирования;

Преременные окружения устройства:
- `DEFAULT_DETECTOR=BLPP4000` - тип детектора (поддерживается `BLPP2000` и `BLPP4000`);
- `DEFAULT_ADC=18` - разрядность АЦП;

Преременные окружения измерения:
- `CHANGE_EXPOSURE_TIMEOUT=1000` - время релаксации после изменения времени экспозиции;
