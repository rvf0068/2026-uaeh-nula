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

## Renderizar los dieciséis videos con Manim

```bash
source .venv/bin/activate
bash scripts/render_manim.sh
```

Por omisión usa `-ql` (calidad baja, para pruebas). Para calidad alta:

```bash
MANIM_QUALITY=-qh bash scripts/render_manim.sh
```

El script ejecuta Manim escena por escena, copia cada MP4 a `videos/` y extrae mediante `ffmpeg` su primer fotograma a `posters/`. **Sobrescribe** las previsualizaciones MP4 incluidas. Los archivos `source/storyboards.py` y `source/manim_scenes.py` contienen las geometrías y la animación editable de los 16 ejemplos. Los videos muestran etapas sucesivas sin texto, mediante fundidos; se pueden personalizar las transiciones en `_Storyboard.construct()`.

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
- **No fue posible ejecutar Manim aquí**, por no estar instalado ni disponible desde la red. Por tanto, el render exacto de Manim todavía debe probarse en el Ubuntu del usuario. El PDF y las previsualizaciones, en cambio, sí están generados.

## Mapa de ejemplos

| Escena Manim | Animación en la presentación |
| --- | --- |
| `Intro` | Portada con el ejemplo de la casa |
| `Graficas` | Aparición de vértices y aristas |
| `Completas` | Completas no necesariamente maximales |
| `Clanes` | Los dos clanes maximales del ejemplo |
| `GraficaDeClanes` | Clanes como vértices de `K(G)` |
| `Ejemplo` | Selección de clanes y construcción de `K(G)` |
| `Iteradas` | Casa → `K_2` → `K_1` |
| `Prisma` | Prisma triangular → `K_{2,3}` → prisma |
| `SuspensionC5` | Suspensión de `C_5` y su gráfica de 10 clanes |
| `Comportamiento` | Ejemplos convergente y divergente |
| `IteradasOctaedro` | `O_3` → `O_4` → `O_8` |
| `Helly` | Clanes que se intersectan en un vértice común |
| `Piramide` | Tres clanes intersecantes sin intersección total |
| `Escalante` | Pirámide → `K_4` → `K_1` |
| `Desmantelables` | Eliminación de hojas de un árbol |
| `Dominados` | Octaedro con hojas, eliminación y crecimiento del iterado |

Documentación oficial: [Manim Community](https://docs.manim.community/) y [pdfpc](https://pdfpc.github.io/).
