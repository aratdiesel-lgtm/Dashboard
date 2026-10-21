# Folio · Dashboard de campañas

Dashboard responsive de afiliación para una creadora de contenido. HTML semántico y Tailwind CSS v4 compilado localmente, sin CDN, JavaScript de aplicación ni frameworks. Todos los resultados son **datos de demostración**, no información verificada.

## Ejecutar

Requisitos: Node.js 20 o superior y npm. Python 3 es necesario solo para las pruebas y el servidor opcional.

```bash
npm ci
npm run build
```

Abre [index.html](index.html) directamente en el navegador. El CSS compilado está incluido. Para visualizarlo mediante HTTP, opcionalmente:

```bash
npm start
```

Visita `http://localhost:3000`. Si el puerto está ocupado, usa `python3 -m http.server 3001` y abre `http://localhost:3001`. Para recompilar al editar: `npm run watch` en otra terminal.

## Estructura

```text
index.html                 Dashboard completo
src/input.css              Importación v4 y tokens de diseño (@theme)
dist/styles.css            CSS generado, listo para visualizar
data/informe-octubre.csv   Exportación de los datos demo
package.json               CLI de Tailwind y comandos
package-lock.json          Versiones reproducibles
tests/test_dashboard.py    Pruebas con la biblioteca estándar de Python
```

## Contenido

- **KPIs:** comisiones, ventas, alcance, impresiones, conversión, engagement y ROI; objetivo de comisiones y variaciones frente al periodo anterior.
- **Drivers:** evolución diaria, funnel, comparación de plataformas, ranking de productos, interacciones y actividad de publicación.
- **Operaciones:** tablas de productos, plataformas y campañas, rankings, tres alertas y oportunidades de mejora.

Navegación por anclas, paneles nativos desplegables y descarga CSV funcionan sin JavaScript. El periodo y la cuenta son informativos y fijos; no se simulan conexiones, sincronización ni filtros en vivo. Las tablas conservan encabezados y desplazamiento horizontal local en móvil, sin desbordar la página. Breakpoints utilizados: `sm:`, `md:`, `lg:` y `xl:`.

## Datos y cálculos

Periodo: 1–15 octubre de 2026. Moneda: EUR. 842 ventas, 9.666 € de comisiones y 2.800 € de costes. Los datos se presentan estáticamente y los cálculos se verifican con las pruebas.

| Producto | Precio | Comisión (15 %) | Ventas | Comisiones |
| --- | ---: | ---: | ---: | ---: |
| A | 50 € | 7,50 € | 420 | 3.150 € |
| B | 120 € | 18,00 € | 242 | 4.356 € |
| C | 80 € | 12,00 € | 180 | 2.160 € |

- Comisión = precio × 15 %; total = comisión por venta × ventas.
- Conversión = conversiones / alcance × 100.
- Engagement = interacciones / alcance × 100.
- ROI = (comisiones atribuidas − costes) / costes × 100.
- Si falta un dato o el denominador es cero, se muestra «—». No se sustituye un dato ausente por cero. El ROI global usa totales ponderados, no la media de los ROI.
- El alcance es agregado, sin deduplicación entre canales. El funnel es ilustrativo, no una secuencia de personas únicas; sus anchos no son proporcionales.
- Cada venta se atribuye exclusivamente a una campaña/plataforma. Reparto A/B/C: Instagram 220/120/70; TikTok 140/90/70; YouTube 60/32/40.
- Los costes son los mismos desglosados por diferentes dimensiones. No sumar productos, plataformas y campañas entre sí. El CSV lo indica en su fila total.
- Comparativa anterior: 8.150 € de comisiones, 748 ventas, 1.144.000 de alcance, 2.230.000 impresiones, 82.368 interacciones, 2.680 € de costes y 24 publicaciones.
- Variaciones relativas para importes y volúmenes; puntos porcentuales para tasas. Redondeo solo en presentación.

Las fotografías ilustrativas proceden de Unsplash; la tipografía Manrope se sirve desde Google Fonts. Ambas necesitan conexión, pero no son necesarias para consultar los datos: existen textos alternativos y una tipografía de respaldo. Los iconos SVG están integrados y no necesitan servicios externos. No hay analítica, cookies ni llamadas a plataformas sociales.

## Verificación

```bash
npm run build
npm test
npm audit
```

Las pruebas comprueban los cálculos, la coherencia entre dimensiones, los totales diarios, CSV, denominadores cero, datos ausentes, enlaces internos, semántica, breakpoints y ausencia de scripts o CDN de Tailwind.
