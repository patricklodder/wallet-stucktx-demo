Stuck TX Demo
==============

Docker container that runs 4 `dogecoind` to demonstrate "the stuck tx problem".

### Scenario

1. A wallet sends out 3 transactions to a recipient of resp 51k, 52k and 53k DOGE.
2. All transactions get stuck because there is no miner that is accepting the fee
3. The first transaction (tx0) gets replaced by respending its inputs
4. The second transaction (tx1) gets replaced without respending inputs
5. The third transaction (tx2) is forgotten
6. When the wallet *(or an attacker!!!)* sends the original tx1 again, the
   recipient gets the amount twice

### Usage

You need an x86 linux pc or vm with `docker` and `git` installed.

```bash
git clone https://github.com/patricklodder/wallet-stucktx-demo.git
cd wallet-stucktx-demo
docker build -t wallet-stucktx-demo:latest .
docker run wallet-stucktx-demo:latest
```

### Example output

```
[00] Setup...  (T=T-2h)
  wallet: sends   txs with 0.10000000 DOGE/kb fee
  relay1: accepts txs with 1.00000000 DOGE/kb fee
  relay2: accepts txs with 0.00100000 DOGE/kb fee
   miner: accepts txs with 1.00000000 DOGE/kb fee

[01] Mining blocks and seeding wallet...  (T=T-2h)
  our wallet has 5 inputs with a total balance of 500000.00000000 DOGE

[02] Sending 3 too low fee transactions... (T-2h)
  tx0: 041166db29f2b683d6d93e80c89f1c21d6ed1784cca1affb1237f80ac35389d7 sending 51000 to n4LRQGEKcyRCXqD2MH3ompyMTJKitxu1WP
  tx1: 2e81e9aeefeb6ca1e0c242bcb29e447ee70e5ae5e106e476d754ea7bb09b1d68 sending 52000 to n4LRQGEKcyRCXqD2MH3ompyMTJKitxu1WP
  tx2: 1a0a798316436d96a5e0ef9fdc5ee563b38da973a7a589730ef7af9f01424acc sending 53000 to n4LRQGEKcyRCXqD2MH3ompyMTJKitxu1WP
  our wallet node has 3 mempool entries
  our wallet has 2 inputs with a total balance of 343999.93220000 DOGE

[03] Syncing mempools... (T=T-2h)
  wallet has 041166db29f2b683d6d93e80c89f1c21d6ed1784cca1affb1237f80ac35389d7 in mempool
  wallet has 2e81e9aeefeb6ca1e0c242bcb29e447ee70e5ae5e106e476d754ea7bb09b1d68 in mempool
  wallet has 1a0a798316436d96a5e0ef9fdc5ee563b38da973a7a589730ef7af9f01424acc in mempool
  relay2 has 041166db29f2b683d6d93e80c89f1c21d6ed1784cca1affb1237f80ac35389d7 in mempool
  relay2 has 2e81e9aeefeb6ca1e0c242bcb29e447ee70e5ae5e106e476d754ea7bb09b1d68 in mempool
  relay2 has 1a0a798316436d96a5e0ef9fdc5ee563b38da973a7a589730ef7af9f01424acc in mempool
  relay1 does not have 041166db29f2b683d6d93e80c89f1c21d6ed1784cca1affb1237f80ac35389d7 in mempool
  relay1 does not have 2e81e9aeefeb6ca1e0c242bcb29e447ee70e5ae5e106e476d754ea7bb09b1d68 in mempool
  relay1 does not have 1a0a798316436d96a5e0ef9fdc5ee563b38da973a7a589730ef7af9f01424acc in mempool
   miner does not have 041166db29f2b683d6d93e80c89f1c21d6ed1784cca1affb1237f80ac35389d7 in mempool
   miner does not have 2e81e9aeefeb6ca1e0c242bcb29e447ee70e5ae5e106e476d754ea7bb09b1d68 in mempool
   miner does not have 1a0a798316436d96a5e0ef9fdc5ee563b38da973a7a589730ef7af9f01424acc in mempool

[04] Mining a block... (T=T-2h)
  wallet still has 041166db29f2b683d6d93e80c89f1c21d6ed1784cca1affb1237f80ac35389d7 in mempool
  wallet still has 2e81e9aeefeb6ca1e0c242bcb29e447ee70e5ae5e106e476d754ea7bb09b1d68 in mempool
  wallet still has 1a0a798316436d96a5e0ef9fdc5ee563b38da973a7a589730ef7af9f01424acc in mempool
  relay2 still has 041166db29f2b683d6d93e80c89f1c21d6ed1784cca1affb1237f80ac35389d7 in mempool
  relay2 still has 2e81e9aeefeb6ca1e0c242bcb29e447ee70e5ae5e106e476d754ea7bb09b1d68 in mempool
  relay2 still has 1a0a798316436d96a5e0ef9fdc5ee563b38da973a7a589730ef7af9f01424acc in mempool
  our wallet has 2 inputs with a total balance of 343999.93220000 DOGE

==============================================

[05] Timewarp back to the future, mempools expire... (T=T+0)
  wallet has 0 transactions in mempool
  relay1 has 0 transactions in mempool
  relay2 has 0 transactions in mempool
   miner has 0 transactions in mempool

[06] Our wallet seems confused now... (T=T+0)
  our wallet has 2 inputs with a total balance of 200000.00000000 DOGE
  very concern!

[07] But the wallet still remembers these transactions... (T=T+0)
  wallet remembers tx 041166db29f2b683d6d93e80c89f1c21d6ed1784cca1affb1237f80ac35389d7 for -51000.00000000
  wallet remembers tx 2e81e9aeefeb6ca1e0c242bcb29e447ee70e5ae5e106e476d754ea7bb09b1d68 for -52000.00000000
  wallet remembers tx 1a0a798316436d96a5e0ef9fdc5ee563b38da973a7a589730ef7af9f01424acc for -53000.00000000

[08] Replace tx0 for 51000 correctly... (T=T+0)
  copy inputs:
    aeaef799f34676b2de572d6de105485147263df68490cfe9232595a3a60f47b6 / 1
  copy outputs:
    mtPvDHF7AqorQiZzrAjnYT4Q1U8eJnKk1K: 48999.97740000
    n4LRQGEKcyRCXqD2MH3ompyMTJKitxu1WP: 51000.00000000
  change fee to 1 DOGE by changing the change output:
    mtPvDHF7AqorQiZzrAjnYT4Q1U8eJnKk1K: 48999.00000000
  create, sign and push new tx:
    wallet sent d7703393f53fce77f859e6ed3b7a8a96eaa3749d372ddce8500be85dadbf1528

[09] The replacement tx0 gets accepted everywhere... (T=T+0)
  wallet has d7703393f53fce77f859e6ed3b7a8a96eaa3749d372ddce8500be85dadbf1528 in mempool
  relay1 has d7703393f53fce77f859e6ed3b7a8a96eaa3749d372ddce8500be85dadbf1528 in mempool
  relay2 has d7703393f53fce77f859e6ed3b7a8a96eaa3749d372ddce8500be85dadbf1528 in mempool
   miner has d7703393f53fce77f859e6ed3b7a8a96eaa3749d372ddce8500be85dadbf1528 in mempool
  and gets mined...
  our wallet has 3 inputs with a total balance of 248999.00000000 DOGE
  that takes care of tx1! wow

[10] We do an oopsie and we accidentally: (T=T+0)
     send out a new tx1 without replacing the original inputs, and
     completely forget about tx2
  wallet has 31cf7f93fcf22ec5d83846c9bec8409d38a491faccd019844e1a5ad6bdf1ca50 in mempool
  relay1 has 31cf7f93fcf22ec5d83846c9bec8409d38a491faccd019844e1a5ad6bdf1ca50 in mempool
  relay2 has 31cf7f93fcf22ec5d83846c9bec8409d38a491faccd019844e1a5ad6bdf1ca50 in mempool
   miner has 31cf7f93fcf22ec5d83846c9bec8409d38a491faccd019844e1a5ad6bdf1ca50 in mempool
  it gets mined...
  our wallet has 3 inputs with a total balance of 196998.00000000 DOGE
  such confuse!!!

==============================================

[11] The miner updates... (T=T+0)
  wallet: sends   txs with 0.10000000 DOGE/kb fee
  relay1: accepts txs with 1.00000000 DOGE/kb fee
  relay2: accepts txs with 0.00100000 DOGE/kb fee
   miner: accepts txs with 0.00100000 DOGE/kb fee

[12] Our wallet sends out cached transactions... (T=T+0)
  wallet has 2e81e9aeefeb6ca1e0c242bcb29e447ee70e5ae5e106e476d754ea7bb09b1d68 in mempool
  wallet has 1a0a798316436d96a5e0ef9fdc5ee563b38da973a7a589730ef7af9f01424acc in mempool
   miner has 2e81e9aeefeb6ca1e0c242bcb29e447ee70e5ae5e106e476d754ea7bb09b1d68 in mempool
   miner has 1a0a798316436d96a5e0ef9fdc5ee563b38da973a7a589730ef7af9f01424acc in mempool

[13] The cached transactions get mined... (T=T+0)
  our wallet has 5 inputs with a total balance of 291997.95480000 DOGE

  (negative confirmations indicate a replaced transaction)
  041166db29f2b683d6d93e80c89f1c21d6ed1784cca1affb1237f80ac35389d7 for -51000.00000000 has -4 conf
  2e81e9aeefeb6ca1e0c242bcb29e447ee70e5ae5e106e476d754ea7bb09b1d68 for -52000.00000000 has 1 conf
  1a0a798316436d96a5e0ef9fdc5ee563b38da973a7a589730ef7af9f01424acc for -53000.00000000 has 1 conf
  d7703393f53fce77f859e6ed3b7a8a96eaa3749d372ddce8500be85dadbf1528 for -51000.00000000 has 4 conf
  31cf7f93fcf22ec5d83846c9bec8409d38a491faccd019844e1a5ad6bdf1ca50 for -52000.00000000 has 3 conf

HOUSTON, WE HAVE A PROBLEM!
    let's make it n4LRQGEKcyRCXqD2MH3ompyMTJKitxu1WP's problem!
    Dear n4LRQGEKcyRCXqD2MH3ompyMTJKitxu1WP, you owe us 52,000 DOGE. Plz send.

=====THE END=====

```
