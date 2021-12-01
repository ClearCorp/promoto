# pylint: disable-all
import logging

_logger = logging.getLogger(__name__)


MODULES_TO_CLEAN = (
    'hw_posbox_upgrade',
    'hw_blackbox_be',
    'hw_drivers',
    'hw_escpos',
    'hw_posbox_homepage',
)


def pre_init_hook(cr):
    remove_deprecated(cr)


def remove_deprecated(cr):
    for module in MODULES_TO_CLEAN:
        cr.execute("UPDATE ir_module_module "
                   "set (state, latest_version) = ('uninstalled', False)"
                   " WHERE name = '{0}'".format(module))
        _logger.info('module to uninstall {0}'.format(module))
