#!/usr/bin/env python3
# Copyright (c) 2021 Patrick Lodder
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
"""Stuck Transaction Demo

# Demonstrates scenarios with stuck tx
"""

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import *
from decimal import Decimal

class StuckTxDemo(BitcoinTestFramework):

    def __init__(self):
        super().__init__()
        self.setup_clean_chain = True
        self.num_nodes = 4

        # set up a receiving address outside of nodes' wallets
        self.recv = "n4LRQGEKcyRCXqD2MH3ompyMTJKitxu1WP"

        # we're going to simulate mempool expiry over a 2 hour period
        self.mocktime = int(time.time()) - 2 * 60 * 60

    def setup_nodes(self, split=False):
        nodes = []

        # Our wallet that wants to send tx with 0.1 DOGE/kb fee
        nodes.append(start_node(0, self.options.tmpdir,
            ["-acceptnonstdtxn=0", "-paytxfee=0.1", "-minrelaytxfee=0.1", "-mempoolexpiry=1"]))

        # 1.14.3 Relay node
        nodes.append(start_node(1, self.options.tmpdir,
            ["-acceptnonstdtxn=0", "-minrelaytxfee=1", "-mempoolexpiry=1"]))

        # 1.14.4-style Relay node
        nodes.append(start_node(2, self.options.tmpdir,
            ["-acceptnonstdtxn=0", "-mempoolexpiry=1"]))

        # 1.14.3 Miner node
        nodes.append(start_node(3, self.options.tmpdir,
            ["-acceptnonstdtxn=0", "-minrelaytxfee=1", "-mempoolexpiry=1"]))

        return nodes

    def setup_network(self, split = False):
        self.nodes = self.setup_nodes()
        self.names = [
          "wallet",
          "relay1",
          "relay2",
          " miner"
        ]

        # set the time 2 hours back
        for n in self.nodes:
            n.setmocktime(self.mocktime)

        # connect wallet node to relay nodes
        connect_nodes_bi(self.nodes, 0, 1)
        connect_nodes_bi(self.nodes, 0, 2)

        # connect relay nodes to miner node
        connect_nodes_bi(self.nodes, 1, 3)
        connect_nodes_bi(self.nodes, 2, 3)

        self.is_network_split = False
        self.sync_all()

    def run_test(self):

        print("[00] Setup...  (T=T-2h)")
        self.print_fee_config()

        print(f"\n[01] Mining blocks and seeding wallet...  (T=T-2h)")
        # mine 100 blocks
        self.nodes[3].generate(100)
        self.sync_all()

        # send 5 outputs of 100,000 DOGE to our wallet
        seed_addr = self.nodes[0].getnewaddress()
        for _ in range(5):
            self.nodes[3].sendtoaddress(seed_addr, 100000);

        # mine 5 more blocks to confirm and mature the txs
        self.nodes[3].generate(5)
        self.sync_all()

        self.print_wallet_balance()

        # now we send out 3 transactions of 51-53k DOGE each from our wallet
        # to the 3rd party address that no one in the network owns
        print(f"\n[02] Sending 3 too low fee transactions... (T-2h)")
        txs = []
        for i in range(3):
            txs.append(self.nodes[0].sendtoaddress(self.recv, 51000 + 1000 * i))
            print(f"  tx{i}: {txs[i]} sending {51000 + 1000 * i} to {self.recv}")

        self.print_wallet_mempool_size()
        self.print_wallet_balance()

        print("\n[03] Syncing mempools... (T=T-2h)")
        # node 2 should accept these tx
        sync_mempools([self.nodes[0], self.nodes[2]])

        # our wallet and the 1.14.4 node will have these tx
        for i in [0,2]:
            mempool = self.nodes[i].getrawmempool()
            for tx in txs:
                assert tx in mempool
                print(f"  {self.names[i]} has {tx} in mempool")

        # the 1.14.3 node and the miner do not have these tx
        for i in [1,3]:
            mempool = self.nodes[i].getrawmempool()
            for tx in txs:
                assert tx not in mempool
                print(f"  {self.names[i]} does not have {tx} in mempool")

        print("\n[04] Mining a block... (T=T-2h)")
        # mine a block
        self.nodes[3].generate(1)
        sync_blocks(self.nodes)

        # our wallet and the 1.14.4 node will have these tx in mempool
        for i in [0,2]:
            mempool = self.nodes[i].getrawmempool()
            for tx in txs:
                assert tx in mempool
                print(f"  {self.names[i]} still has {tx} in mempool")

        self.print_wallet_balance()

        # END OF LIVING IN THE PAST
        print("\n==============================================")

        print("\n[05] Timewarp back to the future, mempools expire... (T=T+0)")

        # fast-forward 2 hours
        for n in self.nodes:
            n.setmocktime(int(time.time()))

        # send a tx from miner to relay 1
        # this is to trigger mempool expiry on all nodes
        self.nodes[3].sendtoaddress(self.nodes[1].getnewaddress(), 500)
        sync_mempools(self.nodes)

        # mine a block
        self.nodes[3].generate(1)
        sync_blocks(self.nodes)

        # all mempools are empty
        for i in range(4):
            mempool = self.nodes[i].getrawmempool()
            assert_equal(len(mempool), 0)
            print(f"  {self.names[i]} has {len(mempool)} transactions in mempool")

        print("\n[06] Our wallet seems confused now... (T=T+0)")

        # our wallet is many confused now
        assert self.nodes[0].getbalance() < Decimal("500000.0")
        self.print_wallet_balance()
        print("  very concern!")

        print("\n[07] But the wallet still remembers these transactions... (T=T+0)")
        hex_txs = []
        for tx in txs:
            wtx = self.nodes[0].gettransaction(tx)
            assert wtx
            print(f"  wallet remembers tx {wtx['txid']} for {wtx['amount']}")
            hex_txs.append(wtx["hex"])

        print("\n[08] Replace tx0 for 51000 correctly... (T=T+0)")

        replace_this = self.nodes[0].decoderawtransaction(hex_txs[0])
        inputs = []
        outputs = {}
        total_input_value = Decimal("0.0")

        print("  copy inputs:")
        for inpt in replace_this["vin"]:
            total_input_value += self.nodes[0].gettxout(inpt["txid"], inpt["vout"])["value"]
            inputs.append({"txid": inpt["txid"], "vout": inpt["vout"]})
            print(f"    {inpt['txid']} / {inpt['vout']}")

        print("  copy outputs:")
        for outpt in replace_this["vout"]:
            addr = outpt["scriptPubKey"]["addresses"][0]
            outputs[addr] = outpt["value"]
            print(f"    {addr}: {outpt['value']}")

        print("  change fee to 1 DOGE by changing the change output:")
        # find change output (dirty)
        for addr in outputs:
            if outputs[addr] < Decimal("51000.0"):
                outputs[addr] = total_input_value - Decimal("51000.0") - 1
                print(f"    {addr}: {outputs[addr]}")

        print("  create, sign and push new tx:")
        rawtx = self.nodes[0].createrawtransaction(inputs, outputs)
        sigtx = self.nodes[0].signrawtransaction(rawtx)
        replacement = self.nodes[0].sendrawtransaction(sigtx["hex"])
        print(f"    wallet sent {replacement}")

        self.sync_all()

        print("\n[09] The replacement tx0 gets accepted everywhere... (T=T+0)")
        # check all mempools
        for i in range(4):
            mempool = self.nodes[i].getrawmempool()
            assert replacement in mempool
            print(f"  {self.names[i]} has {replacement} in mempool")

        # update time and mine the replacement tx
        for n in self.nodes:
            n.setmocktime(int(time.time()))
        self.nodes[3].generate(1)
        self.sync_all()
        assert not len(self.nodes[0].getrawmempool())
        print("  and gets mined...")

        self.print_wallet_balance()
        print("  that takes care of tx1! wow")

        print("\n[10] We do an oopsie and we accidentally: (T=T+0)")
        print("     send out a new tx1 without replacing the original inputs, and")
        print("     completely forget about tx2")
        newtx2 = self.send_custom_tx(Decimal("52000.0"), Decimal("1.0"))
        self.sync_all()
        # check all mempools
        for i in range(4):
            mempool = self.nodes[i].getrawmempool()
            assert newtx2 in mempool
            print(f"  {self.names[i]} has {newtx2} in mempool")

        # update time and mine the replacement tx
        for n in self.nodes:
            n.setmocktime(int(time.time()))
        self.nodes[3].generate(1)
        self.sync_all()
        assert not len(self.nodes[0].getrawmempool())
        print("  it gets mined...")

        self.print_wallet_balance()
        print("  such confuse!!!")

        # END OF MINER FEE ISSUES
        print("\n==============================================")

        print("\n[11] The miner updates... (T=T+0)")
        self.stop_node(3)
        self.nodes[3] = start_node(3, self.options.tmpdir,
            ["-acceptnonstdtxn=0", "-mempoolexpiry=1"])

        # update time as this took a while
        for n in self.nodes:
            n.setmocktime(int(time.time()))

        # connect back to all nodes
        connect_nodes_bi(self.nodes, 1,3)
        connect_nodes_bi(self.nodes, 2,3)
        connect_nodes_bi(self.nodes, 0,3)

        # mine a block to make sure we all talk to the new miner
        self.nodes[3].generate(1)
        self.sync_all()

        self.print_fee_config()

        print("\n[12] Our wallet sends out cached transactions... (T=T+0)")
        for j in [1,2]:
            self.nodes[0].sendrawtransaction(hex_txs[j])

        # nodes 0, 2 and 3 accept the cached tx
        sync_mempools([self.nodes[0], self.nodes[3]])
        for i in [0,3]:
            mempool = self.nodes[i].getrawmempool()
            for j in [1,2]:
                assert txs[j] in mempool
                print(f"  {self.names[i]} has {txs[j]} in mempool")

        print("\n[13] The cached transactions get mined... (T=T+0)")
        # node 3 mines the tx
        self.nodes[3].generate(1)
        self.sync_all()

        self.print_wallet_balance()

        # check status of all transactions
        txs.append(replacement)
        txs.append(newtx2)

        print("\n  (negative confirmations indicate a replaced transaction)")
        for tx in txs:
            wtx = self.nodes[0].gettransaction(tx)
            print(f"  {wtx['txid']} for {wtx['amount']} has {wtx['confirmations']} conf")

        print("\nHOUSTON, WE HAVE A PROBLEM!")
        print(f"    let's make it {self.recv}'s problem!")
        print(f"    Dear {self.recv}, you owe us 52,000 DOGE. Plz send.")

        print("\n=====THE END=====\n")

    def print_fee_config(self):
        print("  wallet: sends   txs with 0.10000000 DOGE/kb fee")
        for i in range(1,4):
            print(f"  {self.names[i]}: accepts txs with {self.nodes[i].getnetworkinfo()['relayfee']} DOGE/kb fee")

    def print_wallet_balance(self):
        inputs = self.nodes[0].listunspent()
        balance = self.nodes[0].getbalance()
        print(f"  our wallet has {len(inputs)} inputs with a total balance of {balance} DOGE")

    def print_wallet_mempool_size(self):
        mempool = self.nodes[0].getrawmempool()
        print(f"  our wallet node has {len(mempool)} mempool entries")

    def send_custom_tx(self, amount, fee):
        avail = self.nodes[0].listunspent(5)[0]
        change = self.nodes[0].getrawchangeaddress()
        inputs = [ {'txid': avail['txid'], 'vout': avail['vout']} ]
        outputs = { self.recv : amount , change: avail['amount'] - amount - fee }
        rawtx = self.nodes[0].createrawtransaction(inputs, outputs)
        sigtx = self.nodes[0].signrawtransaction(rawtx)
        return self.nodes[0].sendrawtransaction(sigtx["hex"])

if __name__ == '__main__':
    StuckTxDemo().main()
