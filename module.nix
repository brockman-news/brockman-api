{
  lib,
  pkgs,
  config,
  ...
}:
let
  cfg = config.services.goto;
in
{
  options.services.goto = {
    enable = lib.mkEnableOption "goto simple url shortener";
    package = lib.mkOption {
      type = lib.types.package;
      default = pkgs.python3.pkgs.callPackage ./default.nix { };
    };
    port = lib.mkOption {
      type = lib.types.int;
      default = 7331;
      description = "Port to listen on";
    };
    hashAlgorithm = lib.mkOption {
      type = lib.types.enum [
        "blake2b"
        "blake2s"
        "md5"
        "md5-sha1"
        "ripemd160"
        "sha1"
        "sha224"
        "sha256"
        "sha384"
        "sha3_224"
        "sha3_256"
        "sha3_384"
        "sha3_512"
        "sha512"
        "sha512_224"
        "sha512_256"
        "shake_128"
        "shake_256"
        "sm3"
      ];
      default = "sha256";
      description = "Hash algorithm to use";
    };
    hashLength = lib.mkOption {
      type = lib.types.int;
      default = 5;
      description = "Length of the hash that goto generates";
    };
    cacheSize = lib.mkOption {
      type = lib.types.int;
      default = 100;
      description = "Number of entries to cache in memory";
    };
    openFirewall = lib.mkEnableOption "open port in firewall";
  };
  config = lib.mkIf cfg.enable {
    networking.firewall.allowedTCPPorts = lib.mkIf cfg.openFirewall [ cfg.port ];

    users.users.goto = {
      isSystemUser = true;
      home = "/var/lib/goto";
    };

    systemd.services.goto = {
      description = "goto simple url shortener";
      wantedBy = [ "multi-user.target" ];
      after = [
        "network.target"
      ];
      serviceConfig = {
        User = "goto";
        ExecStart = ''
          ${cfg.package}/bin/goto \
            --port ${toString cfg.port} \
            --hash-algorithm ${cfg.hashAlgorithm} \
            --hash-length ${toString cfg.hashLength} \
            --state-directory /var/lib/goto \
            --cache-size ${toString cfg.cacheSize}
        '';
        StateDirectory = "goto";
      };
    };
  };
}
