# Modelo de datos de Instagram

Seis modelos SQLAlchemy, definidos en `src/models.py`:

| Modelo | Datos y relaciones |
| --- | --- |
| User | Usuario, correo, hash de contraseña, nombre, biografía, avatar y fecha. |
| Post | Autor, descripción, ubicación y fecha de publicación. |
| Media | Foto o vídeo, URL, texto alternativo y posición dentro de una publicación. |
| Comment | Autor, publicación, contenido y fecha. |
| Like | Usuario y publicación que le gusta. Una sola vez por pareja. |
| Follow | Usuario que sigue y usuario seguido. Sin duplicados ni seguimiento propio. |

Un usuario tiene muchas publicaciones y comentarios. Una publicación contiene
varios archivos multimedia, comentarios y me gusta. Like representa la relación
muchos a muchos entre usuarios y publicaciones. Follow representa la relación
muchos a muchos de usuarios consigo mismos; se declaran explícitamente las dos
claves foráneas para distinguir quién sigue a quién.

Las claves foráneas son obligatorias. Los borrados en cascada evitan dejar
comentarios, archivos o relaciones sin su usuario o publicación. Email y username
son únicos. El campo password debe recibir un hash, nunca texto plano; los métodos
serialize no lo exponen. Este ejercicio define datos, no implementa autenticación.

## Generar el diagrama

```bash
pipenv install
pipenv run diagram
```

Equivale a `pipenv run python src/models.py`. Si ya estás dentro de `pipenv shell`,
puedes ejecutar directamente `python src/models.py` como pide el enunciado.
Se crea `diagram.png` en la raíz desde los metadatos de SQLAlchemy. No requiere
PostgreSQL, migraciones, borrar datos ni arrancar Flask. Codespaces ya incluye
Graphviz en el Dockerfile recibido; eralchemy2 ya está en el Pipfile.

Abre diagram.png en el explorador de Codespaces para comprobar el resultado.
La regla que ignoraba diagram.png se retira para poder entregarlo en GitHub.
No se modifica Pipfile.lock porque no se añaden dependencias.

## Entrega

Después de generar y revisar el diagrama:

```bash
git add src/models.py Pipfile .gitignore diagram.png README-INSTAGRAM.md
git diff --cached --check
git commit -m "Crear modelo de datos de Instagram y diagrama ER"
git push
```

La migración inicial de la plantilla no se actualiza: este ejercicio entrega los
modelos y su diagrama. Para ejecutar una API con este esquema en una base real se
necesitaría generar y revisar una migración aparte.
