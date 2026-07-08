.PHONY: build check serve

build:
	hugo --minify

check: build
	python3 -B scripts/check-site.py

serve:
	hugo server --bind 127.0.0.1 --port 1317 --disableFastRender
