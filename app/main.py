from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v3 import api_v3
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="Upload Dropbox API",
    version="1.0.0",
    description="API com autenticação JWT, integração com Dropbox e banco de dados PostgreSQL."
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="GMF API",
        version="1.0.3",
        description="Autenticação via JWT",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Troque pelo domínio frontend em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas da API
app.include_router(api_v3)


"""
# Rota raiz para servir um index.html (opcional)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_root():
    return FileResponse("static/index.html")  # Coloque o index.html dentro da pasta /static

@app.get("/dropbox")
def read_root():
    return FileResponse("static/dropbox.html")  # Coloque o dropbox.html dentro da pasta /static


@app.get("/register")
def read_root():
    return FileResponse("static/register.html")  # Coloque o register.html dentro da pasta /static


@app.get("/change-password")
def read_root():
    return FileResponse("static/change-password.html")  # Coloque o change-password.html dentro da pasta /static

"""

# Execução local
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
