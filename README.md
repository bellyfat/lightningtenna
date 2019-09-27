# lightningtenna

Pay a lightning invoice over goTenna mesh network

Terms:

* MESH -- the off-grid machine. Has a copy of C-Lightning installed, a Blockstream satellite connection for blockchain backend, and will run lightningtenna/src/MESH_client.py to relay C-Lightning messages for a single channel, over mesh network.

* GATEWAY -- has a connection to goTenna mesh network and also internet. Does not have C-Lightning or Bitcoin blockchain capability but will run lightningtenna/src/GATEWAY_client.py. A pure relay/proxy.

* REMOTE -- the remote channel counterpaty for the lightning channel MESH has open, not GATEWAY! Has C-Lightning running only.

Optional but recommended C-Lightning `config` options:

```
# listen but don't announce
bind-addr=0.0.0.0:9733
# disable dns lookup of peers
disable-dns
# see wire messages
log-level=io
```


## Setup

1) C-Lightning on MESH and GATEWAY *must* be modified before compilation:
    
    1) Apply the following changes to source code for C-Lightning on MESH and GATEWAY: 
    
        [Increase HTLC Timeout](https://github.com/willcl-ark/lightning/commit/75c53de45c3df44a56841048bac98422f4b0a15c) 
        
        [Fully Suppress Gossip](https://github.com/willcl-ark/lightning/commit/14c12eca4c172ca0b8d787a0405b7346b88b70ae)
    

1) Both instances of C-Lightning should be ./configured using `--enable-developer` flag in order to permit the `lightning-cli dev-suppress-gossip` command.

1) Before first start, modify the values in example_config.ini as appropriate

1) MESH should have a single peer and single channel open in C-Lightning

1) On MESH, ensure C-Lightning is not running

1) On MESH, access the C-Lightning database: (~/.lightning/lightningd.sqlite3). Open the `Peers` table and find the row corresponding to REMOTE (ip address and port). Modify the `address` column to have the value `127.0.0.1:9733`, or whatever you set in `example_config.ini` previously

1) On REMOTE start C-Lightning. Issue RPC command: `lightning-cli dev-suppress-gossip`

1) On MESH, start the python mesh client: `python MESH_client.py`, power on goTenna (a) and await connection messages.

1) On GATEWAY (can be same machine for testing) start the gateway client `python GATEWAY_client.py`, power on goTenna (b) and await connection messages.

1) On MESH start C-Lightning.

1) Watch them communicate via mesh network proxy.

1) Pay an invoice.