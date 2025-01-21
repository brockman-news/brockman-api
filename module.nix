{
  lib,
  pkgs,
  config,
  ...
}:
let
  cfg = config.services.brockman-api;
in
{
  options.services.brockman-api = {
    enable = lib.mkEnableOption "brockman api service";
    package = lib.mkOption {
      type = lib.types.package;
      default = pkgs.python3.pkgs.callPackage ./default.nix { };
    };
    port = lib.mkOption {
      type = lib.types.int;
      default = 7331;
      description = "Port to listen on";
    };
    irc-server = lib.mkOption {
      type = lib.types.string;
      default = "brockman.news";
      description = "IRC server to connect to";
    };
    control-channel = lib.mkOption {
      type = lib.types.string;
      default = "#all";
      description = "IRC channel to listen on";
    };
    openFirewall = lib.mkEnableOption "open port in firewall";
  };
  config = lib.mkIf cfg.enable {
    networking.firewall.allowedTCPPorts = lib.mkIf cfg.openFirewall [ cfg.port ];

    systemd.services.brockman-api = {
      description = "brockman api service";
      wantedBy = [ "multi-user.target" ];
      after = [
        "network.target"
      ];
      serviceConfig = {
        ExecStart = ''
          ${cfg.package}/bin/brockman-api \
            --port ${toString cfg.port} \
            --irc-server ${cfg.irc-server} \
            --control-channel ${cfg.control-channel}
        '';
        StateDirectory = "goto";
      };
    };
  };
}
