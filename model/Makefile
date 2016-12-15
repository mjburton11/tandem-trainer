all:
	python -c 'import gpkit.tools; exec gpkit.tools.mdmake("tandem.md")'
	pandoc --template default.latex tandem.md.tex.md -o "tandem.pdf"
