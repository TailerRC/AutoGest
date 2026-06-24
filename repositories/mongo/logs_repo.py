"""
repositories/mongo/logs_repo.py
=================================
Repositorio para log_actividad y alertas_sistema (MongoDB).
"""
from typing import List, Optional, Dict
from database import MongoDB


class LogsRepository:
    """
    Repositorio de logs de actividad y alertas del sistema.

    TODO (MongoDB real):
        self._logs    = db["log_actividad"]
        self._alertas = db["alertas_sistema"]
    """

    def __init__(self, db: MongoDB):
        self._db = db

    # ── Logs de actividad ─────────────────────────────────────────────

    def get_recent(self, limit: int = 50) -> List[Dict]:
        """
        TODO: return list(self._logs.find().sort("fecha_hora", -1).limit(limit))
        """
        return self._db.get_logs(limit=limit)

    def registrar(self, id_empleado: int, accion: str,
                  modulo: str, resultado: str = "exitoso") -> None:
        """
        TODO: self._logs.insert_one({
                  "id_empleado": id_empleado, "accion": accion,
                  "modulo": modulo, "resultado": resultado,
                  "fecha_hora": datetime.utcnow()
              })
        """
        self._db.registrar_log(id_empleado, accion, modulo, resultado)

    # ── Alertas del sistema ───────────────────────────────────────────

    def get_alertas_activas(self, destinatario: Optional[str] = None) -> List[Dict]:
        """
        TODO: query = {"estado": "activa"}
              if destinatario: query["destinatario"] = {"$in": [destinatario, "admin"]}
              return list(self._alertas.find(query))
        """
        return self._db.get_alertas_activas(destinatario=destinatario)
