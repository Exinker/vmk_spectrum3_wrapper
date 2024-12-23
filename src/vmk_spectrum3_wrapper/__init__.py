import dotenv 
import pkg_resources

from vmk_spectrum3_wrapper.loggers import setdefault_logger


dotenv.load_dotenv()
setdefault_logger()


distribution = pkg_resources.get_distribution('vmk-spectrum3-wrapper')
NAME = distribution.project_name
DESCRIPTION = 'It is a wrapper for `vmk_spectrum3` library.'
VERSION = distribution.version

AUTHOR_NAME = 'Pavel Vaschenko'
AUTHOR_EMAIL = 'vaschenko@vmk.ru'

ORGANIZATION_NAME = 'VMK-Optoelektronika'


__version__ = VERSION
