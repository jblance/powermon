powermon-unit-tests: 
	python3 -m unittest discover -s tests/unit -f -v

powermon-integration-tests: 
	python3 -m unittest discover -s tests/integration -f -v

test:
	python3 -m unittest discover -s tests -f

unit-tests:
	python3 -m unittest discover -s tests/unit -f

docker-up:
	docker-compose up --build

docker-powermon-dev-up:
	docker compose -f docker-compose.development.yaml up --build

git-tag-release:
	@./make_version.sh
	@echo Creating a tag for version: `awk '/^version/ {print $$3}' pyproject.toml`
	@echo Pushing version changes to git
	git add powermon/libs/version.py
	git commit -m "remove -dev from version"
	git push
	@git tag `awk '/^version/ {print substr($$3, 2, length($$3)-2)}' pyproject.toml`
	@git push origin --tags
	@echo "Now go to github and create a release for the latest tag" `awk '/^version/ {print substr($$3, 2, length($$3)-2)}' pyproject.toml`
	@echo Bumping version..
	@poetry version patch   # major, minor, patch
	@echo Adding '-dev' to version in git
	@./make_version_dev.sh
	@echo Pushing version changes to git
	git add powermon/libs/version.py pyproject.toml
	git commit -m "Update versions"
	git push

mqtt-docker-start:
	docker run --rm  --network=host -v ./docker/mosquitto/config:/mosquitto/config eclipse-mosquitto

transl-extract:
	xgettext -d powermon -o powermon/locale/powermon.pot -L python -f files_to_translate.txt

transl-gen-en:
	msginit -l en_US.UTF8 -o powermon/locale/en/LC_MESSAGES/powermon.po -i powermon/locale/powermon.pot --no-translator

transl-compile:
	msgfmt -o powermon/locale/en/LC_MESSAGES/powermon.mo powermon/locale/en/LC_MESSAGES/powermon.po

transl: transl-extract transl-gen-en transl-compile
