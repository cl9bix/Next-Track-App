from app.models.session import get_async_session, Base, engine
from app.core.auth import hash_password
from app.models.models import AdminUser
from app.models.models import Organisator

Base.metadata.create_all(bind=engine)
db = get_async_session()
# org = db.query(Organisator).first()
# if not org:
#     org = Organisator(name="My Org")
#     db.add(org)
#     db.commit()
#     db.refresh(org)
username = "cl9bix"
password = "cl9bix"  # заміни!
adm = AdminUser(username=username, password_hash=hash_password(password))
db.add(adm)
db.commit()
print("OK. Admin:", username)
