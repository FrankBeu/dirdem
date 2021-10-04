{ pkgs ? import <nixpkgs> {}}:

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


      black = super.black.overridePythonAttrs (old: {
        dontPreferSetupPy = true;
      });

      didyoumean = super.didyoumean.overridePythonAttrs (old: {
        preBuild = ''
          export HOME=$(mktemp -d)
        '';
      });

      eth-brownie = super.eth-brownie.overridePythonAttrs (old: {
        propagatedBuildInputs = (old.propagatedBuildInputs or [ ]) ++ [
          self.tkinter
        ];
      });

      flit-core = super.flit-core.overridePythonAttrs (old: {
        nativeBuildInputs = (old.nativeBuildInputs or [ ]) ++ [ self.pytest-runner ];
        buildInputs = (old.buildInputs or [ ]) ++ [ self.setuptools-scm-git-archive ];
        preBuild = ''
          export HOME=$(mktemp -d)
        '';
      });

      ipfshttpclient = super.ipfshttpclient.overridePythonAttrs (old: {
        nativeBuildInputs = (old.nativeBuildInputs or [ ]) ++ [ self.pytest-runner ];
      });

      lazy-object-proxy = super.lazy-object-proxy.overridePythonAttrs (old: {
        dontPreferSetupPy = true;
      });

      mythx-models = super.mythx-models.overridePythonAttrs (old: {
        nativeBuildInputs = (old.nativeBuildInputs or [ ]) ++ [ self.pytest-runner ];
        preBuild = ''
          export HOME=$(mktemp -d)
        '';
      });

      platformdirs = super.platformdirs.overridePythonAttrs (old: {
        postPatch = ''
          substituteInPlace setup.py --replace 'setup()' 'setup(version="${old.version}")'
        '';
      });

      pycryptodome = super.pycryptodome.overridePythonAttrs (old: {
        preBuild = ''
          export HOME=$(mktemp -d)
        '';
      });

      pythx = super.pythx.overridePythonAttrs (old: {
        nativeBuildInputs = (old.nativeBuildInputs or [ ]) ++ [ self.pytest-runner ];
      });

      py-solc = super.py-solc.overridePythonAttrs (old: {
        dontPreferSetupPy = true;
        preBuild = ''
          export HOME=$(mktemp -d)
        '';
      });

      py-solc-x = super.py-solc-x.overridePythonAttrs (old: {
        dontPreferSetupPy = true;
        preBuild = ''
          export HOME=$(mktemp -d)
        '';
      });

      tomli = super.tomli.overridePythonAttrs (old: {
        nativeBuildInputs = (old.nativeBuildInputs or [ ]) ++ [
          self.flit-core
          self.pytest-runner
        ];
        preBuild = ''
          export HOME=$(mktemp -d)
        '';
      });

      vvm = super.vvm.overridePythonAttrs (old: {
        nativeBuildInputs = (old.nativeBuildInputs or [ ]) ++ [ self.pytest-runner ];
        preBuild = ''
          export HOME=$(mktemp -d)
        '';
        dontPreferSetupPy = true;
      });

      vyper = super.vyper.overridePythonAttrs (old: {
        nativeBuildInputs = (old.nativeBuildInputs or [ ]) ++ [
          self.pytest-runner
          pkgs.git
        ];
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

  # FLASK_ENV   = "fake";
  FLASK_ENV   = "development";
  # FLASK_ENV   = "staging";
  # FLASK_ENV   = "production";

  # FLASK_DEBUG = "1";
}
