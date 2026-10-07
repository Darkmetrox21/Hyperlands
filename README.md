# Hyperlands invitaciones v2

Mantiene las tres escenas de la invitación y añade aceptar/declinar, confirmación antes de declinar, cambio de respuesta, panel de respuestas y exportación CSV. Incluye el aviso: Aún no hay fecha confirmada, pero ya falta poco.

## Actualizar sin perder tus enlaces
1. Detén la app con Ctrl+C.
2. Haz una copia de tu carpeta actual.
3. Reemplaza app.py y tokens.py; añade storage.py. Puedes copiar el resto del paquete, pero CONSERVA tus assets/logo.png, isla.jpg y tema.ogg.
4. CONSERVA .streamlit/secrets.toml y la misma INVITE_SIGNING_KEY. No reemplaces las claves reales por el ejemplo. Cambiar la clave invalida los enlaces anteriores.
5. Conserva data/respuestas.sqlite3 si ya existe. No subas esta base a GitHub.
6. Ejecuta py -m pip install -r requirements.txt y py -m streamlit run app.py.
7. Añade ?admin=1 a la dirección de la app. Abre la pestaña Respuestas.

## Respuestas
Se guardan en data/respuestas.sqlite3 en el equipo que ejecuta la app, compartidas entre sesiones y conservadas tras reiniciar mientras mantengas el archivo. Cada enlace tiene su propia respuesta, no cada nombre. Dos invitaciones al mismo nombre son registros distintos. Los enlaces anteriores se registran al abrirlos; no aparecen como pendientes antes de su primera apertura. Los nuevos se registran al crearlos.

En demostración, aceptar/declinar solo cambia el estado de la sesión: no genera registros reales. El administrador puede exportar las respuestas a CSV. Fechas del panel en UTC. No se envían notificaciones, no se añade nadie a la whitelist y declinar no libera automáticamente un cupo.

## Seguridad y límites
Los enlaces se firman, no se cifran. El contenido puede leerse desde el token. Quien tenga un enlace puede responder o cambiar la respuesta: no hay verificación de identidad. No publiques enlaces personales en el stream si no quieres que se copien. La contraseña protege el panel, pero la demora ante errores es solo por sesión. No hay revocación individual.

## Streamlit Cloud
SQLite local sirve para probar y para un equipo con disco persistente. Community Cloud no garantiza conservar archivos locales. NO uses esta versión con SQLite local como único registro de respuestas importantes en Cloud. Antes de enviar invitaciones desde Cloud, configura una base externa en una versión adaptada o un alojamiento con disco persistente. RESPONSES_DB_PATH permite elegir una ruta persistente, no convierte el disco de Cloud en persistente.

## Logo y música
Se usan assets/logo.png y assets/tema.ogg si existen. Si no hay logo, se muestra HYPERLANDS en texto. Conserva los assets de tu versión anterior. No se crea un logo nuevo ni se incluye una canción nueva.

## Pruebas
Sintaxis Python, firma de tokens, almacenamiento de respuestas y flujo de Streamlit comprobados. No desplegado ni revisado en navegador real. Haz una prueba de aceptar, declinar y cambiar respuesta con un enlace de prueba antes de enviarlos.


## Novedades v3
- PNG horizontal de 1600 x 1000 con el mismo archivo assets/isla.jpg, titulo Hyperlands Reborn y nombre grande.
- Texto original construido con combinaciones de frases relacionadas con la isla, el hogar y la historia. La seleccion depende del nombre y es estable. Las frases pueden repetirse entre personas: no es un generador de IA ni promete prosa irrepetible. El nombre hace personal la tarjeta.
- Apertura CSS: solapa que gira, carta que emerge, halo y particulas. Se activa al pulsar Romper el sello. La revelacion final sigue siendo un segundo boton.
- Sin sonido automatico ni flashes rapidos. Respeta la preferencia del navegador de movimiento reducido.
- Conserva aceptar/declinar, panel y SQLite. No hay cambios de esquema de base de datos.

## Actualizar desde v2
Deten con Ctrl+C. Copia app.py, card.py, tokens.py, storage.py, requirements.txt y assets/fonts. Conserva tu logo, isla.jpg, tema.ogg, .streamlit/secrets.toml y data/respuestas.sqlite3. Instala requirements y ejecuta py -m streamlit run app.py.

## Validacion v3
AppTest: tres escenas, generacion de PNG, aceptar y declinar guardados. PNG probado con nombres largos y acentos. Ejemplo de DevilJho inspeccionado visualmente. Animacion CSS no revisada en navegador real.
