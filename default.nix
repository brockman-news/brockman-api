{
  buildPythonApplication,
  makeWrapper,
  setuptools,
}:
buildPythonApplication {
  pname = "brockman-api";
  version = "1.0.0";
  src = ./.;
  format = "pyproject";
  buildInputs = [ makeWrapper ];
  nativeBuildInputs = [ setuptools ];
  doCheck = true;
  checkPhase = ''
    PYTHONPATH= $out/bin/brockman-api --help
  '';
}
