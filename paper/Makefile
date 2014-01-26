all: sigproc-sp.tex sigproc.bib
	pdflatex sigproc-sp.tex
	bibtex sigproc-sp.aux
	pdflatex sigproc-sp.tex
	pdflatex sigproc-sp.tex

clean:
	rm -f sigproc-sp.{aux,bbl,blg,log}
