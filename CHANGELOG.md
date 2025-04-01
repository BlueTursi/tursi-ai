# CHANGELOG


## Unreleased

### Chore

* chore(release): bump version to 0.2.7 ([`4837e59`](https://github.com/BlueTursi/tursi-ai/commit/4837e59e43d0a120a979307213cac80075a0ae31))

* chore(release): bump version to 0.2.6 ([`3df1d31`](https://github.com/BlueTursi/tursi-ai/commit/3df1d31308b33eb92aecd6c2cdd70d12305fad9e))

* chore(release): bump version to 0.2.5 ([`679eb41`](https://github.com/BlueTursi/tursi-ai/commit/679eb41ab58a61f85912059bac66455d323b647b))

* chore: update workflows to use Poetry and fix YAML syntax ([`59034b0`](https://github.com/BlueTursi/tursi-ai/commit/59034b06c63c55bebd3095014845e8b26c62bd0c))

* chore: update changelog workflow to use Poetry ([`f79a7b2`](https://github.com/BlueTursi/tursi-ai/commit/f79a7b20f261e2bd32768c527e3d02551cbffe36))

* chore: update workflows to only trigger releases on significant updates ([`7954dca`](https://github.com/BlueTursi/tursi-ai/commit/7954dcac4fb12a563e841711f5a8e9b2dbe7c16e))

* chore: add flake8 configuration to be less strict ([`560820a`](https://github.com/BlueTursi/tursi-ai/commit/560820a931890f6e0c7a1a194a2c6f435cc9938d))

* chore: update lint workflow to use Poetry ([`022cd00`](https://github.com/BlueTursi/tursi-ai/commit/022cd0067eea4d784f8d1bbe436e2588aef739af))

* chore: remove redundant CodeQL steps from test workflow ([`d85fb94`](https://github.com/BlueTursi/tursi-ai/commit/d85fb9424fac1b867e7399222c57aba847720e2e))

* chore: update gitignore with comprehensive Python patterns ([`f2cc9d7`](https://github.com/BlueTursi/tursi-ai/commit/f2cc9d78cea463a9129d150dbb1c771032fc403a))

* chore: remove legacy package files in favor of Poetry ([`55c645e`](https://github.com/BlueTursi/tursi-ai/commit/55c645e747805e130bbb13532d85fa90e388fb25))

### Ci

* ci: update CodeQL configuration to use default setup ([`96374ba`](https://github.com/BlueTursi/tursi-ai/commit/96374baa0a0c62889706de1b1b2bd281f479b926))

* ci: switch to poetry for dependency management ([`0907689`](https://github.com/BlueTursi/tursi-ai/commit/0907689d145de65cbe8aa4ee211cba01aa56c410))

* ci: remove redundant snyk workflow ([`91afb02`](https://github.com/BlueTursi/tursi-ai/commit/91afb02069c9586631ecc5328e0ae964181386c2))

* ci: replace conventional-changelog-cli with python-semantic-release ([`02adf43`](https://github.com/BlueTursi/tursi-ai/commit/02adf432920ebcccfe5a07a9252e3578f7d7ed50))

* ci: fix test and security workflows ([`cdaa71d`](https://github.com/BlueTursi/tursi-ai/commit/cdaa71d0c2de181d1e800e69242f8b36f4271d14))

* ci: switch to python-semantic-release and fix linting ([`3798c90`](https://github.com/BlueTursi/tursi-ai/commit/3798c90ea8db966e120da781aaec8fe6f13d38fe))

* ci: fix release workflow ([`ea393d7`](https://github.com/BlueTursi/tursi-ai/commit/ea393d7e08434acd76656b71c188089839f2b616))

* ci: add enhanced CI/CD pipeline feature to README ([`91a4163`](https://github.com/BlueTursi/tursi-ai/commit/91a4163158a819de6dddc30fe2157ca859296666))

* ci: fix test and changelog workflows ([`64fe09d`](https://github.com/BlueTursi/tursi-ai/commit/64fe09d9f73e1bb489cd75f1cd186cd01551cc2c))

* ci: add semantic versioning feature to README ([`f9e0801`](https://github.com/BlueTursi/tursi-ai/commit/f9e08010dbc2656d5beba46b8b7b841801534861))

* ci: fix GitHub Actions workflows ([`c4c3564`](https://github.com/BlueTursi/tursi-ai/commit/c4c35643d549f45c511e4bec62e0cbb003f79ca6))

* ci: add improved release workflow feature to README ([`12ef6f2`](https://github.com/BlueTursi/tursi-ai/commit/12ef6f2dc0f26268c68fc10f9ef802875b06bec8))

* ci: fix version bump and release workflows ([`7dddf14`](https://github.com/BlueTursi/tursi-ai/commit/7dddf148ede869e0b39ccf52101927a818f340d5))

* ci: add automated GitHub releases feature to README ([`db2a38c`](https://github.com/BlueTursi/tursi-ai/commit/db2a38c9f4f2e0503ede44459e1b3059da56e632))

* ci: fix release workflow to properly handle tag push events ([`51f6660`](https://github.com/BlueTursi/tursi-ai/commit/51f66609ece98cb4b315ef3dd15fea65f7467e4c))

* ci: add CI/CD pipeline feature to README ([`924565c`](https://github.com/BlueTursi/tursi-ai/commit/924565cdb55677f6cc54f179ea06fd1b7c20a737))

* ci: fix version bump and release workflows ([`36a0116`](https://github.com/BlueTursi/tursi-ai/commit/36a011631c531099fb644bee8fa4e718f4e77a7e))

* ci: split version bump and release workflows ([`c0af908`](https://github.com/BlueTursi/tursi-ai/commit/c0af908e40c1ab8539a2af63672986d8f35a1827))

### Documentation

* docs: update README with simplified instructions and features ([`4a5032e`](https://github.com/BlueTursi/tursi-ai/commit/4a5032ed0bd7eca5cd189704980c5029a6cb1f4e))

### Feature

* feat: add special handling for security patches in version bumping ([`c824a79`](https://github.com/BlueTursi/tursi-ai/commit/c824a79fe5afa09b53aae4c950c5e5adae7a4d67))

### Fix

* fix: create valid SARIF file with required tool and results structure ([`9b10f6a`](https://github.com/BlueTursi/tursi-ai/commit/9b10f6ac8897cfcf9fc9c51dec275a61b88684be))

* fix: create valid empty SARIF file for Snyk ([`61a609e`](https://github.com/BlueTursi/tursi-ai/commit/61a609ed72e1f4b3645820dbc0e9e14a56ca6fc7))

* fix: update semantic-release changelog command ([`94e6cd1`](https://github.com/BlueTursi/tursi-ai/commit/94e6cd18e4b248812f30bbf1d57b747a09d42f7f))

* fix: update workflows to handle errors and fix version bumping ([`83e93ca`](https://github.com/BlueTursi/tursi-ai/commit/83e93ca04ad2a233e75b3f1c5f438693c0284739))

* fix: update workflows to use Poetry and handle Snyk errors gracefully ([`90b97c1`](https://github.com/BlueTursi/tursi-ai/commit/90b97c10bee4803009f9a5c509c8b719a0e7fd50))

* fix: add model validation to prevent invalid model loading ([`979051b`](https://github.com/BlueTursi/tursi-ai/commit/979051bf3aeaa7fa43df34b35274a23edd003375))

* fix: add __version__ attribute to package ([`bf062ba`](https://github.com/BlueTursi/tursi-ai/commit/bf062ba12997ae2c650675d2d77860c474ce8a07))

### Style

* style: fix whitespace in engine.py ([`786101e`](https://github.com/BlueTursi/tursi-ai/commit/786101e3d64251776c7c44f7bceb09fc7692f457))

* style: fix flake8 issues in engine.py ([`2471bc0`](https://github.com/BlueTursi/tursi-ai/commit/2471bc0fd0da33216b23ecbf4a26907239aa7cf8))

### Test

* test: fix test suite and remove redundant linting ([`9befa3f`](https://github.com/BlueTursi/tursi-ai/commit/9befa3fea1cd39f5bf3afae6de20853bbf19faa6))

* test: add initial test suite ([`4474a15`](https://github.com/BlueTursi/tursi-ai/commit/4474a158e86ac699c35a710699a4b3b63ed85927))

### Unknown

* Feat: update gitignore for local bin ([`dca4ea3`](https://github.com/BlueTursi/tursi-ai/commit/dca4ea32dce787f326fa3dec0fc1c7380565ffc5))



## v0.2.4 (2025-03-31)

### Chore

* chore(release): bump version to 0.2.4 ([`dce5c87`](https://github.com/BlueTursi/tursi-ai/commit/dce5c8781e54ab245083ae7c1bdbef68b185ccc2))

### Fix

* fix(security): improve code security and add CodeQL scanning ([`e9a8416`](https://github.com/BlueTursi/tursi-ai/commit/e9a84161501197aa4b1602231e2ab497eb9a1cc8))


## v0.2.3 (2025-03-31)

### Chore

* chore(release): bump version to 0.2.3 ([`0d8d0c4`](https://github.com/BlueTursi/tursi-ai/commit/0d8d0c4faffc7270c045fb85d2a3317d48fb026e))

### Fix

* fix(security): add explicit permissions to GitHub Actions workflows ([`5aa5c79`](https://github.com/BlueTursi/tursi-ai/commit/5aa5c791021c9a78fa9e494e0b2e51b548dd57ae))

* fix(security): disable debug mode and improve error handling ([`f8e30a7`](https://github.com/BlueTursi/tursi-ai/commit/f8e30a757bb83ae385768228578d9018a983e761))


## v0.2.2 (2025-03-31)

### Chore

* chore(release): bump version to 0.2.2 ([`52a0fd2`](https://github.com/BlueTursi/tursi-ai/commit/52a0fd287359431e0f16df095b395f970b85a6a1))

### Ci

* ci: add automated release and changelog workflows ([`ef874df`](https://github.com/BlueTursi/tursi-ai/commit/ef874dfaf60f48d893d713dd431dc69de7a6d535))

### Unknown

* Create SECURITY.md ([`34c396e`](https://github.com/BlueTursi/tursi-ai/commit/34c396edac6c1b04cf8ceec96645e88768af62b2))


## v0.2.1 (2025-03-31)

### Unknown

* Fix: PEEP 8 style ([`ceffc25`](https://github.com/BlueTursi/tursi-ai/commit/ceffc25e335a03520717f1c8053eb8723dd7e603))

* Update github action for lint and snyk ([`03fcced`](https://github.com/BlueTursi/tursi-ai/commit/03fcced51aed6126eeab359c911436ebd8c0a669))

* Create snyk-security.yml ([`6725555`](https://github.com/BlueTursi/tursi-ai/commit/672555551feb5cae7be93f445a65c4ca4d2b595f))

* Add v0.2.0 build package ([`455144b`](https://github.com/BlueTursi/tursi-ai/commit/455144bcec1a9dfaa372eb1653458ec410793f3f))


## v0.2.0 (2025-03-29)

### Unknown

* Finalize v0.2.0 with up/down commands and venv check ([`d2a9f54`](https://github.com/BlueTursi/tursi-ai/commit/d2a9f546410f2cdd4d16679ed341bd7ced7e5b25))

* Add GitHub release badge for v0.1.0 ([`d0fe392`](https://github.com/BlueTursi/tursi-ai/commit/d0fe392b502a96b1dbe1ba8e37be353ea0cd0f70))


## v0.1.0 (2025-03-27)

### Unknown

* Restructure for PyPI packaging as tursi v0.1.0 ([`f7f4bf1`](https://github.com/BlueTursi/tursi-ai/commit/f7f4bf19b287d491ca7bbc2fd16903a1580784b3))

* Update tursi-engine for CLI ([`aac444c`](https://github.com/BlueTursi/tursi-ai/commit/aac444c15a73d72c58087688553889cf54e78195))

* Feat: add tursi-test ([`1886e79`](https://github.com/BlueTursi/tursi-ai/commit/1886e791d68b6e11f6631adfa43776caae7fc62c))

* Add local tursi-engine CLI for model deployment ([`69223e9`](https://github.com/BlueTursi/tursi-ai/commit/69223e9c4c7bc213048e7f2da3b99255fd8b7a79))

* Exclude W292 temporarily in Flake8 config ([`b24730c`](https://github.com/BlueTursi/tursi-ai/commit/b24730c90bacd378abaae4e6a93bfbe0882b7084))

* Feat: add gitattributes ([`fd056d0`](https://github.com/BlueTursi/tursi-ai/commit/fd056d05eb5df92f4b2bd35f31af19e1d0c2f706))

* Feat: Add Github Action ([`f0693d9`](https://github.com/BlueTursi/tursi-ai/commit/f0693d911e6ac307b598e7947c3860b54509fe7e))

* Feat: Add BERT example and License fix readme ([`4b11ede`](https://github.com/BlueTursi/tursi-ai/commit/4b11ede17fe546f682562607bd82ac563762edb7))

* Feat: Add BERT example and License ([`2dc4408`](https://github.com/BlueTursi/tursi-ai/commit/2dc440874c2c204e5342a41da63368dc696154b2))

* Feat: Add tursi-engine placeholder ([`162c7a9`](https://github.com/BlueTursi/tursi-ai/commit/162c7a954282eac46431d4b30767d2f047659972))

* first commit ([`ec19a6e`](https://github.com/BlueTursi/tursi-ai/commit/ec19a6e84c0d131e460d4634e86b47ff8eff828b))
