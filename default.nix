{
  buildPythonApplication,
  makeWrapper,
  pytestCheckHook,
  setuptools,
  runCommand,
}:
buildPythonApplication {
  pname = "goto`";
  version = "1.0.0";
  src = ./.;
  format = "pyproject";
  buildInputs = [ makeWrapper ];
  nativeBuildInputs = [ setuptools ];
  doCheck = true;
  checkPhase = ''
    PYTHONPATH= $out/bin/goto --help
  '';
  passthru.tests.pytest =
    runCommand "pytest"
      {
        nativeBuildInputs = [
          pytestCheckHook
        ];
      }
      ''
        cp -r ${./.}/* .
        chmod -R +w .
        pytest .
        touch $out
      '';
}
