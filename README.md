# Gráficas de clanes: Org + Beamer + Manim (Ubuntu)

## Instalación en Ubuntu 24.04 (solo una vez)

```bash
sudo apt update
sudo apt install -y \
    python3-venv python3-pip build-essential pkg-config \
    libcairo2-dev libpango1.0-dev ffmpeg \
    texlive-latex-recommended texlive-latex-extra texlive-pictures \
    texlive-lang-spanish pdfpc \
    gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad gstreamer1.0-libav
```

Si ya tienes una instalación propia de TeX Live, no necesitas sustituirla. Los paquetes GStreamer aparecen por el problema de códecs observado al probar `pdfpc`. Se utiliza **Manim Community**, no `manimgl` (la variante de 3Blue1Brown).

## Crear el entorno de Manim con `uv`

Instala `uv` siguiendo las [instrucciones oficiales](https://docs.astral.sh/uv/getting-started/installation/). En Ubuntu, también puedes usar el instalador independiente:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Abre una terminal nueva, cambia al directorio del proyecto y crea un entorno local con Python 3.12:

```bash
cd /ruta/al/directorio/2026-uaeh-k-null-s2
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
source .venv/bin/activate
manim --version
```

`uv` instala Python 3.12 si hace falta. El entorno queda en `.venv/`; para volver a usarlo en una terminal nueva, activa el entorno con `source .venv/bin/activate` desde la raíz del proyecto. Las dependencias del sistema indicadas arriba (en particular Cairo, Pango y FFmpeg) siguen siendo necesarias.

## Renderizar los videos con Manim (17 originales y 6 nuevos)

```bash
source .venv/bin/activate
bash scripts/render_manim.sh
```

Por omisión usa `-ql` (calidad baja, para pruebas). Para calidad alta:

```bash
MANIM_QUALITY=-qh bash scripts/render_manim.sh
```

El script ejecuta Manim escena por escena, copia cada MP4 a `videos/` y extrae mediante `ffmpeg` su primer fotograma a `posters/`. **Sobrescribe** las previsualizaciones MP4 incluidas. Los archivos `source/storyboards.py` y `source/manim_scenes.py` contienen las geometrías y las animaciones editables. Los videos usan fondo blanco, vértices y aristas algo más grandes para integrarse mejor con las diapositivas. En la escena «Gráficas» aparece un grafo rueda planar de diez vértices y 18 aristas; después se ilustran un lazo (arista de un vértice a sí mismo) y una arista paralela con curvas, marcados como no permitidos. Las escenas generales muestran etapas sucesivas mediante fundidos; se pueden personalizar las transiciones en `_Storyboard.construct()`.

En «Clanes» y «Gráfica de clanes», los dos clanes maximales se enfatizan por separado, con una pausa en el grafo normal entre ellos, y luego juntos. Los vértices y la arista compartidos se muestran en teal y rojo. En «Gráfica de clanes» los grafos están etiquetados \(G\) y \(K(G)\) en Latin Modern Sans, a juego con el texto de la presentación; las etiquetas grandes quedan alineadas bajo los grafos. \(K(G)\) aparece a la derecha, con su arista vertical y el vértice rojo debajo del teal.

En «Gráficas iteradas de clanes», \(G\), \(K(G)\) y \(K^2(G)\) aparecen sucesivamente con sus etiquetas; la arista de \(K(G)\) es vertical.

En las tres escenas del prisma se destacan sucesivamente sus cinco clanes, los seis clanes de \(K_{2,3}\) y la secuencia completa \(T_3\to K_{2,3}\to T_3\). Cada clan se destaca durante medio segundo; en el prisma se muestra primero el triángulo interior y luego el exterior. Las copias del prisma usan una representación planar con triángulos anidados, sin cruces ni solapamientos de aristas. Las escenas de Manim correspondientes son `PrismaClanes`, `PrismaK23` y `Prisma`.

En `SuspensionC5` se resaltan por separado los diez clanes triangulares de la suspensión durante medio segundo cada uno, antes de mostrar su gráfica de clanes a la derecha. La suspensión mantiene sus polos alineados y gira el pentágono para distinguir sus triángulos; las capas pentagonales de la gráfica de clanes están alineadas y giradas para separar las aristas de los vértices no incidentes.

En «Comportamiento», las definiciones se revelan una a una al avanzar y después aparece la animación; esta etiqueta como «Nula» la sucesión del triángulo y como «Divergente» la de los octaedros.

En «Iteradas del octaedro», la animación aparece al avanzar después del texto y muestra sucesivamente \(G=O_3\), \(K(G)\) y \(K^2(G)\).

En «Realización de \(\Delta_1\)», la escena `RealizacionSimplicial` construye la realización geométrica mostrando sucesivamente los cuatro vértices etiquetados, sus cuatro aristas y el triángulo relleno.

En «Topología en gráficas», `TopologiaGraficas` compara la realización contraíble anterior con la superficie triangulada de la suspensión de \(C_5\), homotópica a \(S^2\).

En «Gráficas Helly», «Gráficas desmantelables» y «Teoremas sobre vértices dominados», la animación aparece al avanzar después del último punto del texto.

Ejemplo de Manim para una sola escena:

```bash
manim -pql source/manim_scenes.py Prisma
```

Esto genera un archivo dentro de `media/` (no necesariamente el usado por Beamer). Para instalarlo en la presentación se recomienda ejecutar el script completo, que también coloca el póster correspondiente.

## Compilar con `pdflatex`

```bash
bash scripts/build_pdf.sh
pdfpc -S presentacion.pdf
```

Equivalente manual:

```bash
pdflatex -interaction=nonstopmode -halt-on-error presentacion.tex
pdflatex -interaction=nonstopmode -halt-on-error presentacion.tex
pdfpc -S presentacion.pdf
```

Asegúrate de ejecutar estos comandos **desde la raíz** del proyecto. Para probar el enlace a un video, haz clic sobre la imagen de su diapositiva. Si no reproduce, comprueba primero que pdfpc tenga disponibles los códecs GStreamer para H.264/MP4.

## Editar y exportar el documento Org

- `presentacion.org`: versión Org/Beamer editable. Los encabezados `**` representan diapositivas y las columnas se construyen con subencabezados `***` y la propiedad `BEAMER_COL`. El texto, las listas y las ecuaciones se escriben en sintaxis Org; las directivas `#+LATEX` se reservan para macros de animación y pequeños ajustes de maquetación.
- `presentacion.tex`: Beamer independiente, **ya compilado y verificado**.
- `preamble.tex`: estilo y las macros `\AnimWide`, `\AnimSide`, `\AnimTitle`. Cada imagen de portada enlaza a su video con `?autostart`, por ejemplo `\href{run:videos/archivo.mp4?autostart}{\includegraphics{...}}`.
- `source/original_excerpt.org`: fragmento original conservado sin modificaciones (como referencia).

Para exportar el Org a LaTeX necesitas Emacs con Org/ox-beamer:

```bash
bash scripts/export_org.sh   # sobreescribe presentacion.tex
bash scripts/build_pdf.sh
```

Si modificas el contenido en el `.tex` en lugar del `.org`, **no ejecutes `export_org.sh`** sin guardar una copia: la exportación sobreescribe `presentacion.tex`.

Para las previsualizaciones matemáticas de Org (`C-c C-x C-l`), `preamble.tex` omite los ajustes de Beamer cuando Org usa la clase `article`. Si Org desactivó la precompilación tras un error anterior, reabre el archivo o ejecuta `(setq-local org-latex-preview-process-precompile t)` y vuelve a generar las previsualizaciones.

## Regenerar únicamente las previsualizaciones sin Manim (opcional)

Si tienes Pillow y ffmpeg:

```bash
uv pip install --python .venv/bin/python Pillow
python scripts/render_previews.py
```

Este script es un renderizador de referencia ligero, **no sustituye a Manim**. Su propósito es que se pueda probar el PDF inmediatamente y contrastar las posiciones de los grafos con las de los guiones gráficos. También sobreescribe los MP4 y los pósteres, que representan el primer fotograma.

## Comprobaciones realizadas al preparar este ZIP

- `presentacion.tex` se compiló **dos veces con `pdflatex` sin errores**, generando 16 páginas.
- Se comprobó que **cada página tiene un enlace PDF `/Launch` a su video relativo**.
- Se generaron **16 MP4 H.264** y **16 pósteres PNG** de previsualización.
- `storyboards.py` y `manim_scenes.py` pasan la comprobación de sintaxis de Python; se comprobaron las referencias a vértices y aristas de todos los guiones.
- Las escenas «Clanes» y «Gráfica de clanes» se renderizaron con Manim y se verificó la secuencia de énfasis, incluidos los colores divididos de la intersección.

Documentación oficial: [Manim Community](https://docs.manim.community/) y [pdfpc](https://pdfpc.github.io/).


## Segunda parte: nulidad y homotopía

La segunda parte de `presentacion.org` conserva la sintaxis nativa de Org/Beamer
y añade seis animaciones Manim Community. La sección se basa en los artículos
de Prisner (1992), Larrión–Pizaña–Villarroel-Flores (2008) y
*Equivariant collapses* (2008), disponibles en la Library del autor.

Los ejemplos de diez vértices se identifican por sus cadenas graph6
`ICvbvy}|g` y `IEivrzm}o`. Se comprueban sin leer archivos del censo:

```bash
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python scripts/verify_s2_null.py
python -m unittest discover -s test
```

La verificación construye los complejos de completas, registra 20 colapsos
elementales hasta una superficie cerrada conexa con vector f=(8,18,12),
y calcula K(G), K²(G), K³(G), eliminando luego vértices dominados de K³(G).
Además reproduce las hipótesis del Teorema 3.1 de la publicación de 2008
para el disco H (Figura 2) y su suspensión. El argumento de retracción al
octaedro en K(Susp H) es el teorema publicado, no una hipótesis computacional.

Para renderizar solo las nuevas animaciones, sin repetir las diecisiete escenas
de la primera parte:

```bash
MANIM_ONLY=BettiOctaedros,DiscoSuspension,RetractoOctaedro,DosEjemplosS2,ColapsosS2,IteradasNulas bash scripts/render_manim.sh
bash scripts/export_org.sh
bash scripts/build_pdf.sh
```

Los videos `videos/*.mp4` y pósteres `posters/*.png` se generan localmente
y están excluidos del control de versiones. El código de las nuevas escenas
se encuentra en `source/segunda_parte_manim.py`, con datos verificables en
`source/segunda_parte_data.py`; el script selecciona el archivo de Manim
correspondiente a cada escena. Las primeras páginas PDF de Prisner (1992) y
Larrión–Neumann-Lara–Pizaña (2001) se mantienen intactas en `papers/`.

