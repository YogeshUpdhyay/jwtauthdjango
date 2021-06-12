from django.db import models
from passlib.hash import pbkdf2_sha256
from .forms import UpdateUserForm

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=50)
    email = models.EmailField()
    password = models.TextField()
    address = models.TextField()

    def hashpass(self, password):
        print(pbkdf2_sha256.hash(password))
        self.password = pbkdf2_sha256.hash(password)

    def verifypass(self, password):
        return pbkdf2_sha256.verify(password, self.password)

    def payload(self):
        return {
            'id': self.id,
            'username': self.username,
            'address': self.address,
            'email': self.email,
            'form': UpdateUserForm({'username': self.username, 'address': self.address, 'email': self.email})
        }
