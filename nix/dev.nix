{
  inputs,
  self,
  ...
}: {
  perSystem = {
    system,
    pkgs,
    ...
  }: {
    checks = {
      pre-commit-check = inputs.pre-commit-hooks.lib.${system}.run {
        src = self;
        hooks = {
          markdownlint.enable = true;

          alejandra.enable = true;
          deadnix.enable = true;
          nil.enable = true;

          black.enable = true;
        };
      };
    };

    devShells.default = pkgs.mkShell {
      inherit (self.checks.${system}.pre-commit-check) shellHook;

      packages = with pkgs; [
        (poetry2nix.mkPoetryEnv {
          projectDir = self;
          overrides = pkgs.poetry2nix.overrides.withDefaults (self: super: {
            cachecontrol = super.cachecontrol.overridePythonAttrs (old: {
              buildInputs = (old.buildInputs or []) ++ [self.flit-core];
            });
            editables = super.editables.overridePythonAttrs (old: {
              buildInputs = (old.buildInputs or []) ++ [self.flit-core];
            });
          });
        })
        poetry
      ];
    };

    formatter = pkgs.alejandra;
  };
}
