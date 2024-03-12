powermon-unit-tests: 
	python3 -m unittest discover -s tests/unit -f -v

powermon-integration-tests: 
	python3 -m unittest discover -s tests/integration -f -v

test:
	python3 -m unittest discover -s tests -f

# pypi:
# 	rm -rf dist/*
# 	#python3 -m build 
# 	./make_version.sh
# 	poetry build
# 	poetry version patch
# 	./make_version_dev.sh
# 	ls -l dist/
# 	cat powermon/libs/version.py

# pypi-upload:
# 	twine upload dist/*

docker-up:
	docker-compose up --build

docker-powermon-dev-up:
	docker compose -f docker-compose.development.yaml up --build

git-tag-release:
	./make_version.sh
	@echo Moving from version `awk '/^version/ {print $$3}' pyproject.toml`
	@poetry version patch
	./make_version_dev.sh
	@git tag `awk '/^version/ {print substr($$3, 2, length($$3)-2)}' pyproject.toml`
	@git push origin --tags
	@echo "Now go to github and create a release for the latest tag" `awk '/^version/ {print substr($$3, 2, length($$3)-2)}' pyproject.toml`
