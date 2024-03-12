powermon-unit-tests: 
	python3 -m unittest discover -s tests/unit -f -v

powermon-integration-tests: 
	python3 -m unittest discover -s tests/integration -f -v

test:
	python3 -m unittest discover -s tests -f

docker-up:
	docker-compose up --build

docker-powermon-dev-up:
	docker compose -f docker-compose.development.yaml up --build

git-tag-release:
	@./make_version.sh
	@echo Creating a tag for version: `awk '/^version/ {print $$3}' pyproject.toml`
	@git tag `awk '/^version/ {print substr($$3, 2, length($$3)-2)}' pyproject.toml`
	@git push origin --tags
	@echo "Now go to github and create a release for the latest tag" `awk '/^version/ {print substr($$3, 2, length($$3)-2)}' pyproject.toml`
	@echo Bumping version..
	@poetry version patch
	@echo Adding '-dev' to version in git
	@./make_version_dev.sh
