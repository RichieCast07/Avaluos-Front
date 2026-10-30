from ..config import get_settings
from ..domain.errores import DatoInvalido, NoAutenticado, NoEncontrado
from ..infrastructure.models import User
from ..infrastructure.repositorios import UsuarioRepo
from . import seguridad


class UsuarioService:
    def __init__(self, session):
        self.repo = UsuarioRepo(session)

    def sembrar_admin(self):
        """Crea el primer administrador con ADMIN_EMAIL / ADMIN_PASSWORD si no hay usuarios."""
        if self.repo.total():
            return
        cfg = get_settings()
        self.repo.agregar(User(email=cfg.admin_email, nombre="Administrador",
                               password_hash=seguridad.hash_password(cfg.admin_password), rol="admin"))

    def autenticar(self, email: str, password: str) -> tuple[str, User]:
        u = self.repo.por_email(email.strip().lower())
        if not u or not u.activo or not seguridad.verificar_password(password, u.password_hash):
            raise NoAutenticado("Correo o contraseña incorrectos")
        return seguridad.crear_token(u.id), u

    def desde_token(self, token: str) -> User:
        u = self.repo.por_id(seguridad.leer_token(token))
        if not u or not u.activo:
            raise NoAutenticado("Usuario inactivo")
        return u

    def listar(self):
        return self.repo.todos()

    def crear(self, email: str, nombre: str, password: str, rol: str) -> User:
        email = email.strip().lower()
        if self.repo.por_email(email):
            raise DatoInvalido("Ese correo ya existe")
        if len(password) < 8:
            raise DatoInvalido("La contraseña debe tener al menos 8 caracteres")
        return self.repo.agregar(User(email=email, nombre=nombre.strip(), password_hash=seguridad.hash_password(password),
                                      rol="admin" if rol == "admin" else "valuador"))

    def cambiar_activo(self, uid: int, activo: bool, quien: User):
        u = self.repo.por_id(uid)
        if not u:
            raise NoEncontrado("Usuario no encontrado")
        if u.id == quien.id:
            raise DatoInvalido("No puedes desactivarte a ti mismo")
        u.activo = activo
        self.repo.guardar()
