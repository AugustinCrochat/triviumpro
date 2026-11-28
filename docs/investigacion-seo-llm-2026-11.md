# pro.trivium.ar: cómo rankear en buscadores y en LLMs (28/11/2026)

## En resumen
1. Hay un **error de precios publicado** que conviene corregir antes que cualquier otra cosa.
2. Lo técnico básico está bien. El margen está en **contenido propio de experiencia**, **datos de producto completos y correctos** y **presencia fuera del sitio** (Google Business Profile, Merchant Center, YouTube, menciones).
3. No hay un "SEO para IA" aparte. Google dice que sus funciones de IA usan el mismo índice y los mismos sistemas de calidad que Search.

## 1. Urgente: lo que encontró la auditoría

| Gravedad | Problema | Evidencia | Arreglo |
|---|---|---|---|
| Crítica | Las fichas prerenderizadas y su schema `Offer` muestran precios más bajos que el feed de Google y que la grilla hidratada. Ej.: PL 4.0 2A, $4.240.438 en la ficha y $4.489.063 en el feed (5,5 % menos) | `dolarapi.com` responde 403 al User-Agent por defecto de Python y `scripts/generate_pretty_urls.py` cae en silencio al dólar fijo 1535 (hoy 1625). De 16 fichas comparadas, 15 diferían (la primera versión decía "17 y 14": estaba mal contado). **Corregido el 28/11** | Enviar un User-Agent (probado: responde 1625) y cortar con error si falla, sin dólar de reserva. Revisar también guías y categorías |
| Alta | `llms.txt` afirma que se puede comprar con Mercado Pago, y la tienda está pausada | `scripts/generate_llms_txt.py:94` | **Corregido el 28/11**, junto con el enlace a `/lista-precios/`, que redirige al catálogo. Las páginas legales siguen mencionando Mercado Pago |
| Alta | SPOA10TRIO muestra "elevación 121 mm", que es la altura mínima del adaptador | `data/catalog.json`, SKU 1010017 | Cargar la elevación real. Su botón de PDF además apunta a la ficha del SPOA10: confirmar si corresponde |
| A confirmar | SPO55 figura con elevación 3486 mm, muy distinta de sus pares (1,8 a 2,0 m) | catálogo, SKU P-5083 | Verificar contra el fabricante |
| Alta | 89 fichas declaran `Product` sin `offers`. Sin `offers`, `review` ni `aggregateRating` no son elegibles para resultados enriquecidos de producto | auditoría de 287 páginas | No inventar precio ni reseñas. Publicar precio donde se pueda. Donde no, esperar errores en Search Console o quitar ese bloque |
| Media | 58 de 107 equipos tienen menos de 400 caracteres de descripción | catálogo | Completar primero los que más consultas traen |
| Media | 69 de 114 notas están fechadas en 10/2026. Hay 22 pares con más de 20 % de frases compartidas (máximo 38 %), sobre todo "¿Es rentable…?" y "Cómo montar…" | comparación de texto | Revisar, fusionar o reforzar con experiencia propia. Ver §3 |
| Media | Las ofertas con precio no declaran `shippingDetails` (18 fichas) | auditoría | Agregarlo solo cuando haya reglas de envío reales. Hoy se cotiza |
| Baja | Casi ninguna imagen declara `width` y `height` (riesgo de saltos de diseño) y hay fotos de producto con `alt` vacío | auditoría | Se resuelve con las plantillas nuevas |
| A revisar | CCBot (Common Crawl) recibe 403; GPTBot, OAI-SearchBot, ClaudeBot, Claude-SearchBot, PerplexityBot, Bingbot y Googlebot reciben 200 | prueba con User-Agent simulado, no desde sus IP reales | Mirar AI Crawl Control en Cloudflare |

Lo que está bien: títulos y descripciones sin duplicados, `robots.txt` abierto a los bots de IA, sitemap con 397 URLs y tiempo de respuesta de 0,1 a 1 s en cinco pruebas. No medí Core Web Vitals de usuarios reales; eso se ve en Search Console.

## 2. Qué dice la evidencia

### Fuentes primarias (leídas)
- **Google, guía de optimización para IA** ([enlace](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)): recomienda contenido no genérico y de primera mano, buenas imágenes y video, HTML semántico, rastreo limpio, Merchant Center y Business Profile. Dice que no hacen falta `llms.txt`, trocear el texto, reescribir "para IA", buscar menciones artificiales ni un schema especial.
- **Resultados enriquecidos de FAQ**: Google dejó de mostrarlos el 7/5/2026 ([registro de cambios](https://developers.google.com/search/docs/appearance/structured-data/faqpage)). Las preguntas visibles siguen sirviendo al lector; el marcado ya no da ventaja visual.
- **OpenAI** ([bots](https://developers.openai.com/api/docs/bots)): OAI-SearchBot decide la aparición en la búsqueda de ChatGPT y GPTBot el entrenamiento.
- **Spam** ([políticas](https://developers.google.com/search/docs/essentials/spam-policies)): "contenido a escala" es producir muchas páginas principalmente para posicionar, sin importar cómo se hagan. También advierte sobre páginas casi iguales por consulta o por ciudad.
- **Merchant listing** ([documentación](https://developers.google.com/search/docs/appearance/structured-data/merchant-listing)): exige nombre, imagen y oferta con precio y moneda. Recomienda envío, devoluciones, certificaciones y varias imágenes. Parte de esto lo leí resumido.
- **Sitios aptos para agentes** ([web.dev](https://web.dev/articles/ai-agent-site-ux)): botones y enlaces reales, etiquetas en los formularios, diseño estable y sin capas que tapen controles.

### Un estudio académico (preprint, sin revisión por pares)
[Chen y Koudas, 10/2026](https://arxiv.org/abs/2610.15033), con 158.099 respuestas, en inglés y sobre el mercado de EE. UU. Son asociaciones, no causas.
- Dentro de un mismo sitio, lo que resistió las pruebas fue que **el título y algún párrafo respondan lo que se pregunta** (alrededor de +14 % y +15 % de citas por desvío estándar).
- FAQ, schema, cuadros de resumen, longitud, listas, tablas y velocidad **no mostraron efecto propio** en las citas.
- **Que el buscador del motor encuentre la página** pesa mucho más (32 % de la variación) que los rasgos de la página (2,8 %). En la práctica: primero posicionar.

Las tablas, el comparador y el medidor del rediseño se justifican por el comprador, no como truco para que un LLM cite el sitio.

### Señales de proveedores de SEO (indicativas, sin verificar en origen)
- En un análisis de Ahrefs de 75.000 marcas, las menciones en YouTube (0,74) y en la web (0,66) se correlacionan con la visibilidad en IA bastante más que los enlaces (0,22) ([nota](https://thenextweb.com/news/ahrefs-youtube-mentions-ai-visibility-brand-search)). Correlación no es causa.
- Varios estudios de registros de servidor muestran que los bots de IA casi no piden `llms.txt` ([ejemplo](https://www.ezy.ai/research/do-ai-bots-read-llms-txt)). Se puede mantener porque es barato y se genera solo, pero tiene que decir la verdad.
- El catálogo orgánico de compras de ChatGPT apuntaría hoy solo a EE. UU. ([guía](https://feedworks.io/guides/ai-shopping-feeds/chatgpt)). No lo priorizaría.
- Bing Webmaster Tools tiene un informe (en prueba) de citas en Copilot ([guía](https://viewership.ai/guides/bing-webmaster-tools-ai-performance-report)). El sitio ya tiene IndexNow.
- Para PDF, la canónica se declara con la cabecera HTTP `Link` ([guía](https://patrickstox.com/technical-seo/how-search-works/indexing/canonicalization/canonical-tag/)). Es una opción por si una ficha PDF compite con su página; antes hay que ver en Search Console si pasa.

## 3. Plan, por impacto

### A. Datos correctos (esta semana)
Precios y `llms.txt`: corregidos el 28/11, con un control (`scripts/check_precios.py`) que frena la tarea diaria si ficha y feed difieren. Pendiente: SPOA10TRIO. El mismo día, por decisión del negocio, la cotización pasó de oficial venta a **blue compra** (los montos y el "hoy 1625" de la tabla son anteriores).

### B. Experiencia demostrable (lo que más diferencia)
- Cada categoría importante y cada ficha clave con **una nota firmada por un técnico**: qué se mide, qué falla, cuándo no conviene ese modelo.
- **Casos de instalación** con fotos propias: ciudad, equipo, problema y solución. Solo reales y con permiso del cliente.
- Autor y revisor con nombre y rol en guías y notas.
- Frenar la publicación en tanda. Revisar las 114 notas con datos de Search Console: conservar, mejorar, fusionar con 301 o quitar. No borrar por intuición.
- Completar requisitos por modelo: piso, anclaje, techo, tensión, aire y espacio.

### C. Páginas que respondan la compra
- Título y primer párrafo que contesten la consulta real ("¿qué elevador necesito para pickups?").
- Medidas y especificaciones en texto HTML con las mismas unidades, no solo en PDF o imagen.
- Comparativas por categoría.
- No crear páginas por ciudad con el mismo texto.

### D. Fuera del sitio (tareas de Etienne; probablemente lo que más mueve las recomendaciones)
1. Google Business Profile: URL, categorías, fotos reales y pedido de reseñas a clientes, sin incentivos. Según mis notas, seguía sin actualizar el 12/9.
2. Merchant Center: alta y verificación, **después** de corregir precios ([guía interna](merchant-center.md)).
3. Search Console y Bing Webmaster Tools: informes de rendimiento, incluidos los de IA. Exportar páginas y consultas para explicar la caída respecto de trivium.ar.
4. YouTube: videos cortos de instalaciones y uso, con título que nombre equipo y marca, subtítulos y enlace a la ficha.
5. Que Rotary, Hofmann, Josam y las cámaras del sector nombren y enlacen a Trivium Pro como distribuidor.

### E. Técnica, junto con el rediseño
HTML prerenderizado como fuente principal (sin que el JavaScript cambie precios o datos), imágenes con dimensiones y `srcset`, fuente web con pocos pesos, `BreadcrumbList`, `Product`, `Organization` y `VideoObject`. URLs sin cambios.

### Qué no hacer
Notas en masa, páginas por ciudad, reseñas o autores inventados, texto oculto para IA, menciones compradas, o presentar la instalación como incluida.

### Cómo medir
Línea de base de hoy en Search Console: clics e impresiones, consultas sin marca y de marca, páginas con error de producto, informe de IA. En Bing, citas. Cada mes, las mismas 20 preguntas de compra en ChatGPT, Gemini, Perplexity y Claude, anotando si aparece Trivium Pro y qué cita. Sumar las consultas por WhatsApp según la página de origen.

No se puede prometer una posición ni una cita.

## 4. Rediseño (propuesta, pendiente de aprobación)
Bocetos en `scratch/rediseno-2027/` (no se publican): portada, ficha SPOA10, categoría, biblioteca técnica, nota y ficha PDF A4.

- **Idea:** la cota de plano, la chapa de identificación y las fotos reales del equipo técnico.
- **Color:** grafito `#12171b`, hormigón `#eceeed`, blanco y el rojo de marca reservado para acciones y cotas.
- **Tipografía:** Archivo en tres anchos (expandida en títulos, normal en texto, condensada en datos). Es la familia actual del sitio.
- **Nuevo:** "¿Entra en tu taller?", tabla comparativa con escala de capacidad, resumen técnico tipo chapa y ficha PDF con rótulo.
- **Se conserva:** las portadas de blog del 26/11, el logo, los sellos de origen y las URLs.

### Antes de publicar
- Nombre y rol de quienes firman, y las notas del técnico.
- Confirmar los datos que reuso del sitio: 15+ años, 1 año de garantía, posventa en 48 a 72 h, logos de clientes y sus permisos.
- Confirmar el pie de la foto y que las personas autorizan aparecer en la portada.
- El medidor compara solo techo y ancho con los datos de la ficha del SPOA10: que un técnico valide el criterio y el margen. Para otros modelos faltan datos.
- Fotos nuevas de instalaciones: hoy hay muy pocas.
- En los bocetos, buscador, filtros del blog, selector de vista y varios enlaces son decorativos. Los precios salen del feed del repositorio y son una foto de ese día.
- La ficha PDF nueva no repite la franja de financiación ni "Repuestos originales" y "Servicio técnico oficial" de la actual: decidir si vuelven.

### Orden de implementación
1. Sistema común (CSS, cabecera y pie) y ficha de producto.
2. Categorías y portada.
3. Biblioteca, notas y guías (antes, arreglar `generate_blog_pages.py`, que figura como roto en mis notas, y revisar `blog_layout.py`).
4. Marcas, origen, servicios, nosotros, contacto, 404 y legales.
5. Generador de fichas PDF y regeneración, con sus scripts de enlaces.
