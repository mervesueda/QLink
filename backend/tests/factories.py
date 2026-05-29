"""
factories.py – Factory Boy + Faker ile test verisi üretimi.

Factory'ler ORM modellerini baz alır ancak DB'ye kaydetmez (build stratejisi).
Testlerde manuel olarak db.add() ve db.commit() yapılır.
Bu yaklaşım test izolasyonunu korur.
"""

import factory
from faker import Faker

from app.core.security import hash_password
from app.db.models import QRCode, User

fake = Faker("tr_TR")  # Türkçe locale: gerçekçi test verisi


class UserFactory(factory.Factory):
    """
    Sahte User nesnesi üretir.
    Gerçek bcrypt hash kullanır; bu davranış test edilebilir.
    """

    class Meta:
        model = User

    email = factory.LazyFunction(lambda: fake.email())
    # Tüm test kullanıcıları aynı şifreyi kullanır (hash farklı olur)
    password_hash = factory.LazyFunction(lambda: hash_password("Test1234!"))


class QRCodeFactory(factory.Factory):
    """
    Sahte QRCode nesnesi üretir.
    user_id dışarıdan verilmeli: QRCodeFactory(user_id=some_user.id)
    """

    class Meta:
        model = QRCode

    content = factory.LazyFunction(lambda: fake.url())
    qr_type = "url"
    file_url = factory.LazyFunction(
        lambda: f"http://localhost:4566/qlink-qrcodes/qr_{fake.uuid4()}.png"
    )
    file_format = "png"
