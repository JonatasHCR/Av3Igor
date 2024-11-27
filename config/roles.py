from rolepermissions.roles import AbstractUserRole

class Desenvolvedores(AbstractUserRole):
    available_permissions = {
        'ver_relatorios': True,
        'criar_users': True,
        'acessar_pagina_dev': True,
    }

