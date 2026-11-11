;; -*- lexical-binding: t; -*-

(TeX-add-style-hook
 "test"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-class-options
                     '(("beamer" "aspectratio=169")))
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("graphicx" "") ("multimedia" "")))
   (TeX-run-style-hooks
    "latex2e"
    "beamer"
    "beamer10"
    "graphicx"
    "multimedia"))
 :latex)

