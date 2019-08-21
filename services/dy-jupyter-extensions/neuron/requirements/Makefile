.PHONY: all check clean help base

objects = $(wildcard *.in)
outputs := $(objects:.in=.txt)

# target: all – pip-compiles all requirements/*.in -> requirements/*.txt
all: $(outputs)

%.txt: %.in
	pip-compile --output-file $@ $<

# target: check – Checks whether pip-compile is installed
check:
	@which pip-compile > /dev/null

# target: clean – Cleans all requirements/*.txt
clean: check
	- rm $(outputs)

base:
	docker run --rm --entrypoint pip itisfoundation/jupyter-base-notebook:2.13.0 freeze | grep -v simcore- | grep -v conda > base.txt

# target: help – Display all callable targets
help:
	@echo
	@egrep "^\s*#\s*target\s*:\s*" [Mm]akefile \
	| sed -r "s/^\s*#\s*target\s*:\s*//g"
	@echo
