import pytest
from django.contrib.auth.models import User
from gitload.models import Strategy,Repository
from sandbox.models import Sandbox




@pytest.mark.django_db
def test_admin_user():
    me = User.objects.get(username='admin')
    assert me.is_superuser
    sb= Sandbox.objects.get(name="php-sandbox")
    assert sb
    re= Repository.objects.get(name="plbank")
    assert re.name == "plbank"
    stra= Strategy.objects.get(name="python")
    assert stra.json



    
