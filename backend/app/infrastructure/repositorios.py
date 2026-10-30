"""Acceso a datos. Los servicios solo hablan con estas clases, nunca con SQL directo."""
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from .models import User, Avaluo, Archivo, Documento, Config


class UsuarioRepo:
    def __init__(self, s: Session): self.s = s
    def por_id(self, i): return self.s.get(User, i)
    def por_email(self, email): return self.s.query(User).filter_by(email=email).first()
    def todos(self): return self.s.query(User).order_by(User.id).all()
    def total(self): return self.s.query(User).count()
    def agregar(self, u): self.s.add(u); self.s.commit(); return u
    def guardar(self): self.s.commit()


class AvaluoRepo:
    def __init__(self, s: Session): self.s = s
    def por_id(self, i): return self.s.get(Avaluo, i)
    def buscar(self, q=""):
        qs = self.s.query(Avaluo).order_by(Avaluo.updated_at.desc())
        if q:
            like = f"%{q}%"
            qs = qs.filter(or_(Avaluo.titulo.ilike(like), Avaluo.folio.ilike(like)))
        return qs.all()
    def agregar(self, a): self.s.add(a); self.s.commit(); return a
    def guardar(self): self.s.commit()
    def borrar(self, a): self.s.delete(a); self.s.commit()
    def folio_siguiente(self, anio: int) -> str:
        n = self.s.query(func.count(Avaluo.id)).filter(Avaluo.folio.like(f"AV-{anio}-%")).scalar() + 1
        while self.s.query(Avaluo).filter_by(folio=f"AV-{anio}-{n:04d}").first():
            n += 1
        return f"AV-{anio}-{n:04d}"


class ArchivoRepo:
    def __init__(self, s: Session): self.s = s
    def por_id(self, i): return self.s.get(Archivo, i)
    def de_avaluo(self, aid):
        return self.s.query(Archivo).filter_by(avaluo_id=aid).order_by(Archivo.orden, Archivo.id).all()
    def de_empresa(self):
        return self.s.query(Archivo).filter(Archivo.avaluo_id.is_(None)).all()
    def de_seccion(self, aid, seccion):
        return self.s.query(Archivo).filter_by(avaluo_id=aid, seccion=seccion).all()
    def agregar(self, f): self.s.add(f); self.s.commit(); return f
    def borrar(self, f): self.s.delete(f); self.s.commit()
    def guardar(self): self.s.commit()


class DocumentoRepo:
    def __init__(self, s: Session): self.s = s
    def por_id(self, i): return self.s.get(Documento, i)
    def de_avaluo(self, aid):
        return self.s.query(Documento).filter_by(avaluo_id=aid).order_by(Documento.created_at.desc(), Documento.id.desc()).all()
    def contar(self, aid, formato=None):
        q = self.s.query(func.count(Documento.id)).filter_by(avaluo_id=aid)
        return (q.filter_by(formato=formato) if formato else q).scalar()
    def agregar(self, d): self.s.add(d); self.s.commit(); return d
    def borrar_de_avaluo(self, aid): self.s.query(Documento).filter_by(avaluo_id=aid).delete(); self.s.commit()


class ConfigRepo:
    def __init__(self, s: Session): self.s = s
    def obtener(self, clave):
        c = self.s.get(Config, clave)
        return c.valor if c else None
    def guardar(self, clave, valor):
        c = self.s.get(Config, clave)
        if c: c.valor = valor
        else: self.s.add(Config(clave=clave, valor=valor))
        self.s.commit()
