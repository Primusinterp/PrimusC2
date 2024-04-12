locals {
  peer_templates = flatten([
    for idx, pubkey in var.pubkeys : templatefile("${path.module}/config_templates/peer.tpl", {
      index = idx + 2
      pubkey = pubkey
    })
  ])
}

locals {
  server_template = templatefile("${path.module}/config_templates/server.tpl", {
    private_key = var.wireguard_private_key[0]
    peers = join("\n", local.peer_templates)
  })
}