{
  description = "Prism Launcher Metadata generation scripts";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    pre-commit-hooks = {
      url = "github:cachix/pre-commit-hooks.nix";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.nixpkgs-stable.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, pre-commit-hooks, poetry2nix, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonPackages = pkgs.python311Packages;
        myPoetry2nix = poetry2nix.lib.mkPoetry2Nix { inherit pkgs; };
      in {
        checks = {
          pre-commit-check = pre-commit-hooks.lib.${system}.run {
            src = ./.;
            hooks = {
              black.enable = true;
              nixfmt.enable = true;
            };
          };
        };
        devShells.default = pkgs.mkShell {
          inherit (self.checks.${system}.pre-commit-check) shellHook;
          packages = (with pkgs; [
            (myPoetry2nix.mkPoetryEnv {
              projectDir = self;
              overrides = myPoetry2nix.overrides.withDefaults (self: super: {
                cachecontrol = super.cachecontrol.overridePythonAttrs (old: {
                  buildInputs = (old.buildInputs or [ ]) ++ [ self.flit-core ];
                });
                editables = super.editables.overridePythonAttrs (old: {
                  buildInputs = (old.buildInputs or [ ]) ++ [ self.flit-core ];
                });
              });
            })
            poetry
            nixfmt
            black
          ]);
        };
      });
}
