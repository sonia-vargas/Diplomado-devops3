# Sesión 2 · Del código verificado a producción (CD)

**Módulo 4 · DevOps y CI/CD** — Diplomado Automatización de Procesos con IA
Indra · UPTC · Tec de Monterrey · ProBoyacá

Ayer el pipeline terminaba en "el código está verificado". Hoy ese código llega a producción, y cada paso del camino queda automatizado y registrado. Se trabaja en el **mismo repositorio del equipo** de la Sesión 1 y, otra vez, todo desde el navegador.

```
CI en verde ──► construir la imagen ──► staging + prueba de humo ──► (alguien aprueba) ──► producción
                 una sola vez            la MISMA imagen              ambiente protegido      la MISMA imagen
```

---

## Antes de empezar: su CI tiene que estar en verde

El pipeline de hoy arranca cuando termina un workflow llamado exactamente **`CI`**. Entren a la pestaña **Actions** de su repositorio y revisen la última ejecución de CI sobre `main`.

- **Está en verde:** sigan al reto 6.
- **No terminaron ayer o está en rojo:** copien el contenido de [`ci-completo.yml`](ci-completo.yml) en su `.github/workflows/ci.yml` y el de [`test_calidad_modelo.py`](test_calidad_modelo.py) en `tests/test_calidad_modelo.py`. Hagan commit y esperen el verde.

Para crear un archivo desde la web: en la página principal del repositorio, **Add file → Create new file**, escriban la ruta completa en el nombre (por ejemplo `.github/workflows/cd.yml`) y peguen el contenido.

---

## Reto 6 · Construir y publicar la imagen (15 min)

Creen `.github/workflows/cd.yml` en su repositorio con el contenido de [`cd.yml`](cd.yml) de esta carpeta, y resuelvan los TODO del reto 6: que el pipeline arranque cuando CI termine sobre `main`, que tenga permiso para publicar paquetes, que solo siga si CI terminó en verde, y que construya y publique la imagen Docker en GitHub Container Registry.

**Criterio de aceptación:**

- Hacen un commit en `main`. Corre CI y, **cuando CI termina en verde, CD arranca solo**.
- En la página principal del repositorio, a la derecha, aparece **Packages** con una imagen cuya etiqueta son los 7 primeros caracteres del commit.
- Comprobación: agregan `import os` sin usar en `app/main.py`. CI se pone rojo y en CD el job *Construir* aparece **omitido**. Lo quitan y todo vuelve a verde.

**Pistas**

- El evento se llama `workflow_run`. Busquen en la documentación cómo filtrarlo por nombre de workflow y por rama.
- El permiso es `packages: write`.
- El registro exige nombres en minúsculas. Por eso el paso que arma el nombre ya viene resuelto.

---

## Reto 7 · Staging y prueba de humo (15 min)

Agreguen el job `staging`: debe arrancar **la imagen que acaban de publicar** (no construir otra), esperar a que `GET /health` responda y hacer una prueba de humo contra la API desplegada.

**Criterio de aceptación:**

- El job *Desplegar en staging* queda en verde y el log muestra la respuesta de la API con la categoría `pago`.
- En la página principal del repositorio aparece la sección **Deployments** con el ambiente `staging`.
- **Rómpanlo a propósito:** en el `Dockerfile` cambien `"--port", "8000"` por `"--port", "8080"`. CI queda en verde, la imagen se construye bien y **staging falla**. Restauren el puerto.

**Pregunta para escribir en este README:** ¿por qué ninguna de las pruebas de CI detectó el cambio de puerto?

**Pistas**

- `docker run -d --name tramites -p 8000:8000 "$IMAGEN"` deja la API corriendo en el runner.
- Un ciclo con `curl -fs http://localhost:8000/health` y `sleep 2` evita probar antes de que la API arranque.
- `jq -r .categoria` saca la categoría de la respuesta JSON.

---

## Reto 8 · Producción con aprobación (15 min)

Aquí se pasa de despliegue continuo a **entrega continua**: la última puerta la abre una persona.

1. **Primero** configuren el ambiente: **Settings → Environments → New environment**, nombre `produccion`. Activen **Required reviewers**, agreguen a alguien del equipo y marquen **Prevent self-review** (quien empuja el cambio no puede aprobarse a sí mismo).
2. **Después** agreguen el job `produccion` al `cd.yml`: depende de `staging`, usa el ambiente `produccion` y le pone la etiqueta `produccion` a la misma imagen, sin reconstruirla.

> Si hacen el paso 2 antes que el 1, GitHub crea el ambiente solo, sin protección, y el despliegue pasa directo.

**Criterio de aceptación:**

- La ejecución se detiene en *Desplegar en producción* con el aviso **Waiting for review**.
- La persona revisora aprueba desde **Review deployments**, dejando un comentario.
- En Packages, la imagen tiene ahora dos etiquetas sobre la misma versión: el commit y `produccion`.

**Pregunta para escribir en este README:** ¿por qué la imagen de producción no se vuelve a construir? ¿Qué riesgo habría si se construyera de nuevo?

**Pista:** `docker buildx imagetools create -t "$IMAGEN:produccion" "$IMAGEN:$VERSION"` copia una etiqueta a otra dentro del registro, sin descargar ni construir nada.

---

## Reto 9 · Rollback (10 min)

Hagan un cambio pequeño en `main` (una línea en este README basta) y llévenlo hasta producción. Ahora imaginen que esa versión salió mal: hay que volver a la anterior **en minutos, sin tocar el código**.

Creen `.github/workflows/rollback.yml` con el contenido de [`rollback.yml`](rollback.yml) y resuelvan sus TODO.

**Criterio de aceptación:**

- Desde **Actions → Rollback → Run workflow** escriben la versión anterior (los 7 caracteres).
- Pasa por la misma aprobación que un despliegue.
- En Packages, la etiqueta `produccion` vuelve a estar sobre la versión anterior.

**Pista:** las entradas de un `workflow_dispatch` se leen con `${{ inputs.version }}`. Pásenla al script por `env:`; pegarla directo dentro de `run:` permite que alguien inyecte comandos.

---

## Entregable del equipo (en el chat de la sesión)

1. El enlace del repositorio.
2. Una captura de la ejecución esperando aprobación y otra del paquete con sus etiquetas.
3. Las dos respuestas escritas en este README (reto 7 y reto 8).

## Trabajo autónomo

- Agregar al job de producción un paso que publique un *Release* de GitHub con la versión desplegada.
- Cambiar la prueba de humo para que verifique las cuatro categorías, no solo `pago`.
- Escribir en una página qué cambiaría en `cd.yml` para desplegar en AWS de verdad (pista: ECR, ECS y credenciales con OIDC en vez de llaves guardadas).
