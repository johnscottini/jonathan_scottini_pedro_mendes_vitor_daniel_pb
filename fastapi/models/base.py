"""Base dos schemas de ENTRADA da API.

`extra="forbid"` faz o Pydantic devolver 422 quando o cliente manda um campo
que não existe no schema, em vez de ignorá-lo em silêncio. Isso fecha a porta
para mass assignment (OWASP A08 — Software and Data Integrity Failures) e
deixa explícito no contrato da API o que é aceito.

Todo modelo que representa um corpo de requisição deve herdar de `StrictModel`.
"""

from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
