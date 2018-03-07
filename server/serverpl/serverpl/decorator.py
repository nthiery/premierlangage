#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Python 3
#
#  Author: Coumes Quentin     Mail: qcoumes@etud.u-pem.fr
#  Created: 2017-09-12
#  Last Modified: 2017-09-12

from django.core.exceptions import PermissionDenied


def can_gitload(function):
    def wrap(request, *args, **kwargs):
        if request.user.pluser.can_load():
            return function(request, *args, **kwargs)
        raise PermissionDenied("Vous devez être professeur ou administrateur pour accéder à Gitload.")
        
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
