{ pkgs ? import <nixpkgs> { } }:
let
  nodeEnv = import ./default.nix {};

  pythonEnv = pkgs.poetry2nix.mkPoetryEnv {
    projectDir = ./.;
    python     = pkgs.python39;
    poetrylock = ./poetry.lock;
    overrides = pkgs.poetry2nix.overrides.withDefaults (self: super: {
      werkzeug = super.werkzeug.overrideAttrs (oldAttrs: rec {
        postPatch = ''
          substituteInPlace src/werkzeug/_reloader.py \
          --replace "rv = [sys.executable]" "return sys.argv"
        '';
        doCheck = false;
      });
    });
  };

in
pkgs.mkShell {
  nativeBuildInputs = with pkgs; [
    pythonEnv
    poetry
    # yapf
    black                          ### https://github.com/psf/black
    python39Packages.isort
    python39Packages.debugpy
  ];


  buildInputs = [
    nodeEnv.shell.nodeDependencies
  ];

  shellHook = ''
    export NODE_PATH=${nodeEnv.shell.nodeDependencies}/lib/node_modules
  '';

  # TRACE   = builtins.trace (builtins.attrNames nodePkgs) "trace";

  FLASK_APP   = "dirdem";

  # FLASK_ENV   = "dummy";
  FLASK_ENV   = "development";
  # FLASK_ENV   = "staging";
  # FLASK_ENV   = "development";
  # FLASK_ENV   = "production";

  # FLASK_DEBUG = "1";
}
