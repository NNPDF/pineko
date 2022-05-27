# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   = sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

PINEKODIR = ../src/eko
PINEKOOUT = $(SOURCEDIR)/modules/pineko

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

server:
	python3 -m http.server 8000 --bind 127.0.0.1 --directory $(BUILDDIR)/html

view: html
	$(BROWSER) $(BUILDDIR)/html/index.html


clean:
	rm -rf build
	rm -rf _build

cleanall: clean clean-todos
	rm -rf $(PINEKOOUT)

# TODOs
todos:
	python generate_code_todos.py "$(PINEKODIR)" "$(TODOOUTFILE)"

clean-todos:
	rm "$(TODOOUTFILE)"
