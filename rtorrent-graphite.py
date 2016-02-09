#!/usr/bin/env python

# Configuration:
# rTorrent XML-RPC URI
xmlrpc_uri = ""

# Graphite
graphite_server = "graphite"
graphite_prefix = ""
graphite_port = 2003

# Graphite dry run (display data instead of pushing to graphite.)
graphite_dryrun = False

# Fetch interval (seconds). Set to False for single shot.
interval = 30


import xmlrpclib
import time
import graphitesend


def get_rtorrent_data(xmlrpc_uri):
    "Get data from rtorrent via XML-RPC"
    rtorrent = xmlrpclib.ServerProxy(xmlrpc_uri)
    d = {}

    # Global down rate
    down_rate = rtorrent.get_down_rate("")
    d["rate.down"] = down_rate

    # Global up rate
    up_rate = rtorrent.get_up_rate("")
    d["rate.up"] = up_rate

    # Global maximum upload rate
    max_upload_rate = rtorrent.get_upload_rate("")
    d["rate.max_up"] = max_upload_rate

    # Global maximum download rate
    max_download_rate = rtorrent.get_download_rate("")
    d["rate.max_down"] = max_download_rate

    # Global maximum memory
    max_memory = rtorrent.get_max_memory_usage("")
    d["memory.max"] = max_memory

    # Memory used
    used_memory = rtorrent.get_memory_usage("")
    d["memory.used"] = used_memory

    # Total number of torrents
    torrent_list = rtorrent.download_list("")
    torrents_total = len(torrent_list)
    d["torrents.total"] = torrents_total

    # XML-RPC MultiCall object for torrent statistics
    mc = xmlrpclib.MultiCall(rtorrent)
    for torrent in torrent_list:
        mc.__getattr__('d.get_complete')(torrent)

    for torrent in torrent_list:
        mc.__getattr__('d.get_bytes_done')(torrent)

    for torrent in torrent_list:
        mc.__getattr__('d.get_left_bytes')(torrent)

    for torrent in torrent_list:
        mc.__getattr__('d.get_peers_complete')(torrent)

    for torrent in torrent_list:
        mc.__getattr__('d.get_peers_connected')(torrent)

    for torrent in torrent_list:
        mc.__getattr__('d.get_peers_accounted')(torrent)

    mc_result = tuple(mc())

    # Number of complete & incomplete torrents
    complete = 0
    for i in range(0, torrents_total):
        if mc_result[i]:
            complete += 1

    d["torrents.complete"] = complete
    d["torrents.incomplete"] = torrents_total - complete

    # Number of completed & left to download bytes
    bytes_done = 0
    for i in range(torrents_total, torrents_total*2):
        if mc_result[i]:
            bytes_done += mc_result[i]

    bytes_remaining = 0
    for i in range(torrents_total*2, torrents_total*3):
        if mc_result[i]:
            bytes_remaining += mc_result[i]

    d["bytes.done"] = bytes_done
    d["bytes.remaining"] = bytes_remaining

    # Peers & Seeds
    seeds = 0
    for i in range(torrents_total*3, torrents_total*4):
        if mc_result[i]:
            seeds += mc_result[i]

    peers_total = 0
    for i in range(torrents_total*4, torrents_total*5):
        if mc_result[i]:
            peers_total += mc_result[i]

    peers_accounted = 0
    for i in range(torrents_total*5, torrents_total*6):
        if mc_result[i]:
            peers_accounted += mc_result[i]

    d["peers.seeds_connected"] = seeds
    d["peers.total_connected"] = peers_total
    d["peers.accounted"] = peers_accounted

    # Print result dict in alphabetical order.
    # for key in sorted(d.iterkeys()):
    #     print "%s: %s" % (key, d[key])

    return d


g = graphitesend.init(prefix=graphite_prefix,
                      dryrun=graphite_dryrun,
                      graphite_server=graphite_server,
                      graphite_port=graphite_port,
                      group="rtorrent")

if interval is False:
    print g.send_dict(get_rtorrent_data(xmlrpc_uri))
else:
    while True:
        print g.send_dict(get_rtorrent_data(xmlrpc_uri))
        time.sleep(interval)
